/**
 * Chart Service - Generate price charts
 * Note: This is a placeholder. Cloudflare Workers doesn't support canvas/matplotlib.
 * For chart generation, we need to use a third-party service or API.
 */

export class ChartService {
  /**
   * Generate a chart using QuickChart API (free, no API key needed)
   */
  async generateChart(coinId, prices24h) {
    if (!prices24h || prices24h.length === 0) {
      return null;
    }

    try {
      // Extract timestamps and prices
      const timestamps = prices24h.map(p => {
        const date = new Date(p[0]);
        return date.getHours() + ':00';
      });
      
      const prices = prices24h.map(p => p[1]);

      // Determine if price is going up or down
      const firstPrice = prices[0];
      const lastPrice = prices[prices.length - 1];
      const isUp = lastPrice >= firstPrice;

      // QuickChart configuration
      const chartConfig = {
        type: 'line',
        data: {
          labels: timestamps,
          datasets: [{
            label: 'Price (USD)',
            data: prices,
            borderColor: isUp ? '#00FF88' : '#FF4444',
            backgroundColor: isUp ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 68, 68, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: isUp ? '#00FF88' : '#FF4444',
            pointHoverBorderColor: '#FFFFFF',
            pointHoverBorderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: '24 Hour Price Chart',
              color: '#FFFFFF',
              font: {
                size: 18,
                weight: 'bold'
              }
            }
          },
          scales: {
            x: {
              display: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                drawBorder: false
              },
              ticks: {
                color: '#CCCCCC',
                maxRotation: 45,
                minRotation: 45,
                autoSkip: true,
                maxTicksLimit: 12
              }
            },
            y: {
              display: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                drawBorder: false
              },
              ticks: {
                color: '#CCCCCC',
                callback: function(value) {
                  return '$' + value.toFixed(value >= 1 ? 2 : 6);
                }
              }
            }
          },
          layout: {
            padding: 20
          }
        }
      };

      // QuickChart URL
      const chartUrl = `https://quickchart.io/chart?width=800&height=400&backgroundColor=rgb(30,30,46)&devicePixelRatio=2&c=${encodeURIComponent(JSON.stringify(chartConfig))}`;

      // Fetch the chart image
      const response = await fetch(chartUrl);
      
      if (!response.ok) {
        throw new Error('Chart generation failed');
      }

      return await response.arrayBuffer();
    } catch (error) {
      console.error('Chart generation error:', error);
      return null;
    }
  }

  /**
   * Alternative: Generate a simple SVG chart (lightweight, no external API)
   */
  async generateSVGChart(prices24h) {
    if (!prices24h || prices24h.length === 0) {
      return null;
    }

    const width = 800;
    const height = 400;
    const padding = 50;

    const prices = prices24h.map(p => p[1]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;

    // Generate path points
    const points = prices.map((price, index) => {
      const x = padding + (index / (prices.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((price - minPrice) / priceRange) * (height - 2 * padding);
      return `${x},${y}`;
    }).join(' L ');

    const isUp = prices[prices.length - 1] >= prices[0];
    const color = isUp ? '#00FF88' : '#FF4444';

    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${width}" height="${height}" fill="#1E1E2E"/>
  
  <!-- Grid lines -->
  <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#333" stroke-width="2"/>
  <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#333" stroke-width="2"/>
  
  <!-- Price line -->
  <path d="M ${points}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Title -->
  <text x="${width / 2}" y="30" fill="#FFFFFF" font-size="20" font-weight="bold" text-anchor="middle">24 Hour Price Chart</text>
  
  <!-- Min/Max labels -->
  <text x="${padding - 10}" y="${height - padding + 5}" fill="#CCCCCC" font-size="12" text-anchor="end">$${minPrice.toFixed(2)}</text>
  <text x="${padding - 10}" y="${padding}" fill="#CCCCCC" font-size="12" text-anchor="end">$${maxPrice.toFixed(2)}</text>
</svg>`;

    return Buffer.from(svg, 'utf-8');
  }
}
