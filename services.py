# services.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL
from utils import logger

session = requests.Session()
retries = Retry(total=2, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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

        # Пытаемся получить через CoinGecko
        try:
            coin_id = CryptoService._resolve_coingecko_id(query)
            if coin_id:
                url = f"{COINGECKO_URL}/simple/price"
                params = {'ids': coin_id, 'vs_currencies': 'usd,eur,uah,rub'}
                resp = session.get(url, params=params, headers=HEADERS, timeout=10)
                
                if resp.status_code == 429:
                    logger.warning("CoinGecko Rate Limit hit (429). Switching to CoinCap.")
                else:
                    resp.raise_for_status()
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
        except Exception as e:
            logger.error(f"CoinGecko primary failed: {e}")

        # Если CoinGecko не ответил или лимит — идем в CoinCap
        return CryptoService._get_from_coincap(query)

    @staticmethod
    def _resolve_coingecko_id(query):
        if query in id_cache: return id_cache[query]
        try:
            url = f"{COINGECKO_URL}/search"
            resp = session.get(url, params={'query': query}, headers=HEADERS, timeout=5)
            if resp.status_code == 429: return None
            data = resp.json()
            found = next((c for c in data.get('coins', []) if c['symbol'].lower() == query or c['id'].lower() == query), None)
            if not found and data.get('coins'): found = data['coins'][0]
            if found:
                id_cache[query] = found['id']
                image_cache[query] = found.get('thumb', '').replace('thumb', 'large')
                return found['id']
        except: pass
        return None

    @staticmethod
    def _get_from_coincap(query):
        try:
            url = f"{COINCAP_URL}/assets"
            # Поиск по тикеру
            resp = session.get(url, params={'search': query, 'limit': 1}, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data['data']:
                c = data['data'][0]
                p = float(c['priceUsd'])
                # Статичные кросс-курсы (т.к. CoinCap только USD)
                res = {
                    'name': c['name'], 'symbol': c['symbol'], 'image': None,
                    'usd': round(p, 2) if p > 1 else round(p, 6),
                    'eur': round(p*0.92, 2) if p > 1 else round(p*0.92, 6), 
                    'uah': round(p*41.5, 2), 'rub': round(p*96.0, 2)
                }
                price_cache[query] = res
                return res
        except Exception as e:
            logger.error(f"CoinCap fallback failed: {e}")
        return "error"