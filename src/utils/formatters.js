/**
 * Formatting Helper Functions
 */

export function formatPrice(price) {
  if (price >= 1) {
    return price.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  return price.toFixed(8);
}

export function formatLargeNumber(num) {
  if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
}
