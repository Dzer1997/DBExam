use db_examv2;
DROP PROCEDURE IF EXISTS GetUserRole;
DELIMITER $$

DROP PROCEDURE IF EXISTS GetUserRole$$

CREATE PROCEDURE GetUserRole (
    IN user_email VARCHAR(255),
    IN user_password VARCHAR(255)
)
BEGIN
    SELECT role
    FROM users
    WHERE email = user_email AND password = user_password
    LIMIT 1;
END$$

DELIMITER ;



