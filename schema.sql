-- Database schema for CoinLuma Bot
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  language TEXT DEFAULT 'en',
  created_at INTEGER DEFAULT (strftime('%s', 'now')),
  last_active INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS searches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  coin_symbol TEXT,
  timestamp INTEGER DEFAULT (strftime('%s', 'now')),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_searches_timestamp ON searches(timestamp);
CREATE INDEX IF NOT EXISTS idx_searches_coin ON searches(coin_symbol);
CREATE INDEX IF NOT EXISTS idx_searches_user ON searches(user_id);
CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active);