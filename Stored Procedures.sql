DELIMITER //

CREATE PROCEDURE get_available_flights(
    IN from_city VARCHAR(100),
    IN to_city VARCHAR(100),
    IN dep_date DATE,
    IN selected_class VARCHAR(20)
)
BEGIN
    SELECT 
        f.flight_id,
        a.airline_name,
        cs.city_name AS from_city,
        sa.airport_name AS from_airport,
        ce.city_name AS to_city,
        ea.airport_name AS to_airport,
        DATE(f.departure_time) AS departure_date,
        TIME(f.departure_time) AS departure_time,
        TIME(f.arrival_time) AS arrival_time,
        fc.class_type,
        fc.price
    FROM Flights f
    JOIN flights_classes fc ON f.flight_id = fc.flight_id
    JOIN airline a ON f.airline_id = a.airline_id

    JOIN Airports sa ON f.start_airport_code = sa.airport_code
    JOIN City_Airports csa ON sa.airport_code = csa.airport_code
    JOIN Cities cs ON csa.city_id = cs.city_id

    JOIN Airports ea ON f.end_airport_code = ea.airport_code
    JOIN City_Airports cea ON ea.airport_code = cea.airport_code
    JOIN Cities ce ON cea.city_id = ce.city_id

    WHERE cs.city_name = from_city
      AND ce.city_name = to_city
      AND DATE(f.departure_time) = dep_date
      AND fc.class_type = selected_class
    ORDER BY f.departure_time;
END //

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE GetFlightsBySearch(
    IN origin_city VARCHAR(100),
    IN destination_city VARCHAR(100),
    IN departure_date DATE,
    IN flight_class VARCHAR(20)
)
BEGIN
    WITH
    start_city AS (
        SELECT DISTINCT ca.airport_code, c.city_name
        FROM city_airports ca
        JOIN cities c ON ca.city_id = c.city_id
    ),
    end_city AS (
        SELECT DISTINCT ca.airport_code, c.city_name
        FROM city_airports ca
        JOIN cities c ON ca.city_id = c.city_id
    )
    SELECT DISTINCT
        f.flight_id,
        f.airline_id,
        a.airline_name,
        f.departure_time,
        f.arrival_time,
        f.start_airport_code,
        f.end_airport_code,
        sc.city_name AS city_from,
        ec.city_name AS city_to,
        fc.class_type,
        fc.price,
        fc.total_seats,
        fc.seats_remaining
    FROM flights f
    JOIN flights_classes fc ON f.flight_id = fc.flight_id
    JOIN airline a ON f.airline_id = a.airline_id
    JOIN start_city sc ON f.start_airport_code = sc.airport_code
    JOIN end_city ec ON f.end_airport_code = ec.airport_code
    WHERE sc.city_name = origin_city
      AND ec.city_name = destination_city
      AND DATE(f.departure_time) = departure_date
      AND fc.class_type = flight_class
      AND fc.seats_remaining > 0
    ORDER BY f.departure_time;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE GetFlightsLimited (
    IN origin_city VARCHAR(100),
    IN destination_city VARCHAR(100),
    IN flight_date DATE,
    IN class_type VARCHAR(50),
    IN max_results INT
)
BEGIN
    SELECT
        f.flight_id,
        a.airline_name,
        f.departure_time,
        f.arrival_time,
        f.class_type,
        f.price
    FROM flights f
    JOIN airlines a ON f.airline_id = a.airline_id
    JOIN cities c1 ON f.origin_city_id = c1.city_id
    JOIN cities c2 ON f.destination_city_id = c2.city_id
    WHERE c1.city_name = origin_city
      AND c2.city_name = destination_city
      AND f.flight_date = flight_date
      AND f.class_type = class_type
    LIMIT max_results;
END$$

DELIMITER ;

DELIMITER //

CREATE PROCEDURE GetUserRole(
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255)
)
BEGIN
    SELECT role, user_id
    FROM users
    WHERE email = p_email AND password = p_password;
END //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE register_user(
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(100),
    IN p_role ENUM('admin', 'traveler'),
    IN p_full_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_city_name VARCHAR(100)
)
BEGIN
    DECLARE v_city_id INT;

    -- Debug: check city existence
    SELECT city_id INTO v_city_id
    FROM cities
    WHERE city_name = p_city_name
    LIMIT 1;

    IF v_city_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'City not found';
    END IF;

    START TRANSACTION;

    INSERT INTO users (email, password, role)
    VALUES (p_email, p_password, p_role);

    SET @new_user_id = LAST_INSERT_ID();

    INSERT INTO user_profiles (user_id, full_name, phone, city_id)
    VALUES (@new_user_id, p_full_name, p_phone, v_city_id);

    COMMIT;
END //

DELIMITER ;