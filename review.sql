DELIMITER //

CREATE TRIGGER trg_insertar_review 
AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    DECLARE questionary_points INT;

    SELECT points_reward INTO questionary_points
    FROM questionaries
    WHERE id_questionary = NEW.id_questionary;

    UPDATE users 
    SET points = points + questionary_points
    WHERE email = NEW.email;
END;
//

DELIMITER ;
