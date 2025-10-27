import requests, os
from dotenv import load_dotenv

load_dotenv()

API_KEY_WEBSHARE = os.getenv('API_KEY_WEBSHARE', '')
USE_WEBSHARE = os.getenv('USE_WEBSHARE', 'False').lower() == 'true'

def fetch_proxies(api_url, token):
    headers = {
        "Authorization": f"Token {token}"
    }

    proxies = []
    try:
        while True:
            try:
                response = requests.get(api_url, headers=headers, timeout=(5,5))
                if response.status_code == 200:break
            except:
                pass
        if response.status_code == 200:
            data = response.json()
            for result in data.get("results", []):
                ip = result["proxy_address"]
                port = result["port"]
                username = result["username"]
                password = result["password"]
                # Create IP:Port format
                proxies.append(f"{ip}:{port}:{username}:{password}")
        else:
            print(f"Error fetching proxy data: {response.status_code}")
    except Exception as e:
        print(f"Error fetching proxy data: {e}")

    return [{}] if proxies == [] else proxies

def load_proxies_all(proxies):
    proxies_list = []
    for proxy in proxies:
        proxy_data = proxy.strip().split(':')
        if len(proxy_data) >= 2:
            ip = proxy_data[0]
            port = proxy_data[1]
            username = proxy_data[2]
            password = proxy_data[3]
            proxy = {
                'https': f'http://{username}:{password}@{ip}:{port}'
            }
            proxies_list.append(proxy)
    
    return proxies_list

def load_proxies():
    if USE_WEBSHARE:
        api_url = "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
        proxies = fetch_proxies(api_url, API_KEY_WEBSHARE)
        # Convert proxy data to correct format
        loaded_proxies = load_proxies_all(proxies)
        print(f"Loaded proxies: {len(loaded_proxies)} with webshare")
        return loaded_proxies if loaded_proxies else [{}]
    else:
        # Check if file exists
        filename = "proxies.txt"
        # Ensure path is relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script folder
        file_path = os.path.join(script_dir, filename)
        proxies_list = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    proxy_data = line.strip().split(':')
                    if len(proxy_data) >= 2:
                        ip = proxy_data[0]
                        port = proxy_data[1]
                        username = proxy_data[2]
                        password = proxy_data[3]
                        proxy = {
                            'https': f'http://{username}:{password}@{ip}:{port}'
                        }
                        proxies_list.append(proxy)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return [{}]
        except Exception as e:
            print(f"An error occurred: {e}")
            return [{}]
        print(f"Loaded proxies: {len(proxies_list)} with file")
        return proxies_list if proxies_list else [{}]
    
proxies = load_proxies()

if __name__ == '__main__':
    loaded_proxies = load_proxies()
    print(loaded_proxies)