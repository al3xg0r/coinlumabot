# services.py
import requests
import time
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL
from utils import logger

# Кэш на 1000 элементов, живет 600 секунд (10 минут)
price_cache = TTLCache(maxsize=1000, ttl=600)
# Кэш для поиска ID монет, живет 24 часа
id_cache = TTLCache(maxsize=2000, ttl=86400)

class CryptoService:
    @staticmethod
    def get_coin_price(query):
        query = query.lower().strip()
        
        # 1. Проверяем кэш цен
        if query in price_cache:
            logger.info(f"Returning cached data for {query}")
            return price_cache[query]

        # 2. Основной API (CoinGecko)
        try:
            # Сначала нужно найти ID монеты, если введен тикер (например BTC -> bitcoin)
            coin_id = CryptoService._resolve_coingecko_id(query)
            if not coin_id:
                return None
            
            url = f"{COINGECKO_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd,eur,uah,rub',
                'include_last_updated_at': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if coin_id in data:
                result = {
                    'name': coin_id.capitalize(), # API simple не отдает имя, берем ID
                    'symbol': query.upper(),
                    'usd': data[coin_id]['usd'],
                    'eur': data[coin_id]['eur'],
                    'uah': data[coin_id]['uah'],
                    'rub': data[coin_id]['rub']
                }
                price_cache[query] = result
                return result
                
        except Exception as e:
            logger.error(f"CoinGecko API failed: {e}")
            # Переходим к запасному API

        # 3. Запасной API (CoinCap)
        try:
            return CryptoService._get_from_coincap(query)
        except Exception as e:
            logger.error(f"CoinCap API failed: {e}")
            return "error"

    @staticmethod
    def _resolve_coingecko_id(query):
        """Ищет ID монеты по тикеру или названию через CoinGecko Search"""
        if query in id_cache:
            return id_cache[query]
            
        url = f"{COINGECKO_URL}/search"
        try:
            response = requests.get(url, params={'query': query}, timeout=5)
            data = response.json()
            # Ищем точное совпадение по символу или id
            for coin in data.get('coins', []):
                if coin['symbol'].lower() == query or coin['id'].lower() == query:
                    id_cache[query] = coin['id']
                    return coin['id']
            # Если точного нет, берем первый результат, если он похож
            if data.get('coins'):
                 first = data['coins'][0]['id']
                 id_cache[query] = first
                 return first
        except:
            return query # Пытаемся использовать как есть
        return None

    @staticmethod
    def _get_from_coincap(query):
        # CoinCap поиск
        url = f"{COINCAP_URL}/assets"
        params = {'search': query, 'limit': 1}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['data']:
            coin = data['data'][0]
            # CoinCap отдает только USD. Остальные придется конвертировать примерно или искать API курсов.
            # Для простоты при fallback оставим конвертацию фиктивной или на основе USD
            usd_price = float(coin['priceUsd'])
            
            # Хардкод примерных кросс-курсов для fallback (лучше подключить API валют)
            eur_rate = 0.92
            uah_rate = 41.5
            rub_rate = 96.0
            
            result = {
                'name': coin['name'],
                'symbol': coin['symbol'],
                'usd': round(usd_price, 4),
                'eur': round(usd_price * eur_rate, 4),
                'uah': round(usd_price * uah_rate, 4),
                'rub': round(usd_price * rub_rate, 4)
            }
            price_cache[query] = result
            return result
        return None