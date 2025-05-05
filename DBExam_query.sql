CREATE DATABASE db_examv2;
USE  db_examv2;
-- USERS & PROFILES
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role ENUM('admin', 'traveler') NOT NULL
);

CREATE TABLE User_Profiles (
	user_id  INT PRIMARY KEY,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    city_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
    -- FOREIGN KEY (city_id) REFERENCES Cities(city_id)
);
-- Done
CREATE TABLE Countries (
    country_id INT PRIMARY KEY AUTO_INCREMENT,
    country_name VARCHAR(100) NOT NULL
);

-- Done
CREATE TABLE Cities (
    city_id INT PRIMARY KEY AUTO_INCREMENT,
    country_id INT NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Countries(country_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
 -- Done
-- Hosts table
CREATE TABLE Hosts (
    host_id BIGINT PRIMARY KEY,
    host_name VARCHAR(100)
);
-- Done
-- Listings table
CREATE TABLE Listings (
    listing_id BIGINT PRIMARY KEY,
    host_id BIGINT,
    city_id INT,
    -- instant_bookable BOOLEAN,
    -- cancellation_policy VARCHAR(50),
    room_type VARCHAR(50),
    listing_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (host_id) REFERENCES Hosts(host_id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES Cities(city_id) ON DELETE CASCADE
);
-- Done
-- Pricing table
CREATE TABLE Pricing (
    pricing_id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id BIGINT,
	price FLOAT NOT NULL,
    minimum_nights INT,
    FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE
);


-- Availability table
CREATE TABLE Availability (
    availability_id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id BIGINT,
    availability_365 INT,
    FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE
);


-- Done
-- Create the 'airline' table
CREATE TABLE airline (
    airline_id INT PRIMARY KEY AUTO_INCREMENT,
    airline_name VARCHAR(100) NOT NULL,
    airline_code CHAR(2) NOT NULL UNIQUE 
);
-- Done
-- Create the 'airports' table

CREATE TABLE Airports (
    airport_code CHAR(3) PRIMARY KEY,
    airport_name VARCHAR(100) NOT NULL
);

CREATE TABLE City_Airports (
    city_id INT,        
    airport_code CHAR(3), 
    PRIMARY KEY (city_id, airport_code),
    FOREIGN KEY (city_id) REFERENCES Cities(city_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (airport_code) REFERENCES Airports(airport_code) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create the 'Flights' table
CREATE TABLE Flights (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,  
    airline_id INT,                           
    start_airport_code CHAR(3),               
    end_airport_code CHAR(3),                 
    departure_time DATETIME NOT NULL,         
    arrival_time DATETIME NOT NULL,           
    FOREIGN KEY (start_airport_code) REFERENCES Airports(airport_code) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (end_airport_code) REFERENCES Airports(airport_code) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (airline_id) REFERENCES airline(airline_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE flights_classes (
    classes_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT,
    class_type VARCHAR(20) CHECK (class_type IN ('Economy', 'Business', 'First Class')),
    price FLOAT NOT NULL,
    -- seats_remaining INT NOT NULL,
    -- total_seats INT NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create the 'booking' table
CREATE TABLE Booking (
    bookingid INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    booking_type VARCHAR(20) CHECK (booking_type IN ('flight', 'airbnb')),
    booking_date DATETIME,
    status VARCHAR(20) CHECK (status IN ('confirmed', 'cancelled')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Booking_Details (
    booking_detail_id INT PRIMARY KEY AUTO_INCREMENT,
    airline_id int,
    booking_id INT,
    item_id INT,  
    item_type VARCHAR(20) CHECK (item_type IN ('flight', 'airbnb')),
    quantity INT DEFAULT 1,
    price FLOAT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Booking(bookingid)
    ON DELETE CASCADE
);


CREATE TABLE FlightRoute (
    route_id INT PRIMARY KEY AUTO_INCREMENT,  
    start_city_id INT NOT NULL,  
    end_city_id INT NOT NULL,
    FOREIGN KEY (start_city_id) REFERENCES cities(city_id) 
        ON DELETE CASCADE  
        ON UPDATE CASCADE, 
    FOREIGN KEY (end_city_id) REFERENCES cities(city_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

ALTER TABLE User_Profiles  
ADD FOREIGN KEY (city_id) REFERENCES Cities(city_id);
