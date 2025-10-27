#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from typing import Dict, Any, List, Optional
from discord_webhook import DiscordWebhook, DiscordEmbed
from utils.logging_setter import setup_logger
# Setup logger
logger = setup_logger('discord_webhook', 'discord_webhook.log')

class ImmoweltDiscordWebhook:
    """
    Class for sending property details to a Discord webhook
    using the external discord-webhook library.
    """

    def __init__(self, webhook_url: str = None):
        """
        Initializes the Discord webhook with the provided URL.

        Args:
            webhook_url (str, optional): Discord webhook URL.
                If not provided, attempts to load from environment variable.
        """
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')

        if not self.webhook_url:
            logger.warning("No Discord webhook URL provided or found in environment variables.")
    
    def send_property(self, property_data: Dict[str, Any]) -> bool:
        """
        Sends a property listing to the Discord webhook.

        Args:
            property_data (Dict[str, Any]): Property data with at least URL, title, and address

        Returns:
            bool: True if sending was successful, otherwise False
        """
        if not self.webhook_url:
            logger.error("Discord webhook URL not configured.")
            return False

        try:
            # Extract property data
            url = property_data.get("url", "")
            title = self._extract_title(property_data)
            address = self._extract_address(property_data)
            price = self._extract_price(property_data)

            # Extract additional provider information
            provider_info = self._extract_provider_info(property_data)

            # Determine image source (if available)
            image_url = self._extract_image_url(property_data)
            logo_url = self._extract_logo_url(property_data)


            # Create Discord webhook object
            webhook = DiscordWebhook(url=self.webhook_url)

            # Create embed object for webhook
            # Discord title limit is 256 characters
            embed_title = (title or "Property Listing")[:256]
            # Discord description limit is 4096 characters
            embed_description = (address or "")[:4096]

            embed = DiscordEmbed(
                title=embed_title,
                description=embed_description,
                color="03b2f8"  # Blue
            )

            # Set property listing URL
            if url and url.startswith("http"):
                embed.set_url(url)

            # Add image if available
            #if image_url:
            #    embed.set_image(url=image_url)

            # Add logo as thumbnail if available
            if logo_url and logo_url.startswith("http"):
                embed.set_thumbnail(url=logo_url)
            elif image_url and image_url.startswith("http"):
                embed.set_thumbnail(url=image_url)

            # Set footer
            embed.set_footer(text="by Aimani.de", icon_url="https://aimani.de/logo.png")

            # Set timestamp
            embed.set_timestamp()

            # Add provider information as field
            # Discord field value limit is 1024 characters
            if provider_info:
                embed.add_embed_field(name="Provider", value=provider_info[:1024], inline=False)

            # Add price as field
            if price:
                embed.add_embed_field(name="Price", value=price[:1024])

            # Add additional details as fields
            room_info = self._extract_room_info(property_data)
            if room_info:
                embed.add_embed_field(name="Rooms", value=room_info[:1024])

            area_info = self._extract_area_info(property_data)
            if area_info:
                embed.add_embed_field(name="Living Area", value=area_info[:1024])

            plot_info = self._extract_plot_info(property_data)
            if plot_info:
                embed.add_embed_field(name="Plot", value=plot_info[:1024])

            # Add embed object to webhook
            webhook.add_embed(embed)

            # Debug: Log embed data
            logger.debug(f"Embed Title: {embed.title}")
            logger.debug(f"Embed Description: {embed.description}")
            logger.debug(f"Embed URL: {embed.url}")
            logger.debug(f"Embed Fields: {len(embed.fields) if hasattr(embed, 'fields') else 'No fields'}")

            # Send webhook
            response = webhook.execute()

            # Check if webhook was executed successfully
            if response.status_code in [200, 204]:
                logger.info(f"Property listing successfully sent to Discord: {title}")
                return True
            else:
                logger.error(f"Error sending to Discord: {response.status_code} - {response.text}")
                logger.error(f"Embed details - Title: {embed.title}, URL: {embed.url}")
                return False

        except Exception as e:
            logger.error(f"Error sending property listing to Discord: {str(e)}")
            return False
    
    def _extract_title(self, property_data: Dict[str, Any]) -> str:
        """Extracts title from property data (supports old and new API formats)."""
        # New Mobile API Format
        mobile_title = property_data.get("title")
        if mobile_title:
            # Extend with Broker Company Name if available
            broker = property_data.get("broker", {})
            company_name = broker.get("companyName", "")
            if company_name:
                return f"{company_name} - {mobile_title}"
            return mobile_title

        # Old API Format (Fallback)
        # Extract company name
        company_name = ""
        provider = property_data.get("provider", {})
        if provider and isinstance(provider, dict):
            intermediary_card = provider.get("intermediaryCard", {})
            if intermediary_card and isinstance(intermediary_card, dict):
                company_name = intermediary_card.get("title", "")
        
        # Try from hardFacts->title
        base_title = ""
        hard_facts = property_data.get("hardFacts", {})
        if hard_facts and isinstance(hard_facts, dict):
            base_title = hard_facts.get("title", "")

        # Alternative: From mainDescription->headline
        if not base_title:
            main_description = property_data.get("mainDescription", {})
            if main_description and isinstance(main_description, dict):
                base_title = main_description.get("headline", "")

        # Default fallback
        if not base_title:
            base_title = property_data.get("title", "Property Listing")

        # Combine company name with title
        if company_name:
            return f"{company_name} - {base_title}"
        else:
            return base_title
    
    def _extract_price(self, property_data: Dict[str, Any]) -> str:
        """Extracts price from property data (supports old and new API formats)."""
        # New Mobile API Format: primaryPrice
        primary_price = property_data.get("primaryPrice", {})
        if primary_price and isinstance(primary_price, dict):
            value = primary_price.get("amountMin") or primary_price.get("value")
            currency = primary_price.get("currency", "€")
            if value:
                # Format number with thousands separator
                formatted_value = f"{int(value):,}".replace(",", ".")
                return f"{formatted_value} {currency}"
        
        # Old API Format (Fallback)
        # Try from hardFacts->price->value
        hard_facts = property_data.get("hardFacts", {})
        if hard_facts and isinstance(hard_facts, dict):
            price_data = hard_facts.get("price", {})
            if price_data and isinstance(price_data, dict):
                price_value = price_data.get("value", "")
                if price_value:
                    return price_value

        # Alternative: From price->value
        price_data = property_data.get("price", {})
        if isinstance(price_data, dict):
            value = price_data.get("value")
            currency = price_data.get("currency", "€")
            if value:
                return f"{value} {currency}"
                
        return ""
    
    def _extract_address(self, property_data: Dict[str, Any]) -> str:
        """Extracts the address from property data (supports old and new API formats)."""
        # New Mobile API Format: place
        place = property_data.get("place", {})
        if place and isinstance(place, dict):
            city = place.get("city", "")
            district = place.get("district", "")
            zip_code = place.get("postcode", "") or place.get("zipCode", "")
            street = place.get("street", "")
            
            address_parts = []
            if street:
                address_parts.append(street)
            if district and district != city:
                address_parts.append(district)
            if city:
                address_parts.append(city)
            if zip_code:
                address_parts.append(zip_code)
            
            if address_parts:
                return ", ".join(address_parts)
        
        # Old API Format (Fallback)
        # Prioritize provider->address
        provider = property_data.get("provider", {})
        if provider and isinstance(provider, dict):
            address_data = provider.get("address", "")
            if address_data:
                if isinstance(address_data, str):
                    return address_data
                elif isinstance(address_data, dict):
                    city = address_data.get("city", "")
                    district = address_data.get("district", "")
                    zip_code = address_data.get("zipCode", "")
                    street = address_data.get("street", "")

                    address_parts = []
                    if street:
                        address_parts.append(street)
                    if district and district != city:
                        address_parts.append(district)
                    if city:
                        address_parts.append(city)
                    if zip_code:
                        address_parts.append(zip_code)

                    address = ", ".join(address_parts)
                    # Add provider information
                    company = provider.get("intermediaryCard", {}).get("title", "")
                    if company:
                        return f"{company}\n{address}"
                    return address

        # Alternative: From location->address
        location = property_data.get("location", {})
        if location and isinstance(location, dict):
            address_data = location.get("address", {})
            if address_data and isinstance(address_data, dict):
                city = address_data.get("city", "")
                district = address_data.get("district", "")
                zip_code = address_data.get("zipCode", "")
                
                address_parts = []
                if district and district != city:
                    address_parts.append(district)
                if city:
                    address_parts.append(city)
                if zip_code:
                    address_parts.append(zip_code)
                    
                return ", ".join(address_parts)
                    
        return ""
    
    def _extract_room_info(self, property_data: Dict[str, Any]) -> str:
        """Extracts the number of rooms from property data."""
        # New Mobile API Format: roomsMin/roomsMax
        rooms_min = property_data.get("roomsMin")
        rooms_max = property_data.get("roomsMax")
        if rooms_min is not None:
            if rooms_max and rooms_max != rooms_min:
                return f"{rooms_min}-{rooms_max} rooms"
            else:
                return f"{rooms_min} rooms"

        # Try from hardFacts->facts (old API)
        hard_facts = property_data.get("hardFacts", {})
        if hard_facts and isinstance(hard_facts, dict):
            facts = hard_facts.get("facts", [])
            if facts and isinstance(facts, list):
                for fact in facts:
                    if fact.get("type") == "numberOfRooms":
                        return fact.get("value", "")

        # Alternative: From rawData->nbroom
        raw_data = property_data.get("rawData", {})
        if raw_data and isinstance(raw_data, dict):
            rooms = raw_data.get("nbroom")
            if rooms:
                return f"{rooms} rooms"

        # Further alternative
        return property_data.get("rooms", "")
    
    def _extract_area_info(self, property_data: Dict[str, Any]) -> str:
        """Extracts the living area from property data."""
        # New Mobile API Format: primaryArea or areas with LIVING_AREA type
        primary_area = property_data.get("primaryArea", {})
        if primary_area and isinstance(primary_area, dict):
            if primary_area.get("type") == "LIVING_AREA":
                size_min = primary_area.get("sizeMin")
                size_max = primary_area.get("sizeMax")
                if size_min is not None:
                    if size_max and size_max != size_min:
                        return f"{size_min}-{size_max} m²"
                    else:
                        return f"{size_min} m²"

        # Alternative: From areas Array
        areas = property_data.get("areas", [])
        if areas and isinstance(areas, list):
            for area in areas:
                if area.get("type") == "LIVING_AREA":
                    size_min = area.get("sizeMin")
                    size_max = area.get("sizeMax")
                    if size_min is not None:
                        if size_max and size_max != size_min:
                            return f"{size_min}-{size_max} m²"
                        else:
                            return f"{size_min} m²"

        # Try from hardFacts->facts (old API)
        hard_facts = property_data.get("hardFacts", {})
        if hard_facts and isinstance(hard_facts, dict):
            facts = hard_facts.get("facts", [])
            if facts and isinstance(facts, list):
                for fact in facts:
                    if fact.get("type") == "livingSpace":
                        return fact.get("value", "")

        # Alternative: From rawData->surface->main
        raw_data = property_data.get("rawData", {})
        if raw_data and isinstance(raw_data, dict):
            surface = raw_data.get("surface", {})
            if surface and isinstance(surface, dict):
                main_area = surface.get("main")
                if main_area:
                    return f"{main_area} m²"

        # Further alternative
        living_area = property_data.get("livingArea")
        if living_area:
            return f"{living_area} m²"
            
        return ""
    
    def _extract_plot_info(self, property_data: Dict[str, Any]) -> str:
        """Extracts the plot area from property data."""
        # New Mobile API Format: areas with PLOT_AREA type
        areas = property_data.get("areas", [])
        if areas and isinstance(areas, list):
            for area in areas:
                if area.get("type") == "PLOT_AREA":
                    size_min = area.get("sizeMin")
                    size_max = area.get("sizeMax")
                    if size_min is not None:
                        if size_max and size_max != size_min:
                            return f"{size_min}-{size_max} m² plot"
                        else:
                            return f"{size_min} m² plot"

        # Try from hardFacts->facts (old API)
        hard_facts = property_data.get("hardFacts", {})
        if hard_facts and isinstance(hard_facts, dict):
            facts = hard_facts.get("facts", [])
            if facts and isinstance(facts, list):
                for fact in facts:
                    if fact.get("type") == "plotSpace":
                        return fact.get("value", "")

        # Alternative: From rawData->surface->plot
        raw_data = property_data.get("rawData", {})
        if raw_data and isinstance(raw_data, dict):
            surface = raw_data.get("surface", {})
            if surface and isinstance(surface, dict):
                plot_area = surface.get("plot")
                if plot_area:
                    return f"{plot_area} m²"
            
        return ""
    
    def _extract_image_url(self, property_data: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the URL of the first image from property data (supports old and new API formats).
        """
        try:
            # New Mobile API Format: pictures with imageUri
            pictures = property_data.get("pictures", [])
            if pictures and isinstance(pictures, list) and len(pictures) > 0:
                first_picture = pictures[0]
                if first_picture and isinstance(first_picture, dict):
                    image_uri = first_picture.get("imageUri")
                    if image_uri:
                        return image_uri
                    # Fallback to url
                    return first_picture.get("url", "")

            # Old API Format (Fallback)
            # Try to extract the first image from gallery->images
            gallery = property_data.get("gallery", {})
            if gallery and isinstance(gallery, dict):
                images = gallery.get("images", [])
                if images and isinstance(images, list) and len(images) > 0:
                    first_image = images[0]
                    if first_image and isinstance(first_image, dict):
                        return first_image.get("url", "")

            # Alternative: Try to extract the first image from media
            media = property_data.get("media", [])
            if media and isinstance(media, list):
                for item in media:
                    if item.get("type") == "IMAGE" and item.get("url"):
                        return item.get("url")

            # Last alternative: Check for a possible title picture
            title_picture = property_data.get("titlePicture", {})
            if title_picture and isinstance(title_picture, dict):
                return title_picture.get("url", "")

            return None

        except Exception as e:
            logger.error(f"Error extracting image URL: {str(e)}")
            return None
    
    def _extract_logo_url(self, property_data: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the company logo URL from property data (supports old and new API formats).
        """
        try:
            # New Mobile API Format: broker->logoUriHttps
            broker = property_data.get("broker", {})
            if broker and isinstance(broker, dict):
                logo_uri_https = broker.get("logoUriHttps", "")
                if logo_uri_https and logo_uri_https != "https:":
                    return logo_uri_https

                # Fallback to logoUri
                logo_uri = broker.get("logoUri", "")
                if logo_uri and logo_uri != "https:":
                    # If the URL doesn't start with http, add the protocol
                    if logo_uri.startswith("//"):
                        return "https:" + logo_uri
                    return logo_uri

            # Old API Format (Fallback)
            # Try to extract logo from provider->intermediaryCard->logoUrl
            provider = property_data.get("provider", {})
            if provider and isinstance(provider, dict):
                intermediary_card = provider.get("intermediaryCard", {})
                if intermediary_card and isinstance(intermediary_card, dict):
                    logo_url = intermediary_card.get("logoUrl", "")
                    if logo_url:
                        # If the URL doesn't start with http, add the protocol
                        if logo_url.startswith("//"):
                            logo_url = "https:" + logo_url
                        return logo_url

            return None

        except Exception as e:
            logger.error(f"Error extracting logo URL: {str(e)}")
            return None
    
    def _extract_provider_info(self, property_data: Dict[str, Any]) -> str:
        """Extracts provider information from property data (supports old and new API formats)."""
        # New Mobile API Format: broker
        broker = property_data.get("broker", {})
        if broker and isinstance(broker, dict):
            company = broker.get("companyName", "")
            online_id = property_data.get("onlineId", "")
            
            info_parts = []
            if company:
                info_parts.append(company)
            if online_id:
                info_parts.append(f"ID: {online_id}")
                
            return "\n".join(info_parts)

        # Old API Format (Fallback)
        provider = property_data.get("provider", {})
        if provider and isinstance(provider, dict):
            # Company name
            company = ""
            intermediary_card = provider.get("intermediaryCard", {})
            if intermediary_card and isinstance(intermediary_card, dict):
                company = intermediary_card.get("title", "")

            # Phone numbers
            phone_numbers = provider.get("phoneNumbers", [])
            phone_str = ", ".join(phone_numbers) if phone_numbers else ""

            # Website
            website = provider.get("website", "")

            # Compile information
            info_parts = []
            if company:
                info_parts.append(company)
            if phone_str:
                info_parts.append(f"Tel: {phone_str}")
            if website:
                info_parts.append(website)
                
            return "\n".join(info_parts)
        
        return ""
    
    def send_properties(self, properties: List[Dict[str, Any]]) -> int:
        """
        Sends multiple property listings to the Discord webhook.

        Args:
            properties (List[Dict[str, Any]]): List of property data

        Returns:
            int: Number of successfully sent listings
        """
        if not properties:
            logger.warning("No properties provided to send.")
            return 0

        success_count = 0

        for prop in properties:
            if self.send_property(prop):
                success_count += 1

        logger.info(f"{success_count} of {len(properties)} properties successfully sent to Discord.")
        return success_count

def format_property_for_discord(property_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats property data for the Discord webhook.

    Args:
        property_data (Dict[str, Any]): The original property data

    Returns:
        Dict[str, Any]: The formatted data
    """
    # Simply return the original object, as we now do the extraction in the class methods
    return property_data

# Example usage code
if __name__ == "__main__":
    # Webhook URL from environment variable or specify directly
    import sys, json
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import DISCORD_WEBHOOK_URL
    webhook_url = DISCORD_WEBHOOK_URL

    # Create webhook client
    discord_client = ImmoweltDiscordWebhook(webhook_url)

    # Example property
    property_example = {
        "url": "https://www.immowelt.de/expose/example",
        "hardFacts": {
            "title": "Townhouse for Sale",
            "price": {
                "value": "589.900 €"
            },
            "facts": [
                {
                    "type": "numberOfRooms",
                    "value": "5.5 rooms"
                },
                {
                    "type": "livingSpace",
                    "value": "120 m²"
                },
                {
                    "type": "plotSpace",
                    "value": "377 m² plot"
                }
            ]
        },
        "location": {
            "address": {
                "city": "Leingarten",
                "district": "Großgartach",
                "zipCode": "74211"
            }
        },
        "gallery": {
            "images": [
                {
                    "url": "https://mms.immowelt.de/b/f/2/4/bf241fd6-4cbc-4e03-afd0-052e6ee472d7.jpg"
                }
            ]
        },
        "provider": {
            "intermediaryCard": {
                "logoUrl": "//filestore.immowelt.de/logo/left_4dbf90b538704093a206bf66ab7a5616.jpg",
                "title": "Werner Wohnbau GmbH &Co.KG"
            },
            "publisherType": "PARTNER"
        }
    }
    print("Starting Discord webhook")
    print("Sending webhook to: ", webhook_url)
    with open("data/details.json", "r") as f:
        property_example = json.load(f)

    if isinstance(property_example, list):
        properties = property_example
    else:
        properties = property_example.get("classifieds", [])
    # Send
    success = discord_client.send_property(properties[1])

    if success:
        print("Property listing successfully sent to Discord!")
    else:
        print("Error sending property listing to Discord.")
