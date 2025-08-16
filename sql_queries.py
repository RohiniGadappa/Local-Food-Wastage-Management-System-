import sqlite3
import pandas as pd

class SQLQueries:
    def __init__(self, db_path="database/food_waste.db"):
        self.db_path = db_path
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results as DataFrame"""
        try:
            conn = sqlite3.connect(self.db_path)
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def query_1_providers_receivers_by_city(self):
        """1. How many food providers and receivers are there in each city?"""
        query = '''
        SELECT 
            City,
            COUNT(*) as Count,
            'Providers' as Type
        FROM providers 
        GROUP BY City
        UNION ALL
        SELECT 
            City,
            COUNT(*) as Count,
            'Receivers' as Type
        FROM receivers 
        GROUP BY City
        ORDER BY City, Type
        '''
        return self.execute_query(query)
    
    def query_2_provider_type_contribution(self):
        """2. Which type of food provider contributes the most food?"""
        query = '''
        SELECT 
            p.Type as Provider_Type,
            SUM(fl.Quantity) as Total_Quantity,
            COUNT(fl.Food_ID) as Total_Items,
            ROUND(AVG(fl.Quantity), 2) as Avg_Quantity
        FROM providers p
        JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.Type
        ORDER BY Total_Quantity DESC
        '''
        return self.execute_query(query)
    
    def query_3_provider_contacts_by_city(self, city):
        """3. Contact information of food providers in a specific city"""
        query = '''
        SELECT Name, Type, Address, Contact
        FROM providers
        WHERE City = ?
        ORDER BY Type, Name
        '''
        return self.execute_query(query, (city,))
    
    def query_4_top_claiming_receivers(self):
        """4. Which receivers have claimed the most food?"""
        query = '''
        SELECT 
            r.Name,
            r.Type,
            r.City,
            COUNT(c.Claim_ID) as Total_Claims,
            SUM(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE 0 END) as Food_Received,
            SUM(CASE WHEN c.Status = 'Pending' THEN fl.Quantity ELSE 0 END) as Food_Pending
        FROM receivers r
        LEFT JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        LEFT JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
        ORDER BY Food_Received DESC
        '''
        return self.execute_query(query)
    
    def query_5_total_food_quantity(self):
        """5. Total quantity of food available from all providers"""
        query = '''
        SELECT 
            SUM(Quantity) as Total_Available_Quantity,
            COUNT(Food_ID) as Total_Food_Items,
            COUNT(DISTINCT Provider_ID) as Active_Providers,
            ROUND(AVG(Quantity), 2) as Avg_Quantity_Per_Item
        FROM food_listings
        '''
        return self.execute_query(query)
    
    def query_6_city_food_listings(self):
        """6. Which city has the highest number of food listings?"""
        query = '''
        SELECT 
            Location as City,
            COUNT(Food_ID) as Total_Listings,
            SUM(Quantity) as Total_Quantity,
            ROUND(AVG(Quantity), 2) as Avg_Quantity
        FROM food_listings
        GROUP BY Location
        ORDER BY Total_Listings DESC
        '''
        return self.execute_query(query)
    
    def query_7_common_food_types(self):
        """7. What are the most commonly available food types?"""
        query = '''
        SELECT 
            Food_Type,
            COUNT(Food_ID) as Total_Items,
            SUM(Quantity) as Total_Quantity,
            ROUND(AVG(Quantity), 2) as Avg_Quantity,
            ROUND((COUNT(Food_ID) * 100.0 / (SELECT COUNT(*) FROM food_listings)), 2) as Percentage
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Total_Quantity DESC
        '''
        return self.execute_query(query)
    
    def query_8_claims_per_food_item(self):
        """8. How many food claims have been made for each food item?"""
        query = '''
        SELECT 
            fl.Food_Name,
            fl.Quantity as Available_Quantity,
            fl.Location,
            COUNT(c.Claim_ID) as Total_Claims,
            SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) as Completed_Claims,
            SUM(CASE WHEN c.Status = 'Pending' THEN 1 ELSE 0 END) as Pending_Claims,
            SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END) as Cancelled_Claims
        FROM food_listings fl
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Location
        ORDER BY Total_Claims DESC
        '''
        return self.execute_query(query)
    
    def query_9_successful_providers(self):
        """9. Which provider has had the highest number of successful food claims?"""
        query = '''
        SELECT 
            p.Name,
            p.Type,
            p.City,
            COUNT(c.Claim_ID) as Total_Claims,
            SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) as Successful_Claims,
            ROUND(
                (SUM(CASE WHEN c.Status = 'Completed' THEN 1.0 ELSE 0 END) * 100.0 / 
                 NULLIF(COUNT(c.Claim_ID), 0)), 2
            ) as Success_Rate_Percent
        FROM providers p
        JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        WHERE c.Claim_ID IS NOT NULL
        GROUP BY p.Provider_ID, p.Name, p.Type, p.City
        ORDER BY Successful_Claims DESC
        '''
        return self.execute_query(query)
    
    def query_10_claim_status_distribution(self):
        """10. What percentage of food claims are completed vs pending vs cancelled?"""
        query = '''
        SELECT 
            Status,
            COUNT(*) as Count,
            ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims)), 2) as Percentage
        FROM claims
        GROUP BY Status
        ORDER BY Count DESC
        '''
        return self.execute_query(query)
    
    def query_11_avg_quantity_per_receiver(self):
        """11. What is the average quantity of food claimed per receiver?"""
        query = '''
        SELECT 
            r.Name,
            r.Type,
            r.City,
            COUNT(c.Claim_ID) as Total_Claims,
            SUM(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE 0 END) as Total_Food_Received,
            ROUND(
                AVG(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE NULL END), 2
            ) as Avg_Quantity_Per_Claim
        FROM receivers r
        LEFT JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        LEFT JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
        HAVING Total_Claims > 0
        ORDER BY Total_Food_Received DESC
        '''
        return self.execute_query(query)
    
    def query_12_popular_meal_types(self):
        """12. Which meal type is claimed the most?"""
        query = '''
        SELECT 
            fl.Meal_Type,
            COUNT(c.Claim_ID) as Total_Claims,
            SUM(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE 0 END) as Quantity_Claimed,
            SUM(fl.Quantity) as Total_Available,
            ROUND(
                (SUM(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE 0 END) * 100.0 / 
                 SUM(fl.Quantity)), 2
            ) as Claim_Rate_Percent
        FROM food_listings fl
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Meal_Type
        ORDER BY Total_Claims DESC
        '''
        return self.execute_query(query)
    
    def query_13_provider_donations(self):
        """13. What is the total quantity of food donated by each provider?"""
        query = '''
        SELECT 
            p.Name,
            p.Type,
            p.City,
            COUNT(fl.Food_ID) as Items_Listed,
            SUM(fl.Quantity) as Total_Quantity_Listed,
            SUM(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE 0 END) as Quantity_Donated,
            ROUND(
                (SUM(CASE WHEN c.Status = 'Completed' THEN fl.Quantity ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(fl.Quantity), 0)), 2
            ) as Donation_Rate_Percent
        FROM providers p
        LEFT JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        GROUP BY p.Provider_ID, p.Name, p.Type, p.City
        ORDER BY Quantity_Donated DESC
        '''
        return self.execute_query(query)
    
    def query_14_expiring_food(self):
        """14. Which food items are expiring soon?"""
        query = '''
        SELECT 
            Food_Name,
            Quantity,
            Expiry_Date,
            Location,
            Food_Type,
            Meal_Type,
            julianday(Expiry_Date) - julianday('now') as Days_Until_Expiry,
            CASE 
                WHEN julianday(Expiry_Date) - julianday('now') < 0 THEN 'Expired'
                WHEN julianday(Expiry_Date) - julianday('now') <= 1 THEN 'Critical'
                WHEN julianday(Expiry_Date) - julianday('now') <= 3 THEN 'Warning'
                ELSE 'Safe'
            END as Status
        FROM food_listings
        WHERE julianday(Expiry_Date) - julianday('now') <= 5
        ORDER BY Days_Until_Expiry ASC
        '''
        return self.execute_query(query)
    
    def query_15_unclaimed_food(self):
        """15. What food items have not been claimed yet?"""
        query = '''
        SELECT 
            fl.Food_Name,
            fl.Quantity,
            fl.Expiry_Date,
            fl.Location,
            fl.Food_Type,
            fl.Meal_Type,
            p.Name as Provider_Name,
            p.Contact as Provider_Contact,
            julianday(fl.Expiry_Date) - julianday('now') as Days_Until_Expiry
        FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        WHERE c.Food_ID IS NULL
        ORDER BY fl.Expiry_Date ASC
        '''
        return self.execute_query(query)

    def get_all_queries_results(self):
        """Get results from all 15 queries"""
        results = {}
        
        results['Query 1: Providers & Receivers by City'] = self.query_1_providers_receivers_by_city()
        results['Query 2: Provider Type Contributions'] = self.query_2_provider_type_contribution()
        results['Query 4: Top Claiming Receivers'] = self.query_4_top_claiming_receivers()
        results['Query 5: Total Food Quantity'] = self.query_5_total_food_quantity()
        results['Query 6: City Food Listings'] = self.query_6_city_food_listings()
        results['Query 7: Common Food Types'] = self.query_7_common_food_types()
        results['Query 8: Claims per Food Item'] = self.query_8_claims_per_food_item()
        results['Query 9: Successful Providers'] = self.query_9_successful_providers()
        results['Query 10: Claim Status Distribution'] = self.query_10_claim_status_distribution()
        results['Query 11: Avg Quantity per Receiver'] = self.query_11_avg_quantity_per_receiver()
        results['Query 12: Popular Meal Types'] = self.query_12_popular_meal_types()
        results['Query 13: Provider Donations'] = self.query_13_provider_donations()
        results['Query 14: Expiring Food'] = self.query_14_expiring_food()
        results['Query 15: Unclaimed Food'] = self.query_15_unclaimed_food()
        
        return results