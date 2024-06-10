use opinapp; 

-- Insertar idiomas en la tabla languages
INSERT INTO languages (name_language) VALUES ('ES'), ('EN');

-- Insertar datos en la tabla 'company'
INSERT INTO company (company_code, company_name, address, coords, email)
VALUES ('E73463259', 'Kiabi', 'CC Parque Oeste, Av. de Europa, s/n, 28925 Alcorcón, Madrid', '40.34834628834263/-3.848079453970466', 'kiabi_parque_oeste@kiabi.com'),
       ('U31477490', 'Ginos', 'Av. de Europa, 7, 28922 Alcorcón, Madrid', '40.348939914250124/-3.8490587962988774', 'ginos_parque_oeste@ginos.com');

-- Insertar datos en la tabla 'rewards'
INSERT INTO rewards (rewards_price, company_code, stock)
VALUES (500, 'E73463259', 20),
       (1000, 'E73463259', 50),
       (2500, 'E73463259', 60),
       (250, 'U31477490', 100),
       (700, 'U31477490', 50),
       (820, 'U31477490', 80);

-- Insertar textos
INSERT INTO texts (id_language, text) VALUES 
(1, '5% de descuento en pedidos inferiores a 100€'),
(1, '10% de descuento en pedidos inferiores a 150€'),
(1, 'Tarjeta regalo 30€'),
(1, 'Una bebida GRATIS'),
(1, 'Descuento de lunes a jueves 10%'),
(1, 'Pizza gratis'),
(2, '5% discount on orders under 100€'),
(2, '10% discount on orders under 150€'),
(2, '30€ gift card'),
(2, 'A FREE drink'),
(2, '10% discount from Monday to Thursday'),
(2, 'Free pizza');

-- Insertar relaciones entre recompensas y textos en la tabla mapTextReward
INSERT INTO mapTextReward (id_reward, id_text)
SELECT r.id_reward, t.id_text
FROM (
    SELECT id_reward, ROW_NUMBER() OVER (ORDER BY id_reward) AS row_num
    FROM rewards
	WHERE id_reward NOT IN (SELECT id_reward FROM mapTextReward)
) r
JOIN (
    SELECT id_text, ROW_NUMBER() OVER (PARTITION BY id_language ORDER BY id_text) AS row_num
	FROM texts
	WHERE id_text NOT IN (SELECT id_text FROM mapTextReward) AND id_text NOT IN (SELECT id_text FROM mapTextQuestions) AND id_text NOT IN (SELECT id_text FROM mapTextMenu)
) t ON r.row_num = t.row_num;

-- Insertar cuestionarios en la tabla questionaries
INSERT INTO questionaries (questionary_name, points_reward, company_code)
VALUES ('Encuesta de Satisfacción Kiabi', 50, 'E73463259'),
       ('Encuesta de Opinión Ginos', 30, 'U31477490');	

-- Insertar relaciones entre cuestionarios y menús en la tabla questionaryMenu
INSERT INTO questionaryMenu (id_questionary)
VALUES (1),
       (1),
       (1),
       (2),
       (2),
       (2),
	   (2);

-- Insertar textos en la tabla texts
INSERT INTO texts (id_language, text) VALUES 
(1, 'Experiencia de Compra'),
(1, 'Calidad de los Productos'),
(1, 'Servicio al Cliente'),
(1, 'Calidad de la Comida'),
(1, 'Experiencia en el Restaurante'),
(1, 'Valor por el Dinero'),
(1, 'Servicio del Personal'),
(2, 'Shopping Experience'),
(2, 'Product Quality'),
(2, 'Customer Service'),
(2, 'Food Quality'),
(2, 'Restaurant Experience'),
(2, 'Value for Money'),
(2, 'Staff Service');

