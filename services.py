# services.py
import requests
import matplotlib
import matplotlib.pyplot as plt
import io
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cachetools import TTLCache
from config import (
    COINGECKO_URL, COINCAP_URL, CRYPTOCOMPARE_URL, 
    COINMARKETCAP_URL, COINGECKO_API_KEY, COINMARKETCAP_API_KEY
)
from utils import logger

# Настройка Matplotlib для работы на сервере без экрана
matplotlib.use('Agg')

session = requests.Session()
adapter = HTTPAdapter(max_retries=2)
session.mount('https://', adapter)

CG_HEADERS = {
    'accept': 'application/json',
    'x-cg-demo-api-key': COINGECKO_API_KEY
}

CMC_HEADERS = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
}

# Кэш
chart_cache = TTLCache(maxsize=500, ttl=600)
price_cache = TTLCache(maxsize=1000, ttl=600)
image_cache = TTLCache(maxsize=2000, ttl=86400)
id_cache = TTLCache(maxsize=2000, ttl=86400)
top10_cache = TTLCache(maxsize=1, ttl=300)

class CryptoService:
    @staticmethod
    def get_coin_price(query):
        query = query.upper().strip()
        if query in price_cache:
            return price_cache[query]

        # 1. CoinGecko
        data = CryptoService._get_from_coingecko(query)
        if data: return data

        # 2. CoinMarketCap
        data = CryptoService._get_from_coinmarketcap(query)
        if data: return data

        # 3. CoinCap
        data = CryptoService._get_from_coincap(query)
        if data: return data

        # 4. CryptoCompare
        return CryptoService._get_from_cryptocompare(query)

    @staticmethod
    def get_chart(coin_id):
        """Генерирует график за 24 часа (Только CoinGecko)"""
        if not coin_id: return None

        if coin_id in chart_cache:
            chart_cache[coin_id].seek(0)
            return chart_cache[coin_id]

        try:
            url = f"{COINGECKO_URL}/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': '1'}
            resp = session.get(url, params=params, headers=CG_HEADERS, timeout=10)
            
            if resp.status_code != 200:
                return None

            data = resp.json().get('prices', [])
            if not data: return None

            times = [datetime.fromtimestamp(x[0]/1000) for x in data]
            prices = [x[1] for x in data]

            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 5))
            
            color = '#00ff00' if prices[-1] >= prices[0] else '#ff0055'
            ax.plot(times, prices, color=color, linewidth=2)
            ax.fill_between(times, prices, color=color, alpha=0.1)

            ax.set_title(f"{coin_id.upper()} Price (24h)", fontsize=14, color='white')
            ax.grid(True, linestyle='--', alpha=0.2)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#444')
            ax.spines['left'].set_color('#444')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            plt.close(fig)

            chart_cache[coin_id] = buf
            return buf
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None

    @staticmethod
    def get_top_10():
        """Возвращает список топ-10 монет с CoinMarketCap (более стабильно для серверов)"""
        if 'top10' in top10_cache:
            return top10_cache['top10']
        
        try:
            url = f"{COINMARKETCAP_URL}/cryptocurrency/listings/latest"
            params = {
                'start': '1',
                'limit': '10',
                'convert': 'USD'
            }
            resp = session.get(url, params=params, headers=CMC_HEADERS, timeout=10)
            
            if resp.status_code == 200:
                raw_data = resp.json().get('data', [])
                clean_data = []
                
                # Приводим формат CMC к нашему общему виду
                for item in raw_data:
                    quote = item['quote']['USD']
                    clean_data.append({
                        'symbol': item['symbol'],
                        'current_price': round(quote['price'], 2),
                        'price_change_percentage_24h': quote['percent_change_24h']
                    })
                
                top10_cache['top10'] = clean_data
                return clean_data
        except Exception as e:
            logger.error(f"Top 10 fetch error: {e}")
        return None

    # --- Приватные методы получения цен ---
    
    @staticmethod
    def _get_from_coingecko(query):
        try:
            if query in id_cache:
                c_id = id_cache[query]
            else:
                search_url = f"{COINGECKO_URL}/search"
                r = session.get(search_url, params={'query': query}, headers=CG_HEADERS, timeout=5)
                if r.status_code != 200: return None
                coins = r.json().get('coins', [])
                if not coins: return None
                coin = next((c for c in coins if c['symbol'] == query or c['id'] == query.lower()), coins[0])
                c_id = coin['id']
                id_cache[query] = c_id
                image_cache[query] = coin.get('large') or coin.get('thumb', '').replace('thumb', 'large')

            p_url = f"{COINGECKO_URL}/simple/price"
            p_params = {'ids': c_id, 'vs_currencies': 'usd,eur,uah,rub', 'include_24hr_change': 'true'}
            pr = session.get(p_url, params=p_params, headers=CG_HEADERS, timeout=10)
            p_data = pr.json()
            
            if c_id in p_data:
                d = p_data[c_id]
                res = {
                    'id': c_id,
                    'name': c_id.capitalize(), 'symbol': query, 
                    'image': image_cache.get(query),
                    'usd': d['usd'], 'eur': d['eur'], 'uah': d['uah'], 'rub': d['rub'],
                    'change_24h': d.get('usd_24h_change', 0)
                }
                price_cache[query] = res
                return res
        except Exception as e:
            logger.error(f"CG Error: {e}")
        return None

    @staticmethod
    def _get_from_coinmarketcap(query):
        try:
            url = f"{COINMARKETCAP_URL}/cryptocurrency/quotes/latest"
            params = {'symbol': query, 'convert': 'USD'}
            r = session.get(url, headers=CMC_HEADERS, params=params, timeout=10)
            if r.status_code != 200: return None
            
            data = r.json().get('data', {})
            if query in data:
                coin = data[query]
                quote = coin['quote']['USD']
                price_usd = quote['price']
                
                # Кросс-курсы (примерные)
                eur_rate = 0.96
                uah_rate = 41.60
                rub_rate = 96.50
                
                res = {
                    'id': None, 
                    'name': coin['name'], 
                    'symbol': coin['symbol'], 
                    'image': None,
                    'usd': round(price_usd, 2),
                    'eur': round(price_usd * eur_rate, 2),
                    'uah': round(price_usd * uah_rate, 2),
                    'rub': round(price_usd * rub_rate, 2),
                    'change_24h': quote['percent_change_24h']
                }
                price_cache[query] = res
                return res
        except Exception as e:
            logger.error(f"CMC Error: {e}")
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
                change = float(c['changePercent24Hr'])
                res = {
                    'id': c['id'],
                    'name': c['name'], 'symbol': c['symbol'], 'image': None,
                    'usd': round(p, 2), 'eur': round(p*0.96, 2), 
                    'uah': round(p*41.6, 2), 'rub': round(p*96.5, 2),
                    'change_24h': change
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
                    'id': None,
                    'name': query, 'symbol': query, 'image': None,
                    'usd': d['USD'], 'eur': d['EUR'], 'uah': d['UAH'], 'rub': d['RUB'],
                    'change_24h': 0
                }
                price_cache[query] = res
                return res
        except: pass
        return None