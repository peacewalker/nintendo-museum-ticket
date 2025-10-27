#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from dotenv import load_dotenv
from src.monitor import NintendoMuseumMonitor
from utils.logging_setter import setup_logger

# Load environment variables
load_dotenv()

# Logger setup
logger = setup_logger('nintendo_main', 'nintendo_main.log')


def main():
    """Main entry point for Nintendo Museum Monitor"""
    # Get monitor interval from .env (default: 20 seconds)
    monitor_interval = int(os.getenv('MONITOR_INTERVAL', '20'))

    # Get current date
    now = datetime.now()
    year = now.year
    month = now.month

    logger.info("="*50)
    logger.info("Nintendo Museum Ticket Monitor")
    logger.info("="*50)
    logger.info(f"Monitoring: {year}-{month:02d}")
    logger.info(f"Interval: {monitor_interval} seconds")
    logger.info("="*50)

    # Create monitor instance
    monitor = NintendoMuseumMonitor()

    # Start monitoring
    monitor.monitor(year, month, interval=monitor_interval)


if __name__ == "__main__":
    main()