-- Insertar relaciones entre menús de cuestionarios y textos en la tabla mapTextMenu
INSERT INTO mapTextMenu (id_questionaryMenu, id_text)
SELECT qm.id_questionaryMenu, t.id_text
FROM (
    SELECT id_questionaryMenu, ROW_NUMBER() OVER (ORDER BY id_questionaryMenu) AS row_num
    FROM questionaryMenu
	WHERE id_questionaryMenu NOT IN (SELECT id_questionaryMenu FROM mapTextMenu)
) qm
JOIN (
    SELECT id_text, ROW_NUMBER() OVER (PARTITION BY id_language ORDER BY id_text) AS row_num
	FROM texts
	WHERE id_text NOT IN (SELECT id_text FROM mapTextReward) AND id_text NOT IN (SELECT id_text FROM mapTextQuestions) AND id_text NOT IN (SELECT id_text FROM mapTextMenu)
) t ON qm.row_num = t.row_num;

-- Mapear preguntas a un cuestionario (ESTO SE REALIZA INDIVIDUALMENTE PARA CADA CUESTIONARIO)

INSERT INTO questions (text, question_type)
VALUES ('¿Encontraste fácilmente los productos que estabas buscando?', 'Yes and no'),
       ('¿Estaba la tienda bien organizada y limpia?', 'Yes and no'),
       ('¿Había una buena disponibilidad de tallas y estilos?', 'Yes and no'),
       ('¿Estabas satisfecho con la rapidez en el proceso de pago?', 'Yes and no'),
       ('¿Estás satisfecho con la calidad de los materiales de la ropa?', 'Yes and no'),
       ('¿Consideras que las tallas son precisas y consistentes?', 'Yes and no'),
       ('¿La ropa que compraste ha mantenido su forma y color después de lavarla?', 'Yes and no'),
       ('¿Estás contento con la variedad de estilos disponibles en la tienda?', 'Yes and no'),
       ('¿Fuiste atendido de manera amable y cortés por el personal?', 'Yes and no'),
       ('¿El personal estuvo disponible para ayudarte cuando lo necesitaste?', 'Yes and no'),
       ('¿El personal pudo responder a tus preguntas sobre los productos?', 'Yes and no'),
       ('¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?', 'Yes and no');

INSERT INTO texts (id_language, text) VALUES 
(1, '¿Encontraste fácilmente los productos que estabas buscando?'),
(1, '¿Estaba la tienda bien organizada y limpia?'),
(1, '¿Había una buena disponibilidad de tallas y estilos?'),
(1, '¿Estabas satisfecho con la rapidez en el proceso de pago?'),
(1, '¿Estás satisfecho con la calidad de los materiales de la ropa?'),
(1, '¿Consideras que las tallas son precisas y consistentes?'),
(1, '¿La ropa que compraste ha mantenido su forma y color después de lavarla?'),
(1, '¿Estás contento con la variedad de estilos disponibles en la tienda?'),
(1, '¿Fuiste atendido de manera amable y cortés por el personal?'),
(1, '¿El personal estuvo disponible para ayudarte cuando lo necesitaste?'),
(1, '¿El personal pudo responder a tus preguntas sobre los productos?'),
(1, '¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?'),
(2, 'Did you easily find the products you were looking for?'),
(2, 'Was the store well organized and clean?'),
(2, 'Was there good availability of sizes and styles?'),
(2, 'Were you satisfied with the speed of the checkout process?'),
(2, 'Are you satisfied with the quality of the clothing materials?'),
(2, 'Do you consider the sizes to be accurate and consistent?'),
(2, 'Has the clothing you bought maintained its shape and color after washing?'),
(2, 'Are you happy with the variety of styles available in the store?'),
(2, 'Were you attended to in a friendly and courteous manner by the staff?'),
(2, 'Was the staff available to assist you when needed?'),
(2, 'Could the staff answer your questions about the products?'),
(2, 'Are you satisfied with the resolution of any issues or concerns you had?');

