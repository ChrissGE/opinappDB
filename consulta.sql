SET @language = 'ES';

WITH RECURSIVE TextQuestions AS (
    SELECT 
        mtq.id_questions, 
        qt.id_text, 
        qt.text,
        ROW_NUMBER() OVER (PARTITION BY mtq.id_questions ORDER BY 
            CASE 
                WHEN  @language  THEN CASE WHEN l.name_language = 'ES' THEN 1 ELSE 2 END
                WHEN  @language  THEN CASE WHEN l.name_language = 'EN' THEN 1 ELSE 2 END
                WHEN  @language  THEN CASE WHEN l.name_language = 'PT' THEN 1 ELSE 2 END
                ELSE 2
            END) AS rn
    FROM mapTextQuestions mtq
    LEFT JOIN texts qt ON mtq.id_text = qt.id_text
    LEFT JOIN languages l ON qt.id_language = l.id_language
),
FilteredTextQuestions AS (
    SELECT id_questions, id_text, text
    FROM TextQuestions
    WHERE rn = 1
),
TextMenus AS (
    SELECT 
        mtm.id_questionaryMenu, 
        tm.id_text, 
        tm.text,
        ROW_NUMBER() OVER (PARTITION BY mtm.id_questionaryMenu ORDER BY 
            CASE 
                WHEN  @language  THEN CASE WHEN l.name_language = 'ES' THEN 1 ELSE 2 END
                WHEN  @language  THEN CASE WHEN l.name_language = 'EN' THEN 1 ELSE 2 END
                WHEN  @language  THEN CASE WHEN l.name_language = 'PT' THEN 1 ELSE 2 END
                ELSE 2
            END) AS rn
    FROM mapTextMenu mtm
    LEFT JOIN texts tm ON mtm.id_text = tm.id_text
    LEFT JOIN languages l ON tm.id_language = l.id_language
),
FilteredTextMenus AS (
    SELECT id_questionaryMenu, id_text, text
    FROM TextMenus
    WHERE rn = 1
)
SELECT 
    q.id_questions, 
    COALESCE(ftq.text, qt_default.text) AS question_text, 
    COALESCE(ftm.text, tm_default.text) AS menu_text,
    q.question_type,
    c.company_name
FROM questions q
INNER JOIN mapQuestions mq ON q.id_questions = mq.id_questions
INNER JOIN FilteredTextQuestions ftq ON mq.id_questions = ftq.id_questions
INNER JOIN questionaryMenu qm ON mq.id_questionaryMenu = qm.id_questionaryMenu
INNER JOIN FilteredTextMenus ftm ON qm.id_questionaryMenu = ftm.id_questionaryMenu
LEFT JOIN texts qt_default ON ftq.id_text = qt_default.id_text
LEFT JOIN texts tm_default ON ftm.id_text = tm_default.id_text
INNER JOIN questionaries qn ON qn.id_questionary = qm.id_questionary
INNER JOIN company c ON qn.company_code = c.company_code
WHERE qn.company_code = 'E73463259';
