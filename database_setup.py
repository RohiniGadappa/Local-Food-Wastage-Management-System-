import sqlite3
import pandas as pd
from datetime import datetime
import os
import streamlit as st

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
            raise Exception("Could not connect to database")
        
        try:
            cursor = conn.cursor()
            
            # I'm creating the Providers table - this stores all food suppliers in my system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    Provider_ID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Type TEXT NOT NULL,
                    Address TEXT,
                    City TEXT NOT NULL,
                    Contact TEXT
                )
            ''')
            
            # I'm creating the Receivers table - stores organizations and individuals who need food
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receivers (
                    Receiver_ID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Type TEXT NOT NULL,
                    City TEXT NOT NULL,
                    Contact TEXT
                )
            ''')
            
            # I'm creating the Food Listings table - the heart of my system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_listings (
                    Food_ID INTEGER PRIMARY KEY,
                    Food_Name TEXT NOT NULL,
                    Quantity INTEGER NOT NULL,
                    Expiry_Date DATE,
                    Provider_ID INTEGER,
                    Provider_Type TEXT,
                    Location TEXT,
                    Food_Type TEXT,
                    Meal_Type TEXT,
                    FOREIGN KEY (Provider_ID) REFERENCES providers (Provider_ID)
                )
            ''')
            
            # I'm creating the Claims table - tracks who takes what food
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    Claim_ID INTEGER PRIMARY KEY,
                    Food_ID INTEGER,
                    Receiver_ID INTEGER,
                    Status TEXT,
                    Timestamp DATETIME,
                    FOREIGN KEY (Food_ID) REFERENCES food_listings (Food_ID),
                    FOREIGN KEY (Receiver_ID) REFERENCES receivers (Receiver_ID)
                )
            ''')
            
            # I'm committing all table creations in one transaction
            conn.commit()
            print("✅ Tables created successfully!")
            
        except sqlite3.Error as e:
            # I'm catching any SQL errors during table creation
            raise Exception(f"Error creating tables: {e}")
        finally:
            # I always close the connection to prevent resource leaks
            conn.close()
    
    def load_csv_data(self):
        """I built this method to populate my database with initial data from CSV files"""
        conn = self.create_connection()
        if conn is None:
            raise Exception("Could not connect to database")
        
        try:
            # Check if CSV files exist
            csv_files = {
                'providers': 'data/providers_data.csv',
                'receivers': 'data/receivers_data.csv',
                'food_listings': 'data/food_listings_data.csv',
                'claims': 'data/claims_data.csv'
            }
            
            for table_name, file_path in csv_files.items():
                if not os.path.exists(file_path):
                    raise Exception(f"CSV file not found: {file_path}")
            
            # I'm loading providers data from CSV
            providers_df = pd.read_csv('data/providers_data.csv')
            providers_df.to_sql('providers', conn, if_exists='replace', index=False)
            
            # I'm loading receivers data
            receivers_df = pd.read_csv('data/receivers_data.csv')
            receivers_df.to_sql('receivers', conn, if_exists='replace', index=False)
            
            # I'm loading food listings
            food_listings_df = pd.read_csv('data/food_listings_data.csv')
            food_listings_df.to_sql('food_listings', conn, if_exists='replace', index=False)
            
            # I'm loading claims data
            claims_df = pd.read_csv('data/claims_data.csv')
            claims_df.to_sql('claims', conn, if_exists='replace', index=False)
            
            print("✅ Data loaded successfully!")
            
        except Exception as e:
            # I'm handling any errors during data loading
            raise Exception(f"Error loading data: {e}")
        finally:
            # I always ensure the connection is closed
            conn.close()

# This is where I run the database setup when the script is executed directly
if __name__ == "__main__":
    try:
        # I'm creating an instance of my DatabaseSetup class
        db_setup = DatabaseSetup()
        # I run table creation first
        db_setup.create_tables()
        # Then I load all the CSV data
        db_setup.load_csv_data()
        print("🎉 Database setup completed!")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")