INSERT INTO mapTextQuestions (id_questions, id_text)
SELECT q.id_questions, t.id_text
FROM (
    SELECT id_questions, ROW_NUMBER() OVER (ORDER BY id_questions) AS row_num
    FROM questions
	WHERE id_questions NOT IN (SELECT id_questions FROM mapTextQuestions)
) q
JOIN (
    SELECT id_text, ROW_NUMBER() OVER (PARTITION BY id_language ORDER BY id_text) AS row_num
	FROM texts
	WHERE id_text NOT IN (SELECT id_text FROM mapTextReward) AND id_text NOT IN (SELECT id_text FROM mapTextQuestions) AND id_text NOT IN (SELECT id_text FROM mapTextMenu)
) t ON q.row_num = t.row_num;

SET @company_code_cuestionario = 'U31477490'; -- INSERTAR COMPANY CODE

-- COMPROBAR id_questionaryMenu PARA PODER METER LAS PREGUNTAS
SELECT id_questionaryMenu
FROM questionaryMenu
WHERE id_questionary IN (
    SELECT id_questionary
    FROM questionaries
    WHERE company_code = @company_code_cuestionario
);

INSERT INTO mapQuestions (id_questions, id_questionaryMenu)
SELECT q.id_questions, qm.id_questionaryMenu
FROM questions q
JOIN (
    SELECT '¿Encontraste fácilmente los productos que estabas buscando?' AS text, 1 AS id_questionaryMenu
    UNION ALL SELECT '¿Estaba la tienda bien organizada y limpia?', 1
    UNION ALL SELECT '¿Había una buena disponibilidad de tallas y estilos?', 1
    UNION ALL SELECT '¿Estabas satisfecho con la rapidez en el proceso de pago?', 1
    UNION ALL SELECT '¿Estás satisfecho con la calidad de los materiales de la ropa?', 2
    UNION ALL SELECT '¿Consideras que las tallas son precisas y consistentes?', 2
    UNION ALL SELECT '¿La ropa que compraste ha mantenido su forma y color después de lavarla?', 2
    UNION ALL SELECT '¿Estás contento con la variedad de estilos disponibles en la tienda?', 2
    UNION ALL SELECT '¿Fuiste atendido de manera amable y cortés por el personal?', 3
    UNION ALL SELECT '¿El personal estuvo disponible para ayudarte cuando lo necesitaste?', 3
    UNION ALL SELECT '¿El personal pudo responder a tus preguntas sobre los productos?', 3
    UNION ALL SELECT '¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?', 3
) qm ON q.text = qm.text
WHERE qm.id_questionaryMenu IN (
    SELECT id_questionaryMenu
    FROM questionaryMenu
    WHERE id_questionary IN (
        SELECT id_questionary
        FROM questionaries
        WHERE company_code = @company_code_cuestionario
    )
)
ORDER BY id_questions;


INSERT INTO question_condition (id_questions, id_questionaryMenu, answer_value, score_value)
SELECT 
    mq.id_questions, 
    mq.id_questionaryMenu, 
    1 AS answer_value, 
    CASE q.text
        WHEN '¿Encontraste fácilmente los productos que estabas buscando?' THEN 33
        WHEN '¿Estaba la tienda bien organizada y limpia?' THEN 33
        WHEN '¿Había una buena disponibilidad de tallas y estilos?' THEN 16
        WHEN '¿Estabas satisfecho con la rapidez en el proceso de pago?' THEN 18
        WHEN '¿Estás satisfecho con la calidad de los materiales de la ropa?' THEN 25
        WHEN '¿Consideras que las tallas son precisas y consistentes?' THEN 25
        WHEN '¿La ropa que compraste ha mantenido su forma y color después de lavarla?' THEN 25
        WHEN '¿Estás contento con la variedad de estilos disponibles en la tienda?' THEN 25
        WHEN '¿Fuiste atendido de manera amable y cortés por el personal?' THEN 75
        WHEN '¿El personal estuvo disponible para ayudarte cuando lo necesitaste?' THEN 5
        WHEN '¿El personal pudo responder a tus preguntas sobre los productos?' THEN 10
        WHEN '¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?' THEN 10
        ELSE 1
    END AS custom_answer_value
