/**
 * Price Service - Multi-source API aggregator
 * Sources: CoinGecko, CoinMarketCap, CoinCap, CryptoCompare
 */

export class PriceService {
  constructor(env) {
    this.env = env;
    this.sources = [
      { name: 'coingecko', fn: this.fetchFromCoinGecko.bind(this) },
      { name: 'coinmarketcap', fn: this.fetchFromCoinMarketCap.bind(this) },
      { name: 'coincap', fn: this.fetchFromCoinCap.bind(this) },
      { name: 'cryptocompare', fn: this.fetchFromCryptoCompare.bind(this) }
    ];
  }

  /**
   * Get price data with automatic fallback between sources
   */
  async getPrice(coin) {
    for (const source of this.sources) {
      try {
        console.log(`Trying ${source.name} for ${coin}`);
        const data = await source.fn(coin);
        if (data) {
          console.log(`Success with ${source.name}`);
          return data;
        }
      } catch (error) {
        console.error(`${source.name} failed:`, error.message);
        continue;
      }
    }
    return null;
  }

  /**
   * Get top 10 cryptocurrencies
   */
  async getTop10() {
    try {
      return await this.fetchTop10FromCoinGecko();
    } catch (error) {
      console.error('CoinGecko top10 failed:', error);
    }

    try {
      return await this.fetchTop10FromCoinMarketCap();
    } catch (error) {
      console.error('CoinMarketCap top10 failed:', error);
    }

    try {
      return await this.fetchTop10FromCoinCap();
    } catch (error) {
      console.error('CoinCap top10 failed:', error);
    }

    throw new Error('All sources failed for top10');
  }

  /**
   * CoinGecko API - includes fuzzy search
   */
  async fetchFromCoinGecko(coin) {
    const apiKey = this.env.COINGECKO_API_KEY;
    
    // Use search endpoint for better matching
    const searchUrl = `https://api.coingecko.com/api/v3/search?query=${encodeURIComponent(coin)}`;
    
    const searchResponse = await fetch(searchUrl, {
      headers: { 'x-cg-demo-api-key': apiKey }
    });
    
    if (!searchResponse.ok) throw new Error('CoinGecko search failed');
    
    const searchData = await searchResponse.json();
    
    // Find best match: exact symbol match first, then name match
    let coinData = null;
    
    if (searchData.coins && searchData.coins.length > 0) {
      const exactSymbol = searchData.coins.find(c => 
        c.symbol.toLowerCase() === coin.toLowerCase()
      );
      
      const exactName = searchData.coins.find(c => 
        c.name.toLowerCase() === coin.toLowerCase()
      );
      
      coinData = exactSymbol || exactName || searchData.coins[0];
    }
    
    if (!coinData) return null;

    const coinId = coinData.id;
    const detailUrl = `https://api.coingecko.com/api/v3/coins/${coinId}?localization=false&tickers=false&community_data=false&developer_data=false`;
    
    const detailResponse = await fetch(detailUrl, {
      headers: { 'x-cg-demo-api-key': apiKey }
    });
    
    if (!detailResponse.ok) throw new Error('CoinGecko detail failed');
    
    const data = await detailResponse.json();

    return {
      id: coinId,
      name: data.name,
      symbol: data.symbol,
      price: data.market_data.current_price.usd,
      change24h: data.market_data.price_change_percentage_24h || 0,
      marketCap: data.market_data.market_cap.usd,
      volume24h: data.market_data.total_volume.usd,
      circulatingSupply: data.market_data.circulating_supply
    };
  }

  async fetchTop10FromCoinGecko() {
    const apiKey = this.env.COINGECKO_API_KEY;
    const url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false';
    
    const response = await fetch(url, {
      headers: { 'x-cg-demo-api-key': apiKey }
    });
    
    if (!response.ok) throw new Error('CoinGecko top10 failed');
    
    const data = await response.json();
    
    return data.map(coin => ({
      name: coin.name,
      symbol: coin.symbol,
      price: coin.current_price,
      change24h: coin.price_change_percentage_24h || 0,
      marketCap: coin.market_cap
    }));
  }

