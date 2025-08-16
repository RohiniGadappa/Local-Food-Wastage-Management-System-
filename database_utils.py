import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class DatabaseUtils:
    def __init__(self, db_path="database/food_waste.db"):
        # I'm setting up the path to my database - keeping it consistent with my main app
        self.db_path = db_path
    
    def backup_database(self, backup_path=None):
        """I created this method to protect my data - backups are essential for any real system"""
        if backup_path is None:
            # I'm generating a timestamp-based filename so I never overwrite previous backups
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"food_waste_backup_{timestamp}.db"
        
        try:
            # I'm connecting to my original database to read from it
            conn_orig = sqlite3.connect(self.db_path)
            
            # I'm creating a new database file for the backup
            conn_backup = sqlite3.connect(backup_path)
            # I use SQLite's built-in backup method - it's more reliable than manual copying
            conn_orig.backup(conn_backup)
            
            # I always close connections properly to avoid corruption
            conn_orig.close()
            conn_backup.close()
            
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            # I handle errors gracefully and inform the user what went wrong
            print(f"❌ Error creating backup: {e}")
            return None
    
    def get_database_stats(self):
        """I built this method to give me insights into my database health and usage"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # I'm using a dictionary to organize all my statistics
            stats = {}
            
            # I'm getting row counts for all my main tables - this shows system usage
            tables = ['providers', 'receivers', 'food_listings', 'claims']
            for table in tables:
                df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn)
                stats[f"{table}_count"] = df.iloc[0]['count']
            
            # I'm calculating food-specific statistics to understand inventory patterns
            food_stats = pd.read_sql_query("""
                SELECT 
                    SUM(Quantity) as total_quantity,    -- Total food available
                    AVG(Quantity) as avg_quantity,      -- Average listing size
                    MIN(Quantity) as min_quantity,      -- Smallest listing
                    MAX(Quantity) as max_quantity       -- Largest listing
                FROM food_listings
            """, conn)
            stats['food_stats'] = food_stats.to_dict('records')[0]
            
            # I'm analyzing claim patterns to understand success rates
            claim_stats = pd.read_sql_query("""
                SELECT 
                    Status,
                    COUNT(*) as count
                FROM claims
                GROUP BY Status
            """, conn)
            stats['claim_stats'] = claim_stats.to_dict('records')
            
            conn.close()
            return stats
        except Exception as e:
            # I return empty dict on error so the calling code doesn't break
            print(f"❌ Error getting database stats: {e}")
            return {}
    
    def clean_expired_food(self):
        """I implemented this for database maintenance - expired food shouldn't clutter the system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # I first count expired items so I can report how many were removed
            cursor.execute("SELECT COUNT(*) FROM food_listings WHERE Expiry_Date < date('now')")
            expired_count = cursor.fetchone()[0]
            
            if expired_count > 0:
                # I delete expired food items to keep the database clean
                cursor.execute("DELETE FROM food_listings WHERE Expiry_Date < date('now')")
                conn.commit()
                print(f"✅ Removed {expired_count} expired food items")
            else:
                # I give positive feedback when there's nothing to clean
                print("✅ No expired food items found")
            
            conn.close()
            return expired_count
        except Exception as e:
            # I return 0 on error so the calling code gets a sensible default
            print(f"❌ Error cleaning expired food: {e}")
            return 0
    
    def export_data_to_csv(self, output_dir="exports"):
        """I created this method for data portability - users might want to analyze data elsewhere"""
        import os
        
        try:
            # I create the output directory if it doesn't exist - prevents path errors
            os.makedirs(output_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            
            # I export all main tables for complete data backup
            tables = ['providers', 'receivers', 'food_listings', 'claims']
            exported_files = []
            
            for table in tables:
                # I read each table completely into a DataFrame
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                # I create descriptive filenames with table names
                file_path = os.path.join(output_dir, f"{table}_export.csv")
                # I export without index to keep CSV clean
                df.to_csv(file_path, index=False)
                exported_files.append(file_path)
                print(f"✅ Exported {table} to {file_path}")
            
            conn.close()
            return exported_files
        except Exception as e:
            # I return empty list on error so calling code can handle gracefully
            print(f"❌ Error exporting data: {e}")
            return []

# This is my utility script runner - I can execute this file directly for maintenance tasks
if __name__ == "__main__":
    # I create an instance of my utility class
    utils = DatabaseUtils()
    
    # I run database statistics to understand current state
    print("📊 Database Statistics:")
    stats = utils.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # I export all data for backup purposes
    print("\n🗂️ Exporting data...")
    exported = utils.export_data_to_csv()
    
    # I create a backup to ensure data safety
    print(f"\n💾 Creating backup...")
    backup = utils.backup_database()