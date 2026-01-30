# services.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL
from utils import logger

# Упрощенная сессия без агрессивных повторов
session = requests.Session()
adapter = HTTPAdapter(max_retries=1)
session.mount('https://', adapter)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': 'application/json',
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

        # 1. Пробуем CoinGecko
        try:
            coin_id = CryptoService._resolve_coingecko_id(query)
            if coin_id:
                url = f"{COINGECKO_URL}/simple/price"
                params = {'ids': coin_id, 'vs_currencies': 'usd,eur,uah,rub'}
                resp = session.get(url, params=params, headers=HEADERS, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    if coin_id in data:
                        res = {
                            'name': coin_id.capitalize(),
                            'symbol': query.upper(),
                            'image': image_cache.get(query),
                            'usd': data[coin_id].get('usd', 0),
                            'eur': data[coin_id].get('eur', 0),
                            'uah': data[coin_id].get('uah', 0),
                            'rub': data[coin_id].get('rub', 0)
                        }
                        price_cache[query] = res
                        return res
                elif resp.status_code == 429:
                    logger.warning(f"CoinGecko 429 for {query}")
        except Exception as e:
            logger.error(f"CG Error: {e}")

        # 2. Если CG не сработал, пробуем CoinCap
        return CryptoService._get_from_coincap(query)

    @staticmethod
    def _resolve_coingecko_id(query):
        if query in id_cache: return id_cache[query]
        try:
            url = f"{COINGECKO_URL}/search"
            resp = session.get(url, params={'query': query}, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                coins = data.get('coins', [])
                if not coins: return None
                
                found = next((c for c in coins if c['symbol'].lower() == query or c['id'].lower() == query), coins[0])
                id_cache[query] = found['id']
                image_cache[query] = found.get('thumb', '').replace('thumb', 'large')
                return found['id']
        except: pass
        return None

    @staticmethod
    def _get_from_coincap(query):
        try:
            # Напрямую запрашиваем конкретный ассет по тикеру
            url = f"{COINCAP_URL}/assets"
            params = {'search': query, 'limit': 1}
            resp = session.get(url, params=params, headers=HEADERS, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data'):
                    c = data['data'][0]
                    p = float(c['priceUsd'])
                    res = {
                        'name': c['name'], 'symbol': c['symbol'], 'image': None,
                        'usd': round(p, 2) if p > 1 else round(p, 6),
                        'eur': round(p*0.92, 2) if p > 1 else round(p*0.92, 6),
                        'uah': round(p*41.5, 2), 'rub': round(p*96.0, 2)
                    }
                    price_cache[query] = res
                    return res
            logger.error(f"CoinCap returned {resp.status_code}")
        except Exception as e:
            logger.error(f"CoinCap final fail: {e}")
        return "error"