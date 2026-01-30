# services.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL, CRYPTOCOMPARE_URL, COINGECKO_API_KEY
from utils import logger

session = requests.Session()
adapter = HTTPAdapter(max_retries=2)
session.mount('https://', adapter)

# Заголовки для CoinGecko теперь включают ключ
CG_HEADERS = {
    'accept': 'application/json',
    'x-cg-demo-api-key': COINGECKO_API_KEY
}

price_cache = TTLCache(maxsize=1000, ttl=600)
image_cache = TTLCache(maxsize=2000, ttl=86400)

class CryptoService:
    @staticmethod
    def get_coin_price(query):
        query = query.upper().strip()
        if query in price_cache:
            return price_cache[query]

        # 1. CoinGecko с API-ключом
        data = CryptoService._get_from_coingecko(query)
        if data and data != "error":
            return data

        # 2. Резерв: CoinCap
        data = CryptoService._get_from_coincap(query)
        if data and data != "error":
            return data

        # 3. Финальный резерв: CryptoCompare
        return CryptoService._get_from_cryptocompare(query)

    @staticmethod
    def _get_from_coingecko(query):
        try:
            # Сначала ищем ID
            search_url = f"{COINGECKO_URL}/search"
            r = session.get(search_url, params={'query': query}, headers=CG_HEADERS, timeout=10)
            if r.status_code == 200:
                coins = r.json().get('coins', [])
                if coins:
                    coin = next((c for c in coins if c['symbol'] == query or c['id'] == query.lower()), coins[0])
                    c_id = coin['id']
                    image_cache[query] = coin.get('large') or coin.get('thumb', '').replace('thumb', 'large')
                    
                    # Получаем цену
                    p_url = f"{COINGECKO_URL}/simple/price"
                    p_params = {'ids': c_id, 'vs_currencies': 'usd,eur,uah,rub'}
                    pr = session.get(p_url, params=p_params, headers=CG_HEADERS, timeout=10)
                    p_data = pr.json()
                    
                    if c_id in p_data:
                        res = {
                            'name': coin['name'], 'symbol': query, 'image': image_cache[query],
                            'usd': p_data[c_id]['usd'], 'eur': p_data[c_id]['eur'],
                            'uah': p_data[c_id]['uah'], 'rub': p_data[c_id]['rub']
                        }
                        price_cache[query] = res
                        return res
        except Exception as e:
            logger.error(f"CG Auth Error: {e}")
        return None

    @staticmethod
    def _get_from_coincap(query):
        try:
            url = f"{COINCAP_URL}/assets"
            r = session.get(url, params={'search': query, 'limit': 1}, timeout=10)
            d = r.json().get('data')
            if d:
                c = d[0]
                p = float(c['priceUsd'])
                res = {
                    'name': c['name'], 'symbol': c['symbol'], 'image': None,
                    'usd': round(p, 2), 'eur': round(p*0.92, 2), 'uah': round(p*41.5, 2), 'rub': round(p*96.0, 2)
                }
                price_cache[query] = res
                return res
        except: return None

    @staticmethod
    def _get_from_cryptocompare(query):
        try:
            params = {'fsym': query, 'tsyms': 'USD,EUR,UAH,RUB'}
            r = session.get(CRYPTOCOMPARE_URL, params=params, timeout=10)
            d = r.json()
            if "USD" in d:
                res = {
                    'name': query, 'symbol': query, 'image': None,
                    'usd': d['USD'], 'eur': d['EUR'], 'uah': d['UAH'], 'rub': d['RUB']
                }
                price_cache[query] = res
                return res
        except: pass
        return "error"