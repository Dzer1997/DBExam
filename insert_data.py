from data_connextion import connect_to_database
from mysql.connector import Error
import mysql.connector
# Insert into Countries Table
# ------------------------------  
def insert_country(connection, country_name):
  cursor = connection.cursor()
  cursor.execute("SELECT country_id FROM Countries WHERE country_name = %s", (country_name,))
  result = cursor.fetchone()
  if result:
    print(f"{country_name} already exists with ID {result[0]}")
  else:
      cursor.execute("INSERT INTO Countries (country_name) VALUES (%s)", (country_name,))
      connection.commit()
      print(f"Inserted: {country_name}")
  cursor.close()
# Insert into Cities Table
# ------------------------------  
def get_country_id(connection, country_name):
    cursor = connection.cursor()
    cursor.execute("SELECT country_id FROM Countries WHERE country_name = %s", (country_name,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def insert_city(connection, city_name, country_name):
    country_id = get_country_id(connection, country_name)
    if not country_id:
        print(f"Country '{country_name}' does not exist. Insert it first.")
        return

    cursor = connection.cursor()
    cursor.execute("SELECT city_id FROM Cities WHERE city_name = %s AND country_id = %s", (city_name, country_id))
    if cursor.fetchone():
        print(f"{city_name} already exists in {country_name}")
    else:
        cursor.execute("INSERT INTO Cities (city_name, country_id) VALUES (%s, %s)", (city_name, country_id))
        connection.commit()
        print(f"Inserted city: {city_name} in country: {country_name}")
    cursor.close()

# Insert into Airline Table
# ------------------------------
def insert_airline(connection, airline_name, airline_code):

  cursor = connection.cursor()
  cursor.execute("SELECT COUNT(*) FROM airline WHERE airline_code = %s", (airline_code,))
  result = cursor.fetchone()
  if result[0] == 0:
    query = "INSERT INTO airline (airline_name, airline_code) VALUES (%s, %s)"
    try:
      cursor.execute(query, (airline_name, airline_code))
      connection.commit()
      print(f"Inserted: {airline_name} ({airline_code})")
    except Error as e:
      print(f"Insert error for {airline_name}: {e}")   
  else:
    print(f"Airline code {airline_code} already exists. Skipping insertion.")
  cursor.close()       

# Insert into airports Table
# ------------------------------  
def insert_airport(connection, airport_code, airport_name):
    cursor = connection.cursor()
    cursor.execute("SELECT airport_code FROM Airports WHERE airport_code = %s", (airport_code,))
    result = cursor.fetchone()
    if result is None:
        try:
            query = "INSERT INTO Airports (airport_code, airport_name) VALUES (%s, %s)"
            cursor.execute(query, (airport_code, airport_name))
            connection.commit()
            print(f"Inserted: {airport_name} ({airport_code})")
        except Exception as e:
            print(f"Insert error for {airport_name}: {e}")
    else:
        print(f"Airport code {airport_code} already exists. Skipping insertion.")

    cursor.close()
# insert data into Hosts table   

def insert_hosts(connection, host_id, host_name):
    cursor = connection.cursor()
    cursor.execute("SELECT host_id FROM Hosts WHERE host_id = %s", (host_id,))
    result = cursor.fetchone()
    if result is None:
       cursor.execute(
        "INSERT INTO hosts (host_id, host_name) VALUES (%s, %s)",
        (host_id, host_name)
    )
    connection.commit()
    print(f"Inserted: {host_name}")
    cursor.close()
# Insert into Listings
# ------------------------------   
def get_city_id(connection, city_name):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT city_id FROM Cities WHERE city_name = %s", (city_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()

def insert_Listings(connection, listing_id, host_id, room_type, listing_name, city_name):
    city_id = get_city_id(connection, city_name)
    if not city_id:
        print(f"City '{city_name}' does not exist. Insert it first.")
        return

    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Listings (listing_id, host_id, city_id, room_type, listing_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (listing_id, host_id, city_id, room_type, listing_name))
        connection.commit()
        print(f"Inserted listing: {listing_name}")
    except mysql.connector.IntegrityError as e:
        print(f"Insert error for '{listing_name}': {e}")
    finally:
        cursor.close()

# Insert into Pricing
# ------------------------------  
def insert_pricing(connection, listing_id, price, minimum_nights):
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Pricing (listing_id, price, minimum_nights)
            VALUES (%s, %s, %s)
        """, (listing_id, price, minimum_nights))
        connection.commit()
        print(f"Inserted pricing for listing ID {listing_id}")
    except mysql.connector.IntegrityError as e:
        print(f"Error inserting pricing: {e}")
    finally:
        cursor.close()

# Insert into availability
# ------------------------------  
def insert_availability(connection, listing_id, availability_365):
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Availability (listing_id, availability_365)
            VALUES (%s, %s)
        """, (listing_id, availability_365))
        connection.commit()
        print(f"Inserted availability for listing ID {listing_id}")
    except mysql.connector.IntegrityError as e:
        print(f"Error inserting availability: {e}")
    finally:
        cursor.close()
# insert into city_airport
# --------------------------------------------------------
def insert_city_airport(connection, city_name, airport_code):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT city_id FROM Cities WHERE city_name = %s", (city_name,))
        city_result = cursor.fetchone()
        if not city_result:
            print(f"City '{city_name}' does not exist.")
            return
        city_id = city_result[0]
        cursor.execute("""
            SELECT 1 FROM City_Airports
            WHERE city_id = %s AND airport_code = %s
        """, (city_id, airport_code))
        if cursor.fetchone():
            print(f"both (city: '{city_name}', airport: '{airport_code}') already linked.")
            return
        cursor.execute("""
            INSERT INTO City_Airports (city_id, airport_code)
            VALUES (%s, %s)
        """, (city_id, airport_code))
        connection.commit()
        print(f"Linked city '{city_name}' to airport '{airport_code}'")

    except mysql.connector.Error as e:
        print(f"MySQL error: {e}")
    finally:
        cursor.close()
# insert into Flights 
#----------------------------------------------------------------------

def insert_flight(connection, airline_code, start_code, end_code, departure, arrival):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT airline_id FROM airline WHERE airline_code = %s", (airline_code,))
        result = cursor.fetchone()
        if not result:
            print(f"Airline code '{airline_code}' not found.")
            return
        airline_id = result[0]
        cursor.execute("""
            INSERT INTO Flights (
                airline_id, start_airport_code, end_airport_code, departure_time, arrival_time
            ) VALUES (%s, %s, %s, %s, %s)
        """, (airline_id, start_code, end_code, departure, arrival))
        connection.commit()
        print(f"Inserted flight for airline '{airline_code}' from {start_code} to {end_code}")
    except mysql.connector.Error as e:
        print(f"MySQL error inserting flight: {e}")
    finally:
        cursor.close()
# insert into TABLE flights_classes 
# -----------------------------------------------------------------------
def get_flight_id(connection, airline_code, start_code, end_code, departure, arrival):
    cursor = connection.cursor(buffered=True) 
    try:
        cursor.execute("SELECT airline_id FROM airline WHERE airline_code = %s", (airline_code,))
        airline_result = cursor.fetchone()
        if not airline_result:
            print(f"Airline '{airline_code}' not found.")
            return None
        airline_id = airline_result[0]
        cursor.execute("""
            SELECT flight_id FROM Flights
            WHERE airline_id = %s AND start_airport_code = %s AND end_airport_code = %s
              AND departure_time = %s AND arrival_time = %s
        """, (airline_id, start_code, end_code, departure, arrival))
        flight_result = cursor.fetchone()
        if not flight_result:
            print(f"Flight not found for airline '{airline_code}' from {start_code} to {end_code} at {departure}")
            return None
        return flight_result[0]
    finally:
        cursor.close()

def insert_flight_class(connection, flight_id, class_type, price):
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO flights_classes (flight_id, class_type, price)
            VALUES (%s, %s, %s)
        """, (flight_id, class_type, price))
        connection.commit()
        print(f"Inserted class '{class_type}' for flight {flight_id}")
    except mysql.connector.Error as e:
        print(f"MySQL error inserting flight class: {e}")
    finally:
        cursor.close()

def get_city_id(connection, city_name):
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("SELECT city_id FROM Cities WHERE city_name = %s", (city_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()

def insert_flight_route(connection, start_city_name, end_city_name):
    start_city_id = get_city_id(connection, start_city_name)
    end_city_id = get_city_id(connection, end_city_name)

    if not start_city_id or not end_city_id:
        print(f"Missing city_id for '{start_city_name}' or '{end_city_name}'")
        return

    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO FlightRoute (start_city_id, end_city_id)
            VALUES (%s, %s)
        """, (start_city_id, end_city_id))
        connection.commit()
        print(f"Inserted route: {start_city_name} → {end_city_name}")
    except mysql.connector.Error as e:
        print(f"Insert error: {e}")
    finally:
        cursor.close()


