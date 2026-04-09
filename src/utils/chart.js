/**
 * Chart Generation Helper
 * Generates chart URLs using QuickChart API
 */

export function generateChartUrl(symbol, change24h) {
  const isUp = change24h >= 0;
  const color = isUp ? '#00FF88' : '#FF4444';
  
  // Generate simple price trend chart
  const chartConfig = {
    type: 'line',
    data: {
      labels: ['24h ago', '18h', '12h', '6h', 'Now'],
      datasets: [{
        label: symbol,
        data: generateTrendData(change24h),
        borderColor: color,
        backgroundColor: `${color}33`,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: `${symbol} - 24h ${isUp ? '↑' : '↓'} ${Math.abs(change24h).toFixed(2)}%`,
          color: '#FFFFFF',
          font: { size: 16, weight: 'bold' }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          ticks: { color: '#CCCCCC' }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          ticks: { color: '#CCCCCC' }
        }
      },
      layout: { padding: 10 }
    }
  };

  const chartUrl = `https://quickchart.io/chart?width=600&height=300&backgroundColor=rgb(30,30,46)&c=${encodeURIComponent(JSON.stringify(chartConfig))}`;
  
  return chartUrl;
}

function generateTrendData(change24h) {
  // Generate realistic-looking trend data based on 24h change
  const endValue = 100;
  const startValue = 100 / (1 + change24h / 100);
  
  // Add some variance
  const data = [
    startValue,
    startValue + (endValue - startValue) * 0.2 + (Math.random() - 0.5) * 2,
    startValue + (endValue - startValue) * 0.5 + (Math.random() - 0.5) * 2,
    startValue + (endValue - startValue) * 0.75 + (Math.random() - 0.5) * 2,
    endValue
  ];
  
  return data;
}