  /**
   * CoinMarketCap API
   */
  async fetchFromCoinMarketCap(coin) {
    const apiKey = this.env.COINMARKETCAP_API_KEY;
    
    // Try by symbol first
    const searchUrl = `https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?symbol=${encodeURIComponent(coin.toUpperCase())}`;
    
    const searchResponse = await fetch(searchUrl, {
      headers: { 'X-CMC_PRO_API_KEY': apiKey }
    });
    
    if (!searchResponse.ok) throw new Error('CoinMarketCap search failed');
    
    const searchData = await searchResponse.json();
    let coinData = searchData.data?.[0];
    
    // If no match by symbol, try by name using search endpoint
    if (!coinData) {
      const nameSearchUrl = `https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?limit=5`;
      const nameSearchResponse = await fetch(nameSearchUrl, {
        headers: { 'X-CMC_PRO_API_KEY': apiKey }
      });
      
      const nameSearchData = await nameSearchResponse.json();
      coinData = nameSearchData.data?.find(c => 
        c.name.toLowerCase().includes(coin.toLowerCase()) ||
        c.symbol.toLowerCase() === coin.toLowerCase()
      );
    }
    
    if (!coinData) return null;

    const quoteUrl = `https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id=${coinData.id}`;
    
    const quoteResponse = await fetch(quoteUrl, {
      headers: { 'X-CMC_PRO_API_KEY': apiKey }
    });
    
    if (!quoteResponse.ok) throw new Error('CoinMarketCap quote failed');
    
    const quoteData = await quoteResponse.json();
    const data = quoteData.data[coinData.id];

    return {
      id: coinData.slug,
      name: data.name,
      symbol: data.symbol,
      price: data.quote.USD.price,
      change24h: data.quote.USD.percent_change_24h || 0,
      marketCap: data.quote.USD.market_cap,
      volume24h: data.quote.USD.volume_24h,
      circulatingSupply: data.circulating_supply
    };
  }

  async fetchTop10FromCoinMarketCap() {
    const apiKey = this.env.COINMARKETCAP_API_KEY;
    const url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=10';
    
    const response = await fetch(url, {
      headers: { 'X-CMC_PRO_API_KEY': apiKey }
    });
    
    if (!response.ok) throw new Error('CoinMarketCap top10 failed');
    
    const data = await response.json();
    
    return data.data.map(coin => ({
      name: coin.name,
      symbol: coin.symbol,
      price: coin.quote.USD.price,
      change24h: coin.quote.USD.percent_change_24h || 0,
      marketCap: coin.quote.USD.market_cap
    }));
  }

  /**
   * CoinCap API (No API key required)
   */
  async fetchFromCoinCap(coin) {
    const searchUrl = `https://api.coincap.io/v2/assets?search=${encodeURIComponent(coin)}&limit=5`;
    
    const searchResponse = await fetch(searchUrl);
    if (!searchResponse.ok) throw new Error('CoinCap search failed');
    
    const searchData = await searchResponse.json();
    
    // Find best match
    let coinData = null;
    if (searchData.data && searchData.data.length > 0) {
      coinData = searchData.data.find(c => 
        c.symbol.toLowerCase() === coin.toLowerCase()
      ) || searchData.data.find(c =>
        c.name.toLowerCase() === coin.toLowerCase()
      ) || searchData.data[0];
    }
    
    if (!coinData) return null;

    return {
      id: coinData.id,
      name: coinData.name,
      symbol: coinData.symbol,
      price: parseFloat(coinData.priceUsd),
      change24h: parseFloat(coinData.changePercent24Hr) || 0,
      marketCap: parseFloat(coinData.marketCapUsd),
      volume24h: parseFloat(coinData.volumeUsd24Hr),
      circulatingSupply: parseFloat(coinData.supply)
    };
  }

  async fetchTop10FromCoinCap() {
    const url = 'https://api.coincap.io/v2/assets?limit=10';
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('CoinCap top10 failed');
    
    const data = await response.json();
    
    return data.data.map(coin => ({
      name: coin.name,
      symbol: coin.symbol,
      price: parseFloat(coin.priceUsd),
      change24h: parseFloat(coin.changePercent24Hr) || 0,
      marketCap: parseFloat(coin.marketCapUsd)
    }));
  }

  /**
   * CryptoCompare API (No API key required for basic data)
   */
  async fetchFromCryptoCompare(coin) {
    const symbol = coin.toUpperCase();
    const priceUrl = `https://min-api.cryptocompare.com/data/pricemultifull?fsyms=${symbol}&tsyms=USD`;
    
    const priceResponse = await fetch(priceUrl);
    if (!priceResponse.ok) throw new Error('CryptoCompare price failed');
    
    const priceData = await priceResponse.json();
    const data = priceData.RAW?.[symbol]?.USD;
    
    if (!data) return null;

    return {
      id: symbol.toLowerCase(),
      name: data.FROMSYMBOL,
      symbol: symbol,
      price: data.PRICE,
      change24h: data.CHANGEPCT24HOUR || 0,
      marketCap: data.MKTCAP,
      volume24h: data.VOLUME24HOURTO,
      circulatingSupply: data.SUPPLY
    };
  }
}