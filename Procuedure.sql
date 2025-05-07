use db_examv2;

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

    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
    END;

    START TRANSACTION;

    SELECT city_id INTO v_city_id
    FROM Cities
    WHERE city_name = p_city_name
    LIMIT 1;

 
    INSERT INTO Users (email, password, role)
    VALUES (p_email, p_password, p_role);

  
    SET @new_user_id = LAST_INSERT_ID();

   
    INSERT INTO User_Profiles (user_id, full_name, phone, city_id)
    VALUES (@new_user_id, p_full_name, p_phone, v_city_id);

    COMMIT;
END //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE make_booking_from_cart(
    IN p_user_id INT,
    IN p_cart_json JSON 
)
BEGIN
   
    DECLARE new_booking_id INT;

  
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
    END;

    START TRANSACTION;

    -- Insert into Booking table
    INSERT INTO Booking (user_id, booking_date, status)
    VALUES (p_user_id, NOW(), 'confirmed');

    
    SET new_booking_id = LAST_INSERT_ID();

    --  fetch from JSON cart
    INSERT INTO Booking_Details (airline_id, booking_id, item_id, item_type, quantity, price)
    SELECT
        jt.airline_id,
        new_booking_id, 
        jt.item_id,
        jt.item_type,
        jt.quantity,
        jt.price
    FROM JSON_TABLE(
        p_cart_json, 
        "$[*]" COLUMNS (
            airline_id INT PATH "$.airline_id",
            item_id INT PATH "$.item_id",
            item_type VARCHAR(20) PATH "$.item_type",
            quantity INT PATH "$.quantity",
            price FLOAT PATH "$.price"
        )
    ) AS jt;

    COMMIT;
END //

DELIMITER ;
