# services.py
import requests
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL
from utils import logger

# Добавляем заголовки, чтобы имитировать браузер
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
                return None
            
            url = f"{COINGECKO_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd,eur,uah,rub',
                'include_last_updated_at': 'true'
            }
            # ДОБАВЛЕНЫ headers=HEADERS
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = response.json()
            
            if coin_id in data:
                image_url = image_cache.get(query)
                result = {
                    'name': coin_id.capitalize(),
                    'symbol': query.upper(),
                    'image': image_url,
                    'usd': data[coin_id]['usd'],
                    'eur': data[coin_id]['eur'],
                    'uah': data[coin_id]['uah'],
                    'rub': data[coin_id]['rub']
                }
                price_cache[query] = result
                return result
                
        except Exception as e:
            logger.error(f"CoinGecko API failed: {e}")

        try:
            return CryptoService._get_from_coincap(query)
        except Exception as e:
            logger.error(f"CoinCap API failed: {e}")
            return "error"

    @staticmethod
    def _resolve_coingecko_id(query):
        if query in id_cache:
            return id_cache[query]
            
        url = f"{COINGECKO_URL}/search"
        try:
            # ДОБАВЛЕНЫ headers=HEADERS
            response = requests.get(url, params={'query': query}, headers=HEADERS, timeout=5)
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
                large_url = thumb_url.replace('thumb', 'large')
                image_cache[query] = large_url
                return c_id
        except:
            return query 
        return None

    @staticmethod
    def _get_from_coincap(query):
        url = f"{COINCAP_URL}/assets"
        params = {'search': query, 'limit': 1}
        # ДОБАВЛЕНЫ headers=HEADERS
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = response.json()
        
        if data['data']:
            coin = data['data'][0]
            usd_price = float(coin['priceUsd'])
            eur_rate, uah_rate, rub_rate = 0.92, 41.5, 96.0
            
            result = {
                'name': coin['name'],
                'symbol': coin['symbol'],
                'image': None,
                'usd': round(usd_price, 4),
                'eur': round(usd_price * eur_rate, 4),
                'uah': round(usd_price * uah_rate, 4),
                'rub': round(usd_price * rub_rate, 4)
            }
            price_cache[query] = result
            return result
        return None