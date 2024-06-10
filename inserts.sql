use opinapp
-- Insertar idiomas en la tabla languages
INSERT INTO languages VALUES ('ES'), ('EN');

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

-- Insertar mapeo de textos y recompensas
INSERT INTO mapTextReward (id_reward, id_text)
SELECT r.id_reward, t.id_text
FROM rewards r
JOIN texts t ON r.id_reward NOT IN (SELECT id_reward FROM mapTextReward)
            AND t.id_text NOT IN (SELECT id_text FROM mapTextReward)
            AND t.id_text NOT IN (SELECT id_text FROM mapTextQuestions)
            AND t.id_text NOT IN (SELECT id_text FROM mapTextMenu);

-- Insertar cuestionarios
INSERT INTO questionaries (questionary_name, points_reward, company_code)
VALUES ('Encuesta de Satisfacción Kiabi', 50, 'E73463259'),
       ('Encuesta de Opinión Ginos', 30, 'U31477490');

-- Insertar menú de cuestionarios
INSERT INTO questionaryMenu (id_questionary) VALUES (1), (1), (1), (2), (2), (2), (2);

-- Insertar mapeo de textos y menú de cuestionarios
INSERT INTO mapTextMenu (id_questionaryMenu, id_text)
SELECT qm.id_questionaryMenu, t.id_text
FROM questionaryMenu qm
JOIN texts t ON t.id_text NOT IN (SELECT id_text FROM mapTextReward)
           AND t.id_text NOT IN (SELECT id_text FROM mapTextQuestions)
           AND t.id_text NOT IN (SELECT id_text FROM mapTextMenu);

-- Insertar preguntas
INSERT INTO questions (text, question_type) VALUES
    ('¿Encontraste fácilmente los productos que estabas buscando?', 'Yes and no'),
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

-- Insertar mapeo de textos y preguntas
INSERT INTO mapTextQuestions (id_questions, id_text)
SELECT q.id_questions, t.id_text
FROM questions q
JOIN texts t ON t.id_text NOT IN (SELECT id_text FROM mapTextReward)
           AND t.id_text NOT IN (SELECT id_text FROM mapTextQuestions)
           AND t.id_text NOT IN (SELECT id_text FROM mapTextMenu);

-- Insertar condiciones de pregunta
INSERT INTO question_condition (id_questions, id_questionaryMenu, answer_value, score_value)
SELECT mq.id_questions, qm.id_questionaryMenu, 1, 
    CASE
        WHEN q.text = '¿Encontraste fácilmente los productos que estabas buscando?' THEN 33
        WHEN q.text = '¿Estaba la tienda bien organizada y limpia?' THEN 33
        WHEN q.text = '¿Había una buena disponibilidad de tallas y estilos?' THEN 16
        WHEN q.text = '¿Estabas satisfecho con la rapidez en el proceso de pago?' THEN 18
        WHEN q.text = '¿Estás satisfecho con la calidad de los materiales de la ropa?' THEN 25
        WHEN q.text = '¿Consideras que las tallas son precisas y consistentes?' THEN 25
        WHEN q.text = '¿La ropa que compraste ha mantenido su forma y color después de lavarla?' THEN 25
        WHEN q.text = '¿Estás contento con la variedad de estilos disponibles en la tienda?' THEN 25
        WHEN q.text = '¿Fuiste atendido de manera amable y cortés por el personal?' THEN 75
        WHEN q.text = '¿El personal estuvo disponible para ayudarte cuando lo necesitaste?' THEN 5
        WHEN q.text = '¿El personal pudo responder a tus preguntas sobre los productos?' THEN 10
        WHEN q.text = '¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?' THEN 10
        ELSE 1
    END AS custom_answer_value
FROM questions q
JOIN mapTextQuestions mq ON q.id_questions = mq.id_questions
JOIN questionaryMenu qm ON mq.id_text = qm.id_questionaryMenu;

-- Insertar preguntas de opinión para Ginos
INSERT INTO questions (text, question_type) VALUES 
    ('¿Consideras que la comida estaba fresca y bien preparada durante tu visita?', 'Yes and no'),
    ('¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?', 'Yes and no'),
    ('¿Sentiste que la atmósfera del restaurante era acogedora y agradable?', 'Yes and no'),
    ('¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?', 'Yes and no'),
    ('¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?', 'Yes and no'),
    ('¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?', 'Yes and no'),
    ('¿Hay algún comentario adicional que te gustaría compartir sobre tu experiencia con el servicio del personal en Ginos Restaurante?', 'Text');

-- Insertar mapeo de textos y preguntas de opinión para Ginos
INSERT INTO mapTextQuestions (id_questions, id_text)
SELECT q.id_questions, t.id_text
FROM questions q
JOIN texts t ON t.id_text NOT IN (SELECT id_text FROM mapTextReward)
           AND t.id_text NOT IN (SELECT id_text FROM mapTextQuestions)
           AND t.id_text NOT IN (SELECT id_text FROM mapTextMenu);

-- Insertar condiciones de pregunta para opinión de Ginos
INSERT INTO question_condition (id_questions, id_questionaryMenu, answer_value, score_value)
SELECT mq.id_questions, qm.id_questionaryMenu, 1, 
    CASE
        WHEN q.text = '¿Consideras que la comida estaba fresca y bien preparada durante tu visita?' THEN 50
        WHEN q.text = '¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?' THEN 50
        WHEN q.text = '¿Sentiste que la atmósfera del restaurante era acogedora y agradable?' THEN 30
        WHEN q.text = '¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?' THEN 70
        WHEN q.text = '¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?' THEN 45
        WHEN q.text = '¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?' THEN 55
        ELSE 1
    END AS custom_answer_value
FROM questions q
JOIN mapTextQuestions mq ON q.id_questions = mq.id_questions
JOIN questionaryMenu qm ON mq.id_text = qm.id_questionaryMenu;

-- Insertar nombres de puntuaciones
INSERT INTO scorings (scoring_name, id_questionaryMenu)
SELECT CONCAT('Scoring ', txt.text, ', ', c.company_name), mqm.id_questionaryMenu
FROM questionaryMenu mqm
JOIN mapTextMenu mtm ON mtm.id_questionaryMenu = mqm.id_questionaryMenu
JOIN texts txt ON txt.id_text = mtm.id_text AND id_language = 1
JOIN questionaries q ON q.id_questionary = mqm.id_questionary
JOIN company c ON c.company_code = q.company_code
WHERE (mqm.id_questionaryMenu IN (SELECT id_questionaryMenu FROM question_condition) 
       OR mqm.id_questionaryMenu IN (SELECT id_questionaryMenu FROM mapQuestions WHERE id_questions IN (SELECT id_questions FROM questions WHERE question_type LIKE 'Text')))
  AND CONCAT('Scoring ', txt.text, ', ', c.company_name) NOT IN (SELECT scoring_name FROM scorings);

-- Insertar mapeo de puntuaciones globales
INSERT INTO map_global_scorings (company_code, id_scoring, percentage)
SELECT s.company_code, s.id_scoring, 
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
JOIN questionaryMenu qm ON qm.id_questionaryMenu = s.id_questionaryMenu
JOIN questionaries q ON q.id_questionary = qm.id_questionary
JOIN mapTextMenu mtm ON qm.id_questionaryMenu = mtm.id_questionaryMenu
JOIN texts t ON t.id_text = mtm.id_text AND id_language = 1
WHERE s.company_code NOT IN (SELECT company_code FROM map_global_scorings);
