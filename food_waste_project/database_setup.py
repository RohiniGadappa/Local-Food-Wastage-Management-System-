import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseSetup:
    def __init__(self, db_path="database/food_waste.db"):
        # I'm setting the database path to be in a separate 'database' folder for better organization
        self.db_path = db_path
        # I'm automatically creating the database directory if it doesn't exist - this prevents path errors
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def create_connection(self):
        """I created this method to handle database connections safely"""
        try:
            # I'm establishing a connection to my SQLite database
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            # I'm adding error handling to catch connection issues early
            print(f"Error creating connection: {e}")
            return None
    
    def create_tables(self):
        """I designed this method to create all the tables I need for my food waste system"""
        conn = self.create_connection()
        if conn is None:
            return
        
        try:
            cursor = conn.cursor()
            
            # I'm creating the Providers table - this stores all food suppliers in my system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    Provider_ID INTEGER PRIMARY KEY,    -- I use this as unique identifier
                    Name TEXT NOT NULL,                  -- Provider name is essential
                    Type TEXT NOT NULL,                  -- Restaurant, Grocery Store, Supermarket
                    Address TEXT,                        -- Physical location for pickups
                    City TEXT NOT NULL,                  -- Geographic categorization I need
                    Contact TEXT                         -- Communication is crucial
                )
            ''')
            
            # I'm creating the Receivers table - stores organizations and individuals who need food
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receivers (
                    Receiver_ID INTEGER PRIMARY KEY,    -- Unique ID for each receiver
                    Name TEXT NOT NULL,                  -- Who they are
                    Type TEXT NOT NULL,                  -- NGO, Community Center, Individual
                    City TEXT NOT NULL,                  -- Location for distribution planning
                    Contact TEXT                         -- How to reach them
                )
            ''')
            
            # I'm creating the Food Listings table - the heart of my system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_listings (
                    Food_ID INTEGER PRIMARY KEY,        -- Unique identifier for each food item
                    Food_Name TEXT NOT NULL,             -- What food is available
                    Quantity INTEGER NOT NULL,           -- How much is available
                    Expiry_Date DATE,                    -- Critical for food safety
                    Provider_ID INTEGER,                 -- Links to providers table
                    Provider_Type TEXT,                  -- Denormalized for quick queries
                    Location TEXT,                       -- Where to pick up
                    Food_Type TEXT,                      -- Vegetarian, Non-Vegetarian, Vegan
                    Meal_Type TEXT,                      -- Breakfast, Lunch, Dinner, Snacks
                    FOREIGN KEY (Provider_ID) REFERENCES providers (Provider_ID)  -- I enforce data integrity
                )
            ''')
            
            # I'm creating the Claims table - tracks who takes what food
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    Claim_ID INTEGER PRIMARY KEY,       -- Unique claim identifier
                    Food_ID INTEGER,                     -- Which food item is claimed
                    Receiver_ID INTEGER,                 -- Who is claiming it
                    Status TEXT,                         -- Pending, Completed, Cancelled
                    Timestamp DATETIME,                  -- When the claim was made
                    FOREIGN KEY (Food_ID) REFERENCES food_listings (Food_ID),      -- Links to food
                    FOREIGN KEY (Receiver_ID) REFERENCES receivers (Receiver_ID)   -- Links to receiver
                )
            ''')
            
            # I'm committing all table creations in one transaction
            conn.commit()
            print("Tables created successfully!")
            
        except sqlite3.Error as e:
            # I'm catching any SQL errors during table creation
            print(f"Error creating tables: {e}")
        finally:
            # I always close the connection to prevent resource leaks
            conn.close()
    
    def load_csv_data(self):
        """I built this method to populate my database with initial data from CSV files"""
        conn = self.create_connection()
        if conn is None:
            return
        
        try:
            # I'm loading providers data from CSV - restaurants, stores, etc.
            providers_df = pd.read_csv('data/providers_data.csv')
            # I use 'replace' to ensure clean data loading each time
            providers_df.to_sql('providers', conn, if_exists='replace', index=False)
            
            # I'm loading receivers data - NGOs, community centers, individuals
            receivers_df = pd.read_csv('data/receivers_data.csv')
            receivers_df.to_sql('receivers', conn, if_exists='replace', index=False)
            
            # I'm loading food listings - the main inventory data
            food_listings_df = pd.read_csv('data/food_listings_data.csv')
            food_listings_df.to_sql('food_listings', conn, if_exists='replace', index=False)
            
            # I'm loading claims data - tracks food distribution
            claims_df = pd.read_csv('data/claims_data.csv')
            claims_df.to_sql('claims', conn, if_exists='replace', index=False)
            
            print("Data loaded successfully!")
            
        except Exception as e:
            # I'm handling any errors during data loading - file not found, formatting issues, etc.
            print(f"Error loading data: {e}")
        finally:
            # I always ensure the connection is closed
            conn.close()

# This is where I run the database setup when the script is executed directly
if __name__ == "__main__":
    # I'm creating an instance of my DatabaseSetup class
    db_setup = DatabaseSetup()
    # I run table creation first - must happen before data loading
    db_setup.create_tables()
    # Then I load all the CSV data into my newly created tables
    db_setup.load_csv_data()
    print("Database setup completed!")