FROM mapQuestions mq
INNER JOIN questions q ON q.id_questions = mq.id_questions AND q.question_type != 'Text'
WHERE mq.id_questionaryMenu NOT IN (SELECT id_questionaryMenu FROM question_condition)
  AND mq.id_questions NOT IN (SELECT id_questions FROM question_condition);

-- Mapear preguntas a un cuestionario (ESTO SE REALIZA INDIVIDUALMENTE PARA CADA CUESTIONARIO)
INSERT INTO questions (text, question_type) VALUES 
('¿Consideras que la comida estaba fresca y bien preparada durante tu visita?', 'Yes and no'),
('¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?', 'Yes and no'),
('¿Sentiste que la atmósfera del restaurante era acogedora y agradable?', 'Yes and no'),
('¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?', 'Yes and no'),
('¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?', 'Yes and no'),
('¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?', 'Yes and no'),
('¿Hay algún comentario adicional que te gustaría compartir sobre tu experiencia con el servicio del personal en Ginos Restaurante?', 'Text');

INSERT INTO texts (id_language, text) VALUES 
(1, '¿Consideras que la comida estaba fresca y bien preparada durante tu visita?'),
(1, '¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?'),
(1, '¿Sentiste que la atmósfera del restaurante era acogedora y agradable?'),
(1, '¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?'),
(1, '¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?'),
(1, '¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?'),
(1, '¿Hay algún comentario adicional que te gustaría compartir sobre tu experiencia con el servicio del personal en Ginos Restaurante?'),
(2, 'Did you find the food fresh and well-prepared during your visit?'),
(2, 'Did you find the ingredients used in the dishes to be of high quality and tasty?'),
(2, 'Did you feel that the atmosphere of the restaurant was cozy and pleasant?'),
(2, 'Did the presentation of the dishes and the overall restaurant decor positively contribute to your experience?'),
(2, 'Did you feel that the price of the dishes was justified by the quality and quantity of food you received?'),
(2, 'Do you consider Ginos’ value for money to be favorable compared to other Italian restaurants in the area?'),
(2, 'Is there any additional feedback you would like to share about your experience with the service of the staff at Ginos Restaurant?');

INSERT INTO mapTextQuestions (id_questions, id_text)
SELECT q.id_questions, t.id_text
FROM (
    SELECT id_questions, ROW_NUMBER() OVER (ORDER BY id_questions) AS row_num
    FROM questions
	WHERE id_questions NOT IN (SELECT id_questions FROM mapTextQuestions)
) q
JOIN (
    SELECT id_text, ROW_NUMBER() OVER (PARTITION BY id_language ORDER BY id_text) AS row_num
	FROM texts
	WHERE id_text NOT IN (SELECT id_text FROM mapTextReward) AND id_text NOT IN (SELECT id_text FROM mapTextQuestions) AND id_text NOT IN (SELECT id_text FROM mapTextMenu)
) t ON q.row_num = t.row_num;

SET @company_code_cuestionario = 'U31477490'; -- INSERTAR COMPANY CODE

-- COMPROBAR id_questionaryMenu PARA PODER METER LAS PREGUNTAS
SELECT id_questionaryMenu
FROM questionaryMenu
WHERE id_questionary IN (
    SELECT id_questionary
    FROM questionaries
    WHERE company_code = @company_code_cuestionario
);

