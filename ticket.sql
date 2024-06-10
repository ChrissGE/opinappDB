DELIMITER //

CREATE TRIGGER trg_insertar_ticket 
BEFORE OF INSERT ON ticket
FOR EACH ROW
BEGIN
    DECLARE points_act INT;
    DECLARE price INT;
    DECLARE current_stock INT;

    SELECT points INTO points_act
    FROM users
    WHERE email = NEW.email;

    SELECT rewards_price, stock INTO price, current_stock
    FROM rewards
    WHERE id_reward = NEW.id_reward AND company_code = NEW.company_code;

    IF points_act >= price AND current_stock > 0 THEN
        UPDATE rewards 
        SET stock = stock - 1 
        WHERE id_reward = NEW.id_reward AND company_code = NEW.company_code;

        UPDATE users 
        SET points = points - price 
        WHERE email = NEW.email;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay suficientes puntos o stock para realizar esta transacción';
    END IF;
END;
//

DELIMITER ;
