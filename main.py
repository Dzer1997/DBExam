import pandas as pd
from data_connextion import connect_to_database
from mysql.connector import Error
from insert_data import insert_airline, insert_pricing,insert_country, insert_city,insert_airport, insert_hosts,insert_Listings
from insert_data import insert_availability,insert_city_airport,insert_flight,get_flight_id,insert_flight_class,insert_flight_route
def add_country(file):
    df= pd.read_excel(file)
    connection = connect_to_database()
    if not connection:
        return
    for _, row in df.iterrows():
        insert_country(connection, row['Country'])
    connection.close()
    print("All data inserted.")  

def add_city(file):
    df= pd.read_excel(file)
    connection = connect_to_database()
    if not connection:
        return
    for _, row in df.iterrows():
        insert_city(connection,row['city'], row['country'])
    connection.close()
    print("All data inserted.")      

def add_airline(file):
    df = pd.read_excel(file)   
    connection = connect_to_database()
    if not connection:
        return
    for _, row in df.iterrows():
        try:
            insert_airline(connection, row['airline_name'], row['airline_code'])
        except Exception as e:
            print(f"Error inserting airline {row['airline_code']}: {e}")
    
    connection.close()
    print("All data inserted.")

def add_airports(file):
    df = pd.read_excel(file)   
    connection = connect_to_database()
    if not connection:
        return
    for _, row in df.iterrows():
        try:
            insert_airport(connection, row['airport_code'], row['airport_name'])
        except Exception as e:
            print(f"Error inserting airport {row['airport_code']}: {e}")
    
    connection.close()
    print("All data inserted.")
def add_hosts(file):
    df = pd.read_csv(file)

    connection = connect_to_database()
    if not connection:
        return
    for _, row in df.iterrows():
        try:
            insert_hosts(connection, row['host_id'],row['host_name'])
        except Exception as e:
            print(f"Error inserting hosts {row['host_name']}: {e}")
    
    connection.close()
    print("All data inserted.")

def add_listing(file):
    df = pd.read_csv(file)
    connection = connect_to_database()
    if not connection:
        return

    for _, row in df.iterrows():
        try:
            insert_Listings(
                connection,
                row['listing_id'],
                row['host_id'],
                row['room_type'],
                row['listing_name'],
                row['city_name']
            )
        except Exception as e:
            print(f"Error inserting listing '{row['listing_name']}': {e}")

    connection.close()

def add_pricing(file):
    df = pd.read_csv(file)
    connection = connect_to_database()
    if not connection:
        return

    for _, row in df.iterrows():
        try:
           insert_pricing(
                connection,
                row['listing_id'],
                row['price'],
                row['minimum_nights']
            )
        except Exception as e:
            print(f"Error inserting price '{row['price']}': {e}")

    connection.close()   

def add_availability(file):
    df = pd.read_csv(file)
    connection = connect_to_database()
    if not connection:
        return

    for _, row in df.iterrows():
        try:
           insert_availability(
                connection,
                row['listing_id'],
                row['availability_365']
            )
        except Exception as e:
            print(f"Error inserting availability'{row['availability_365']}': {e}")

    connection.close()  

def add_insert_city_airport():
    airport_city_df = pd.read_csv("mysql_import_ready_US Airline Flight Routes and Fares_carrier_lg.csv") 
    airport_city_df = airport_city_df.rename(columns={'start_city': 'city_name',
                                                      'start_airport_code':'airport_code'})

    connection = connect_to_database()
    if not connection:
        print("Could not connect to the database.")
        return

    for _, row in airport_city_df.iterrows():
        city_name = row['city_name']
        airport_code = row['airport_code']
        insert_city_airport(connection, city_name, airport_code) 
    connection.close()

def add_city_airport():
    airport_city_df = pd.read_csv("mysql_import_ready_US Airline Flight Routes and Fares_carrier_lg.csv") 
    airport_city_df = airport_city_df.rename(columns={'end_city': 'city_name',
                                                      'end_airport_code':'airport_code'})

    connection = connect_to_database()
    if not connection:
        print("Could not connect to the database.")
        return

    for _, row in airport_city_df.iterrows():
        city_name = row['city_name']
        airport_code = row['airport_code']
        insert_city_airport(connection, city_name, airport_code) 
    connection.close()

def add_flights():
    df = pd.read_csv("mysql_import_ready_US Airline Flight Routes and Fares_carrier_lg.csv")

    connection = connect_to_database()
    if not connection:
        print("Could not connect to the database.")
        return

    for _, row in df.iterrows():
        insert_flight(
            connection,
            row['airline_code'],
            row['start_airport_code'],
            row['end_airport_code'],
            row['flight_datetime'],
            row['arrival_datetime']
        )

    connection.close()


def add_flight_classes():
    df = pd.read_csv("mysql_import_ready_US Airline Flight Routes and Fares_carrier_lg.csv")
    connection = connect_to_database()
    if not connection:
        print("Could not connect to the database.")
        return

    for _, row in df.iterrows():
        flight_id = get_flight_id(
            connection,
            row['airline_code'],
            row['start_airport_code'],
            row['end_airport_code'],
            row['flight_datetime'],
            row['arrival_datetime']
        )
        if not flight_id:
            print(f"Flight not found for airline {row['airline_code']} on {row['flight_datetime']}")
            continue

        insert_flight_class(
            connection,
            flight_id,
            row['class_type'],
            row[' price']
        )

    connection.close()

def add_routes():
    df = pd.read_csv("mysql_import_ready_US Airline Flight Routes and Fares_carrier_lg.csv")
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database.")
        return

    for _, row in df.iterrows():
        insert_flight_route(connection, row['start_city'], row['end_city'])

    connection.close()




#add_country("mysql_import_ready_country.xlsx")    
#add_city("mysql_import_ready_cities.xlsx")
#add_airline("mysql_import_ready_airline.xlsx")
#add_airports("mysql_import_ready_airport.xlsx")
#add_hosts("mysql_import_ready_Updated_AB_US_2023.csv")
#add_listing("mysql_import_ready_Updated_AB_US_2023.csv")
#add_pricing("mysql_import_ready_Updated_AB_US_2023.csv")
#add_availability("mysql_import_ready_Updated_AB_US_2023.csv")
#add_insert_city_airport()
#add_city_airport()
#add_flights()
#add_flight_classes() 
add_routes()