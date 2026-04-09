/**
 * Database Service for Cloudflare D1
 * Handles user management, search logging, and statistics
 */

export class DatabaseService {
  constructor(db) {
    this.db = db;
  }

  /**
   * Save or update user
   */
  async saveUser(userId, username, firstName, language) {
    try {
      const now = Math.floor(Date.now() / 1000);
      
      await this.db.prepare(`
        INSERT INTO users (user_id, username, first_name, language, created_at, last_active)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
          username = excluded.username,
          first_name = excluded.first_name,
          language = excluded.language,
          last_active = excluded.last_active
      `).bind(userId, username, firstName, language, now, now).run();
    } catch (error) {
      console.error('Database save user error:', error);
    }
  }

  /**
   * Log a search
   */
  async logSearch(userId, coinSymbol) {
    try {
      await this.db.prepare(`
        INSERT INTO searches (user_id, coin_symbol)
        VALUES (?, ?)
      `).bind(userId, coinSymbol).run();
    } catch (error) {
      console.error('Database log search error:', error);
    }
  }

  /**
   * Get statistics
   */
  async getStats() {
    try {
      const now = Math.floor(Date.now() / 1000);
      const dayAgo = now - 86400;

      // Total users
      const totalUsersResult = await this.db.prepare(`
        SELECT COUNT(*) as count FROM users
      `).first();
      
      // New users (24h)
      const newUsersResult = await this.db.prepare(`
        SELECT COUNT(*) as count FROM users WHERE created_at >= ?
      `).bind(dayAgo).first();
      
      // Active users (24h)
      const activeUsersResult = await this.db.prepare(`
        SELECT COUNT(*) as count FROM users WHERE last_active >= ?
      `).bind(dayAgo).first();
      
      // Total searches
      const totalSearchesResult = await this.db.prepare(`
        SELECT COUNT(*) as count FROM searches
      `).first();
      
      // Top searched coins
      const topCoinsResult = await this.db.prepare(`
        SELECT coin_symbol as symbol, COUNT(*) as count
        FROM searches
        GROUP BY coin_symbol
        ORDER BY count DESC
        LIMIT 10
      `).all();

      return {
        totalUsers: totalUsersResult?.count || 0,
        newUsers: newUsersResult?.count || 0,
        activeUsers: activeUsersResult?.count || 0,
        totalSearches: totalSearchesResult?.count || 0,
        topCoins: topCoinsResult?.results || []
      };
    } catch (error) {
      console.error('Database stats error:', error);
      return {
        totalUsers: 0,
        newUsers: 0,
        activeUsers: 0,
        totalSearches: 0,
        topCoins: []
      };
    }
  }

  /**
   * Get all users (for broadcasting)
   */
  async getAllUsers() {
    try {
      const result = await this.db.prepare(`
        SELECT user_id, username, first_name, language
        FROM users
        ORDER BY last_active DESC
      `).all();
      
      return result?.results || [];
    } catch (error) {
      console.error('Database get all users error:', error);
      return [];
    }
  }

  /**
   * Get user by ID
   */
  async getUser(userId) {
    try {
      return await this.db.prepare(`
        SELECT * FROM users WHERE user_id = ?
      `).bind(userId).first();
    } catch (error) {
      console.error('Database get user error:', error);
      return null;
    }
  }
}