# services.py
import requests
from cachetools import TTLCache
from config import COINGECKO_URL, COINCAP_URL
from utils import logger

# Кэш цен (10 минут)
price_cache = TTLCache(maxsize=1000, ttl=600)
# Кэш ID монет (24 часа)
id_cache = TTLCache(maxsize=2000, ttl=86400)
# Кэш картинок (24 часа) — хранит URL логотипов
image_cache = TTLCache(maxsize=2000, ttl=86400)

class CryptoService:
    @staticmethod
    def get_coin_price(query):
        query = query.lower().strip()
        
        # 1. Проверяем кэш цен
        if query in price_cache:
            return price_cache[query]

        # 2. Основной API (CoinGecko)
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
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if coin_id in data:
                # Достаем картинку из кэша (она туда попала при поиске ID)
                image_url = image_cache.get(query)

                result = {
                    'name': coin_id.capitalize(),
                    'symbol': query.upper(),
                    'image': image_url,  # Добавляем ссылку на фото
                    'usd': data[coin_id]['usd'],
                    'eur': data[coin_id]['eur'],
                    'uah': data[coin_id]['uah'],
                    'rub': data[coin_id]['rub']
                }
                price_cache[query] = result
                return result
                
        except Exception as e:
            logger.error(f"CoinGecko API failed: {e}")

        # 3. Запасной API (CoinCap)
        try:
            return CryptoService._get_from_coincap(query)
        except Exception as e:
            logger.error(f"CoinCap API failed: {e}")
            return "error"

    @staticmethod
    def _resolve_coingecko_id(query):
        """Ищет ID и сохраняет картинку"""
        if query in id_cache:
            return id_cache[query]
            
        url = f"{COINGECKO_URL}/search"
        try:
            response = requests.get(url, params={'query': query}, timeout=5)
            data = response.json()
            
            found_coin = None
            
            # Ищем точное совпадение
            for coin in data.get('coins', []):
                if coin['symbol'].lower() == query or coin['id'].lower() == query:
                    found_coin = coin
                    break
            
            # Если нет точного, берем первый
            if not found_coin and data.get('coins'):
                found_coin = data['coins'][0]

            if found_coin:
                c_id = found_coin['id']
                id_cache[query] = c_id
                
                # Обработка картинки: меняем thumb на large для качества
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
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['data']:
            coin = data['data'][0]
            usd_price = float(coin['priceUsd'])
            
            # Хардкод курсов для fallback
            eur_rate = 0.92
            uah_rate = 41.5
            rub_rate = 96.0
            
            result = {
                'name': coin['name'],
                'symbol': coin['symbol'],
                'image': None, # У CoinCap сложно достать картинки без лишних движений
                'usd': round(usd_price, 4),
                'eur': round(usd_price * eur_rate, 4),
                'uah': round(usd_price * uah_rate, 4),
                'rub': round(usd_price * rub_rate, 4)
            }
            price_cache[query] = result
            return result
        return None