INSERT INTO mapQuestions (id_questions, id_questionaryMenu)
SELECT q.id_questions, qm.id_questionaryMenu
FROM questions q
JOIN (
    SELECT '¿Consideras que la comida estaba fresca y bien preparada durante tu visita?' AS text, 4 AS id_questionaryMenu
    UNION ALL SELECT '¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?', 4
    UNION ALL SELECT '¿Sentiste que la atmósfera del restaurante era acogedora y agradable?', 5
    UNION ALL SELECT '¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?', 5
    UNION ALL SELECT '¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?', 6
    UNION ALL SELECT '¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?', 6
    UNION ALL SELECT '¿Hay algún comentario adicional que te gustaría compartir sobre tu experiencia con el servicio del personal en Ginos Restaurante?', 7
) qm ON q.text = qm.text
WHERE qm.id_questionaryMenu IN (
    SELECT id_questionaryMenu
    FROM questionaryMenu
    WHERE id_questionary IN (
        SELECT id_questionary
        FROM questionaries
        WHERE company_code = @company_code_cuestionario
    )
)
ORDER BY id_questions;

INSERT INTO question_condition (id_questions, id_questionaryMenu, answer_value, score_value)
SELECT 
    mq.id_questions, 
    mq.id_questionaryMenu, 
    1 AS answer_value, 
    CASE q.text
        WHEN '¿Consideras que la comida estaba fresca y bien preparada durante tu visita?' THEN 50
        WHEN '¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?' THEN 50
        WHEN '¿Sentiste que la atmósfera del restaurante era acogedora y agradable?' THEN 30
        WHEN '¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?' THEN 70
        WHEN '¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?' THEN 45
        WHEN '¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?' THEN 55
        ELSE 1
    END AS custom_answer_value
FROM mapQuestions mq
INNER JOIN questions q ON q.id_questions = mq.id_questions AND q.question_type != 'Text'
WHERE mq.id_questionaryMenu NOT IN (SELECT id_questionaryMenu FROM question_condition)
  AND mq.id_questions NOT IN (SELECT id_questions FROM question_condition);

INSERT INTO scorings (scoring_name, id_questionaryMenu)
SELECT CONCAT('Scoring ', txt.text, ', ', c.company_name) AS scoring_name, mqm.id_questionaryMenu
FROM questionaryMenu mqm
INNER JOIN mapTextMenu mtm ON mtm.id_questionaryMenu = mqm.id_questionaryMenu
INNER JOIN texts txt ON mtm.id_text = txt.id_text AND id_language = 1
INNER JOIN questionaries q ON q.id_questionary = mqm.id_questionary
INNER JOIN company c ON c.company_code = q.company_code
WHERE (mqm.id_questionaryMenu IN (SELECT id_questionaryMenu FROM question_condition) 
    OR mqm.id_questionaryMenu IN (SELECT id_questionaryMenu FROM mapQuestions WHERE id_questions IN (SELECT id_questions FROM questions WHERE question_type LIKE 'Text')))
    AND CONCAT('Scoring ', txt.text, ', ', c.company_name) NOT IN (SELECT scoring_name FROM scorings);


INSERT INTO map_global_scorings (company_code, id_scoring, percentage)
SELECT company_code, id_scoring, 
CASE t.text
    WHEN 'Experiencia de Compra' THEN 33.33333
    WHEN 'Calidad de los Productos' THEN 33.33333
    WHEN 'Servicio al Cliente' THEN 33.33333
    WHEN 'Calidad de la Comida' THEN 40
    WHEN 'Experiencia en el Restaurante' THEN 30
    WHEN 'Valor por el Dinero' THEN 20
    WHEN 'Servicio del Personal' THEN 10
    ELSE 1
END AS custom_answer_value
FROM scorings s
INNER JOIN questionaryMenu qm ON qm.id_questionaryMenu = s.id_questionaryMenu
INNER JOIN questionaries q ON q.id_questionary = qm.id_questionary
INNER JOIN mapTextMenu mtm ON qm.id_questionaryMenu = mtm.id_questionaryMenu
INNER JOIN texts t ON t.id_text = mtm.id_text AND id_language = 1
WHERE company_code NOT IN (SELECT company_code FROM map_global_scorings);
