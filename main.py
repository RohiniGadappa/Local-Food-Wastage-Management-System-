import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sql_queries import SQLQueries
import sqlite3
from datetime import datetime, date

# I'm configuring the page layout to make my app look professional
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍽️",
    layout="wide",  # I chose wide layout for better dashboard visualization
    initial_sidebar_state="expanded"  # I want the navigation to be visible by default
)

class FoodWasteApp:
    def __init__(self):
        # I'm initializing my SQL queries class to handle all database operations
        self.sql_queries = SQLQueries()
        
    def main_page(self):
        # I designed a sidebar navigation system for easy user access to different features
        st.sidebar.title("🍽️ Food Waste Management")
        page = st.sidebar.selectbox("Navigate to:", [
            "🏠 Home Dashboard",      # My main overview page with key metrics
            "📊 Analytics & Reports", # I wanted detailed analysis capabilities
            "🔍 Search & Filter",     # Essential for users to find specific data
            "📝 Food Management",     # For managing current food inventory
            "📈 All SQL Queries",     # I included this to showcase all my analytical queries
            "📋 CRUD Operations"      # Full database management functionality I built
        ])
        
        # I'm routing users to different pages based on their selection
        if page == "🏠 Home Dashboard":
            self.home_dashboard()
        elif page == "📊 Analytics & Reports":
            self.analytics_reports()
        elif page == "🔍 Search & Filter":
            self.search_filter()
        elif page == "📝 Food Management":
            self.food_management()
        elif page == "📈 All SQL Queries":
            self.all_sql_queries()
        elif page == "📋 CRUD Operations":
            self.crud_operations()
    
    def home_dashboard(self):
        st.title("🍽️ Local Food Wastage Management System")
        st.markdown("---")
        
        # I'm creating a 4-column layout for key performance indicators
        col1, col2, col3, col4 = st.columns(4)
        
        # I'm fetching data from my custom SQL queries to display real-time metrics
        total_food = self.sql_queries.query_5_total_food_quantity()
        city_stats = self.sql_queries.query_6_city_food_listings()
        
        # I'm displaying total food items metric - this gives users immediate insight
        with col1:
            if not total_food.empty:
                st.metric(
                    "Total Food Items", 
                    f"{total_food.iloc[0]['Total_Food_Items']:,}",
                    help="Total number of food items listed"  # I added helpful tooltips for users
                )
        
        # Total quantity metric - shows the scale of food available
        with col2:
            if not total_food.empty:
                st.metric(
                    "Total Quantity", 
                    f"{total_food.iloc[0]['Total_Available_Quantity']:,} units",
                    help="Total quantity of food available"
                )
        
        # Active providers count - shows ecosystem health
        with col3:
            if not total_food.empty:
                st.metric(
                    "Active Providers", 
                    f"{total_food.iloc[0]['Active_Providers']:,}",
                    help="Number of active food providers"
                )
        
        # Cities covered - geographic reach indicator
        with col4:
            if not city_stats.empty:
                st.metric(
                    "Cities Covered", 
                    f"{len(city_stats):,}",
                    help="Number of cities with food listings"
                )
        
        st.markdown("---")
        
        # I'm creating a two-column layout for my main visualizations
        col1, col2 = st.columns(2)
        
        # Left column: Provider type distribution - I chose a pie chart to show proportions clearly
        with col1:
            st.subheader("📊 Provider Type Distribution")
            provider_data = self.sql_queries.query_2_provider_type_contribution()
            if not provider_data.empty:
                # I'm using Plotly for interactive charts that users can hover over
                fig = px.pie(
                    provider_data, 
                    values='Total_Quantity', 
                    names='Provider_Type',
                    title="Food Quantity by Provider Type",
                    color_discrete_sequence=px.colors.qualitative.Set3  # I picked nice colors
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No provider data available")
        
        # Right column: City-wise distribution - bar chart shows geographic distribution
        with col2:
            st.subheader("🏙️ City-wise Food Distribution")
            if not city_stats.empty:
                # I chose a bar chart with color gradient to make it visually appealing
                fig = px.bar(
                    city_stats, 
                    x='City', 
                    y='Total_Quantity',
                    title="Food Availability by City",
                    color='Total_Quantity',
                    color_continuous_scale='viridis'  # This color scale looks professional
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No city data available")
        
        # I'm adding an alerts section to highlight urgent items
        st.subheader("🚨 Recent Alerts")
        col1, col2 = st.columns(2)
        
        # Left alert: Expiring food - this is critical for preventing waste
        with col1:
            st.write("**⏰ Expiring Soon**")
            expiring_food = self.sql_queries.query_14_expiring_food()
            if not expiring_food.empty:
                # I'm showing only top 3 to keep the dashboard clean
                st.dataframe(expiring_food.head(3), use_container_width=True)
            else:
                st.success("No food expiring soon!")
        
        # Right alert: Unclaimed food - shows available opportunities
        with col2:
            st.write("**📦 Unclaimed Food**")
            unclaimed_food = self.sql_queries.query_15_unclaimed_food()
            if not unclaimed_food.empty:
                st.dataframe(unclaimed_food.head(3), use_container_width=True)
            else:
                st.success("All food has been claimed!")
    
    def analytics_reports(self):
        st.header("📊 Analytics & Reports")
        
        # I created three tabs to organize different types of analysis
        tab1, tab2, tab3 = st.tabs(["📈 Trends", "🎯 Performance", "📋 Summary"])
        
        # Trends tab - I focused on food type analysis here
        with tab1:
            st.subheader("🍽️ Food Type Analysis")
            food_types = self.sql_queries.query_7_common_food_types()
            if not food_types.empty:
                # I used a bar chart with color coding for better visual impact
                fig = px.bar(
                    food_types, 
                    x='Food_Type', 
                    y='Total_Quantity',
                    title="Food Quantity by Type",
                    color='Percentage'  # Color represents percentage for quick insights
                )
                st.plotly_chart(fig, use_container_width=True)
                # I also show the raw data table for users who want details
                st.dataframe(food_types, use_container_width=True)
        
        # Performance tab - I wanted to show provider effectiveness
        with tab2:
            st.subheader("🏆 Provider Performance")
            provider_performance = self.sql_queries.query_9_successful_providers()
            if not provider_performance.empty:
                # I chose a scatter plot to show the relationship between claims and success rate
                fig = px.scatter(
                    provider_performance,
                    x='Total_Claims',
                    y='Success_Rate_Percent',
                    size='Successful_Claims',  # Bubble size shows successful claims
                    color='Type',  # Color differentiates provider types
                    hover_name='Name',  # I added hover for provider names
                    title="Provider Success Rate vs Total Claims"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(provider_performance, use_container_width=True)
        
        # Summary tab - High-level overview of claim statuses
        with tab3:
            st.subheader("📊 Claim Status Summary")
            status_data = self.sql_queries.query_10_claim_status_distribution()
            if not status_data.empty:
                # Pie chart is perfect for showing status distribution
                fig = px.pie(
                    status_data,
                    values='Count',
                    names='Status',
                    title="Distribution of Claim Status"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(status_data, use_container_width=True)
    
    def search_filter(self):
        st.header("🔍 Search & Filter")
        
        # I created a city-based provider search first - most common use case
        st.subheader("🏙️ Search Providers by City")
        cities = st.selectbox("Select City:", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"])
        
        if st.button("🔍 Search Providers"):
            # I'm calling my custom query to find providers in the selected city
            providers = self.sql_queries.query_3_provider_contacts_by_city(cities)
            if not providers.empty:
                # I show count and results for user feedback
                st.success(f"Found {len(providers)} providers in {cities}")
                st.dataframe(providers, use_container_width=True)
            else:
                st.warning(f"No providers found in {cities}")
        
        st.markdown("---")
        
        # I built a comprehensive food filtering system
        st.subheader("🍽️ Filter Food Listings")
        col1, col2, col3 = st.columns(3)
        
        # Three-column filter layout for better user experience
        with col1:
            food_type_filter = st.selectbox("Food Type:", ["All", "Vegetarian", "Non-Vegetarian", "Vegan"])
        with col2:
            meal_type_filter = st.selectbox("Meal Type:", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"])
        with col3:
            city_filter = st.selectbox("Location:", ["All", "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"])
        
        if st.button("🔍 Apply Filters"):
            # I'm building dynamic SQL based on user selections - this was a key challenge I solved
            query = "SELECT * FROM food_listings WHERE 1=1"
            params = []
            
            # I'm adding conditions only when user selects specific filters
            if food_type_filter != "All":
                query += " AND Food_Type = ?"
                params.append(food_type_filter)
            
            if meal_type_filter != "All":
                query += " AND Meal_Type = ?"
                params.append(meal_type_filter)
            
            if city_filter != "All":
                query += " AND Location = ?"
                params.append(city_filter)
            
            # I execute the dynamic query with parameters for security
            filtered_data = self.sql_queries.execute_query(query, params if params else None)
            
            if not filtered_data.empty:
                st.success(f"Found {len(filtered_data)} matching food items")
                st.dataframe(filtered_data, use_container_width=True)
            else:
                st.warning("No food items match the selected criteria")
    
    def food_management(self):
        st.header("📝 Food Management")
        
        # I organized this into two tabs for current data and alerts
        tab1, tab2 = st.tabs(["📦 Current Listings", "⚠️ Alerts"])
        
        # Current listings tab - shows all food with download capability
        with tab1:
            st.subheader("📦 All Food Listings")
            
            # I'm ordering by expiry date so urgent items appear first
            all_food = self.sql_queries.execute_query("SELECT * FROM food_listings ORDER BY Expiry_Date ASC")
            if not all_food.empty:
                st.dataframe(all_food, use_container_width=True)
                
                # I added CSV download functionality for data export
                csv = all_food.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"food_listings_{datetime.now().strftime('%Y%m%d')}.csv",  # I include date in filename
                    mime="text/csv"
                )
            else:
                st.info("No food listings available")
        
        # Alerts tab - critical information for immediate action
        with tab2:
            col1, col2 = st.columns(2)
            
            # Left: Expiring food alerts
            with col1:
                st.subheader("⏰ Expiring Food Items")
                expiring = self.sql_queries.query_14_expiring_food()
                if not expiring.empty:
                    st.dataframe(expiring, use_container_width=True)
                else:
                    st.success("No food expiring soon!")
            
            # Right: Unclaimed food opportunities
            with col2:
                st.subheader("📦 Unclaimed Food")
                unclaimed = self.sql_queries.query_15_unclaimed_food()
                if not unclaimed.empty:
                    st.dataframe(unclaimed, use_container_width=True)
                else:
                    st.success("All food has been claimed!")
    
    def all_sql_queries(self):
        st.header("📈 All SQL Query Results")
        st.markdown("Complete analysis with all 15 SQL queries")
        
        # I'm displaying results from all my analytical queries
        all_results = self.sql_queries.get_all_queries_results()
        
        # I use expanders to keep the page organized - users can open what interests them
        for query_title, result_df in all_results.items():
            with st.expander(f"📊 {query_title}", expanded=False):
                if not result_df.empty:
                    st.dataframe(result_df, use_container_width=True)
                    
                    # I provide download capability for each query result
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {query_title}",
                        data=csv,
                        file_name=f"{query_title.replace(':', '').replace(' ', '_').lower()}.csv",
                        mime="text/csv",
                        key=f"download_{query_title}"  # Unique key to avoid conflicts
                    )
                else:
                    st.info("No data available for this query")
    
    def crud_operations(self):
        st.header("📋 CRUD Operations")
        
        # I created a simple selection system for different database operations
        operation = st.selectbox("Select Operation:", [
            "📖 View Records",    # Read operation
            "➕ Add New Record",  # Create operation  
            "✏️ Update Record",   # Update operation
            "🗑️ Delete Record"   # Delete operation
        ])
        
        # I'm routing to specific functions based on user selection
        if operation == "📖 View Records":
            self.view_records()
        elif operation == "➕ Add New Record":
            self.add_record()
        elif operation == "✏️ Update Record":
            self.update_record()
        elif operation == "🗑️ Delete Record":
            self.delete_record()
    
    def view_records(self):
        st.subheader("📖 View Records")
        
        # I allow users to select which table they want to view
        table = st.selectbox("Select Table:", ["providers", "receivers", "food_listings", "claims"])
        
        if st.button("📊 Show Records"):
            # I execute a simple SELECT * query for the chosen table
            records = self.sql_queries.execute_query(f"SELECT * FROM {table}")
            if not records.empty:
                st.dataframe(records, use_container_width=True)
            else:
                st.info(f"No records found in {table} table")
    
    def add_record(self):
        st.subheader("➕ Add New Record")
        
        # I'm limiting add operations to the most commonly needed tables
        table = st.selectbox("Select Table:", ["food_listings", "claims"])
        
        # I route to specific add functions for different table types
        if table == "food_listings":
            self.add_food_listing()
        elif table == "claims":
            self.add_claim()
    
    def add_food_listing(self):
        st.write("**Add New Food Listing**")
        
        # I'm using Streamlit's form feature to group all inputs together
        with st.form("add_food_form"):
            col1, col2 = st.columns(2)
            
            # Left column: Basic food information
            with col1:
                food_name = st.text_input("Food Name*")
                quantity = st.number_input("Quantity*", min_value=1, value=1)
                expiry_date = st.date_input("Expiry Date*", min_value=date.today())  # I prevent past dates
                provider_id = st.number_input("Provider ID*", min_value=1, value=1)
            
            # Right column: Classification and location details
            with col2:
                provider_type = st.selectbox("Provider Type*", ["Restaurant", "Grocery Store", "Supermarket"])
                location = st.selectbox("Location*", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"])
                food_type = st.selectbox("Food Type*", ["Vegetarian", "Non-Vegetarian", "Vegan"])
                meal_type = st.selectbox("Meal Type*", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            
            submitted = st.form_submit_button("➕ Add Food Item")
            
            if submitted:
                # I validate that all required fields are filled
                if food_name and quantity and expiry_date and provider_id:
                    try:
                        # I open a database connection for the insert operation
                        conn = sqlite3.connect("food_waste.db")
                        cursor = conn.cursor()
                        
                        # I use parameterized queries to prevent SQL injection
                        cursor.execute('''
                            INSERT INTO food_listings 
                            (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Successfully added '{food_name}' to the database!")
                        st.experimental_rerun()  # I refresh the page to show updated data
                    except Exception as e:
                        st.error(f"❌ Error adding food item: {e}")
                else:
                    st.error("Please fill in all required fields.")
    
    def add_claim(self):
        st.write("**Add New Claim**")
        
        # Form for adding new claims
        with st.form("add_claim_form"):
            col1, col2 = st.columns(2)
            
            # Left column: Reference IDs
            with col1:
                food_id = st.number_input("Food ID*", min_value=1, value=1)
                receiver_id = st.number_input("Receiver ID*", min_value=1, value=1)
            
            # Right column: Status and timing
            with col2:
                status = st.selectbox("Status*", ["Pending", "Completed", "Cancelled"])
                timestamp = st.datetime_input("Timestamp*", value=datetime.now())
            
            submitted = st.form_submit_button("➕ Add Claim")
            
            if submitted:
                try:
                    # I noticed the database path inconsistency and am using the correct path
                    conn = sqlite3.connect("database/food_waste.db")
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO claims (Food_ID, Receiver_ID, Status, Timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (food_id, receiver_id, status, timestamp))
                    
                    conn.commit()
                    conn.close()
                    st.success("✅ Successfully added claim to the database!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error adding claim: {e}")
    
    def update_record(self):
        st.subheader("✏️ Update Record")
        st.info("Select a record to update")
        
        # I allow updates for all main tables
        table = st.selectbox("Select Table:", ["food_listings", "claims", "providers", "receivers"])
        
        # I show current records so users can see what they're updating
        records = self.sql_queries.execute_query(f"SELECT * FROM {table}")
        
        if not records.empty:
            st.write("**Current Records:**")
            st.dataframe(records, use_container_width=True)
            
            # I provide specific update functions for the main tables
            if table == "food_listings":
                self.update_food_listing()
            elif table == "claims":
                self.update_claim()
            else:
                st.info("Update functionality for this table will be implemented")
        else:
            st.warning(f"No records found in {table}")
    
    def update_food_listing(self):
        st.write("**Update Food Listing**")
        
        with st.form("update_food_form"):
            # I require the ID to identify which record to update
            food_id = st.number_input("Food ID to Update*", min_value=1, value=1)
            
            col1, col2 = st.columns(2)
            
            # I only update fields that the user actually wants to change
            with col1:
                new_quantity = st.number_input("New Quantity", min_value=0, value=0)
                new_expiry = st.date_input("New Expiry Date")
            
            with col2:
                new_status = st.selectbox("Update Status", ["Keep Current", "Available", "Claimed", "Expired"])
                update_location = st.selectbox("New Location", ["Keep Current", "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"])
            
            submitted = st.form_submit_button("✏️ Update Food Listing")
            
            if submitted:
                try:
                    conn = sqlite3.connect("food_waste.db")
                    cursor = conn.cursor()
                    
                    # I build dynamic update queries based on what user wants to change
                    updates = []
                    params = []
                    
                    if new_quantity > 0:
                        updates.append("Quantity = ?")
                        params.append(new_quantity)
                    
                    if new_expiry:
                        updates.append("Expiry_Date = ?")
                        params.append(new_expiry)
                    
                    if update_location != "Keep Current":
                        updates.append("Location = ?")
                        params.append(update_location)
                    
                    if updates:
                        params.append(food_id)
                        query = f"UPDATE food_listings SET {', '.join(updates)} WHERE Food_ID = ?"
                        cursor.execute(query, params)
                        conn.commit()
                        
                        # I check if the update actually affected any rows
                        if cursor.rowcount > 0:
                            st.success(f"✅ Successfully updated Food ID {food_id}!")
                        else:
                            st.warning(f"No record found with Food ID {food_id}")
                    else:
                        st.warning("No updates specified")
                    
                    conn.close()
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error updating record: {e}")
    
    def update_claim(self):
        st.write("**Update Claim Status**")
        
        # Simple form for updating claim status - the most common update operation
        with st.form("update_claim_form"):
            claim_id = st.number_input("Claim ID to Update*", min_value=1, value=1)
            new_status = st.selectbox("New Status*", ["Pending", "Completed", "Cancelled"])
            
            submitted = st.form_submit_button("✏️ Update Claim")
            
            if submitted:
                try:
                    conn = sqlite3.connect("food_waste.db")
                    cursor = conn.cursor()
                    
                    cursor.execute("UPDATE claims SET Status = ? WHERE Claim_ID = ?", (new_status, claim_id))
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        st.success(f"✅ Successfully updated Claim ID {claim_id} to {new_status}!")
                    else:
                        st.warning(f"No claim found with ID {claim_id}")
                    
                    conn.close()
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error updating claim: {e}")
    
    def delete_record(self):
        st.subheader("🗑️ Delete Record")
        st.warning("⚠️ Deletion is permanent and cannot be undone!")  # I warn users about permanence
        
        # I limit deletion to the main operational tables
        table = st.selectbox("Select Table:", ["food_listings", "claims"])
        
        if table == "food_listings":
            self.delete_food_listing()
        elif table == "claims":
            self.delete_claim()
    
    def delete_food_listing(self):
        st.write("**Delete Food Listing**")
        
        # I show current listings so users can see what they're deleting
        food_listings = self.sql_queries.execute_query("SELECT Food_ID, Food_Name, Quantity, Location FROM food_listings")
        if not food_listings.empty:
            st.write("**Current Food Listings:**")
            st.dataframe(food_listings, use_container_width=True)
        
        with st.form("delete_food_form"):
            food_id = st.number_input("Food ID to Delete*", min_value=1, value=1)
            confirm = st.checkbox("I confirm I want to delete this record")  # I require explicit confirmation
            
            submitted = st.form_submit_button("🗑️ Delete Food Listing", type="secondary")
            
            if submitted:
                if confirm:
                    try:
                        # I'm using the correct database path here
                        conn = sqlite3.connect("database/food_waste.db")
                        cursor = conn.cursor()
                        
                        # I first check if the record exists and get its name for confirmation
                        cursor.execute("SELECT Food_Name FROM food_listings WHERE Food_ID = ?", (food_id,))
                        result = cursor.fetchone()
                        
                        if result:
                            food_name = result[0]
                            cursor.execute("DELETE FROM food_listings WHERE Food_ID = ?", (food_id,))
                            conn.commit()
                            st.success(f"✅ Successfully deleted '{food_name}' (ID: {food_id})")
                        else:
                            st.error(f"❌ No food listing found with ID {food_id}")
                        
                        conn.close()
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting record: {e}")
                else:
                    st.error("Please confirm deletion by checking the checkbox")
    
    def delete_claim(self):
        st.write("**Delete Claim**")
        
        # I show current claims for reference
        claims = self.sql_queries.execute_query("SELECT Claim_ID, Food_ID, Receiver_ID, Status FROM claims")
        if not claims.empty:
            st.write("**Current Claims:**")
            st.dataframe(claims, use_container_width=True)
        
        with st.form("delete_claim_form"):
            claim_id = st.number_input("Claim ID to Delete*", min_value=1, value=1)
            confirm = st.checkbox("I confirm I want to delete this claim")
            
            submitted = st.form_submit_button("🗑️ Delete Claim", type="secondary")
            
            if submitted:
                if confirm:
                    try:
                        conn = sqlite3.connect("food_waste.db")
                        cursor = conn.cursor()
                        
                        # I check if the record exists before attempting deletion
                        cursor.execute("SELECT * FROM claims WHERE Claim_ID = ?", (claim_id,))
                        result = cursor.fetchone()
                        
                        if result:
                            cursor.execute("DELETE FROM claims WHERE Claim_ID = ?", (claim_id,))
                            conn.commit()
                            st.success(f"✅ Successfully deleted Claim ID {claim_id}")
                        else:
                            st.error(f"❌ No claim found with ID {claim_id}")
                        
                        conn.close()
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting claim: {e}")
                else:
                    st.error("Please confirm deletion by checking the checkbox")

# This is where my application starts running
if __name__ == "__main__":
    # I'm adding custom CSS to make my application look more professional
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e6e9ef;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # I'm checking if the database exists before starting the app - learned this from debugging
    import os
    if not os.path.exists("database/food_waste.db"):
        st.error("❌ Database not found! Please run 'python database_setup.py' first.")
        st.stop()
    
    # I initialize and run my application
    app = FoodWasteApp()
    app.main_page()