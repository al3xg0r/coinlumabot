# services.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL
from utils import logger

# Настройка сессии с повторами (Retries)
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

price_cache = TTLCache(maxsize=1000, ttl=600)
id_cache = TTLCache(maxsize=2000, ttl=86400)
image_cache = TTLCache(maxsize=2000, ttl=86400)

class CryptoService:
    @staticmethod
    def get_coin_price(query):
        query = query.lower().strip()
        
        if query in price_cache:
            return price_cache[query]

        try:
            coin_id = CryptoService._resolve_coingecko_id(query)
            if not coin_id:
                return CryptoService._get_from_coincap(query)
            
            # Используем v3 API
            url = f"{COINGECKO_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd,eur,uah,rub'
            }
            
            response = session.get(url, params=params, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                image_url = image_cache.get(query)
                result = {
                    'name': coin_id.capitalize(),
                    'symbol': query.upper(),
                    'image': image_url,
                    'usd': data[coin_id].get('usd', 0),
                    'eur': data[coin_id].get('eur', 0),
                    'uah': data[coin_id].get('uah', 0),
                    'rub': data[coin_id].get('rub', 0)
                }
                price_cache[query] = result
                return result
                
        except Exception as e:
            logger.error(f"CoinGecko API error: {e}")
            return CryptoService._get_from_coincap(query)

    @staticmethod
    def _resolve_coingecko_id(query):
        if query in id_cache:
            return id_cache[query]
            
        url = f"{COINGECKO_URL}/search"
        try:
            response = session.get(url, params={'query': query}, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            found_coin = None
            for coin in data.get('coins', []):
                if coin['symbol'].lower() == query or coin['id'].lower() == query:
                    found_coin = coin
                    break
            
            if not found_coin and data.get('coins'):
                found_coin = data['coins'][0]

            if found_coin:
                c_id = found_coin['id']
                id_cache[query] = c_id
                thumb_url = found_coin.get('thumb', '')
                image_cache[query] = thumb_url.replace('thumb', 'large')
                return c_id
        except Exception as e:
            logger.error(f"Resolve ID error: {e}")
        return None

    @staticmethod
    def _get_from_coincap(query):
        try:
            url = f"{COINCAP_URL}/assets"
            params = {'search': query, 'limit': 1}
            response = session.get(url, params=params, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data['data']:
                coin = data['data'][0]
                usd_price = float(coin['priceUsd'])
                # Приблизительные курсы для резерва
                rates = {'eur': 0.92, 'uah': 41.5, 'rub': 96.0}
                
                result = {
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'image': None,
                    'usd': round(usd_price, 4),
                    'eur': round(usd_price * rates['eur'], 4),
                    'uah': round(usd_price * rates['uah'], 4),
                    'rub': round(usd_price * rates['rub'], 4)
                }
                price_cache[query] = result
                return result
        except Exception as e:
            logger.error(f"CoinCap fallback error: {e}")
        return "error"