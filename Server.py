
from flask import Flask, request, jsonify, send_file
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,sent_tokenize
nltk.download('stopwords')
nltk.download('universal_tagset')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')
nltk.download('punkt')
import io
import json
import mysql.connector

spanish_sw = set(stopwords.words('spanish'))

with open("lexico", "r") as archivo:
    lexicon_personalizado = json.load(archivo)
    
sia = SentimentIntensityAnalyzer()

sia.lexicon.update(lexicon_personalizado)
app = Flask(__name__)


#server = '(localdb)\localhostAdrian'

# Configura los parámetros de conexión
config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',  # Solo especifica el host aquí
  'port': 3306,  # Especifica el puerto por separado
  'database': 'opinapp',
  'raise_on_warnings': True
}


# Conecta a la base de datos
 

def create_connection():
    try:
        conn = mysql.connector.connect(**config)
        print("Conexión exitosa")
        return conn
    except Exception as e:
        print("Error al conectar:", e)
        return None



@app.route('/test', methods=['GET'])
def test():
    conc = create_connection()
    
    return {'respuesta':'HELLO WORLD!'}

@app.route('/getUser', methods=['POST'])
def getUser():
    try:
        conn = create_connection()
        resultado = None
        datos = request.json
        email = datos.get("email")
        cursor = conn.cursor()
        query = """ select email,username, points 
                    from users
                    where email = %s;
                    """
        cursor.execute(query,email)
        row = cursor.fetchone()
        if row is None:
            resultado = jsonify({'email': 'NOK'}), 200
        else:
            resultado =  {'username':row.username,
                            'email':row.email,
                            'points':row.points}
            resultado = jsonify(resultado), 200
        return resultado
    finally:
        cursor.close()
        conn.close()

@app.route('/setUser', methods=['POST'])
def setUser():
    try:
        conn = create_connection()
        datos = request.json
        cursor = conn.cursor()
        
        email=datos.get('email')
        username = datos.get('username')
        genero = datos.get('gender')
        fecha = datos.get('birth_date')
        print(fecha,username,genero)
        insert = """insert into users (email,username,gender,birth_date,points) values (%s,%s,%s,%s,%s)"""
        cursor.execute(insert,(email,username,genero,fecha,0))
        conn.commit()
        return {'message': 'OK'}, 200
    finally:
        cursor.close()
        conn.close()

#TODO: seguro se puede modularizar
@app.route('/getScores',methods=['POST'])
def get_scores():
    try:
        conn = create_connection()
        datos = request.json
        company_code = datos.get("company_code")
        cursor = conn.cursor()
        query = """ SELECT s.scoring_name, smp.mark
                    FROM scorings s 
                    JOIN scoring_per_map_review smp ON s.id_questionaryMenu = smp.id_questionaryMenu
                    JOIN questionaryMenu mp ON smp.id_questionaryMenu = mp.id_questionaryMenu
                    JOIN questionaries q ON mp.id_questionary = q.id_questionary
                    WHERE q.company_code = %s;
                    """
        cursor.execute(query,company_code)
        rows = cursor.fetchall()
        results = [
            {description[0]: row[i] for i, description in enumerate(cursor.description)}for row in rows
        ]
        return jsonify(results)
    finally:
        cursor.close()              
        conn.close()
        
# @app.route("/getTopReviews", methods=["POST"])
# def getTopReviews():
#     try:
#         conn = create_connection()
#         datos = request.json
#         email = datos.get("email")
#         cursor = conn.cursor()
#         query = """ select TOP(3) FORMAT(r.insert_date, 'dd/MM/yyyy') AS insert_date, q.company_code, q.points_reward
#                     from reviews r 
#                     inner join questionaries q on r.id_questionary=q.id_questionary 
#                     left join company c on q.company_code = c.company_code 
#                     where r.email = ?
#                     order by r.insert_date desc
#                     """
#         cursor.execute(query,email)
#         rows = cursor.fetchall()
#         results = [
#             {
#                 'insert_date': row[0],
#                 'company_code': row[1],
#                 'points_reward': row[2]
#             } 
#             for row in rows
#         ]
#         return jsonify(results)
#     finally:
#         cursor.close()
#         conn.close()
                    
@app.route('/getReviews',methods=['POST'])
def get_reviews():
    try:
        conn = create_connection()
        datos = request.json
        print(datos)
        email = datos.get("email")
        cursor = conn.cursor()
        query = """SELECT DATE_FORMAT(r.insert_date, '%d/%m/%Y') AS insert_date, c.company_name, q.points_reward
                    FROM reviews r
                    JOIN questionaries q ON r.id_questionary = q.id_questionary
                    JOIN company c ON q.company_code = c.company_code 
                    WHERE r.email = %s
                    ORDER BY r.insert_date DESC
                    """
        cursor.execute(query,(email,))
        rows = cursor.fetchall()
        results = [
            {
                'insert_date': row[0],
                'company_name': row[1],
                'points_reward': row[2],
            } 
            for row in rows
        ]
        return jsonify(results)
    finally:
        cursor.close()
        conn.close()
        
@app.route('/getCompanies', methods=['POST'])
def getCompanies():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = """ WITH ranked_scores AS (
                        SELECT  
                            c.company_name, 
                            c.company_code, 
                            c.address, 
                            c.coords, 
                            COALESCE(gsv.mark, -1.00) AS mark, 
                            ROW_NUMBER() OVER (PARTITION BY c.company_code ORDER BY gsv.mark DESC) AS row_num
                        FROM 
                            company c
                        LEFT JOIN 
                            global_scorings_value gsv 
                        ON 
                            gsv.company_code = c.company_code
                    )
                    SELECT 
                        company_name, 
                        company_code, 
                        address, 
                        coords, 
                        mark
                    FROM 
                        ranked_scores
                    WHERE 
                        row_num = 1;

                    """
        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = {
                "company_code": row[1],
                "company_name": row[0],
                "address": row[2],
                "coords": row[3],
                "mark": float(row[4]) if row[4] is not None else None
            }
            results.append(result)

        return jsonify(results)
    finally:
        cursor.close()
        conn.close()
@app.route('/getProducts', methods=['POST'])
def get_products():
    try:
        datos = request.json
        conn = create_connection()
        cursor = conn.cursor()
        name_language = datos.get('name_language')
        if name_language.lower()=='español':
            language_code='ES'
        else:
            language_code='EN'
        query = """ select r.id_reward,r.company_code,t.text, r.rewards_price
                    from rewards r
                    JOIN mapTextReward mt on mt.id_reward = r.id_reward
                    JOIN texts t on t.id_text = mt.id_text
                    JOIN languages i on t.id_language = i.id_language
                    where i.name_language = %s
                    """
        cursor.execute(query, [language_code])
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = {
                'id_reward': row[0],
                'company_code': row[1],
                'text': row[2],
                'rewards_price': row[3]
            }
            results.append(result)

        return jsonify(results)
    finally:
        cursor.close()
        conn.close()

@app.route('/getImage', methods=['POST'])
def get_image():
    try: 
        datos = request.json
        id_image = datos.get('id_image')
        tipo = datos.get('tipo')
        conn = create_connection()
        cursor = conn.cursor()
        if tipo == 'producto':
            query = "SELECT image_reward FROM rewards WHERE id_reward = %s"

        elif tipo == 'company':
            query = "SELECT image_company FROM company WHERE company_code = %s"
            
        cursor.execute(query, (id_image,))
        row = cursor.fetchone()
        if row and row[0]:
            # Convertir varbinary a bytes
            imagen_bytes = bytes(row[0])
            # Crear un stream de bytes
            imagen_stream = io.BytesIO(imagen_bytes)
            return send_file(imagen_stream, mimetype='image/jpg') 
        else:
            return "Imagen no encontrada", 404
    finally:
        cursor.close()
        conn.close()



@app.route('/getQuestionary',methods=['POST'])
def getQuestionary():
    if request.method == 'POST':
        conn = create_connection()
        datos = request.json
        company_code = datos.get('company_code')
        name_language=datos.get('name_language')

        if name_language.lower()=='español':
            if company_code =="U31477490":
                results = [
                                {
                                    "id_questions": 13,
                                    "question_text": "¿Consideras que la comida estaba fresca y bien preparada durante tu visita?",
                                    "menu_text": "Calidad de la Comida",
                                    "question_type": "Yes and no",
                                    "company_name": "Ginos"
                                },
                                {
                                    "id_questions": 14,
                                    "question_text": "¿Te pareció que los ingredientes utilizados en los platos eran de alta calidad y sabrosos?",
                                    "menu_text": "Calidad de la Comida",
                                    "question_type": "Yes and no",
                                    "company_name": "Ginos"
                                },
                                {
                                    "id_questions": 15,
                                    "question_text": "¿Sentiste que la atmósfera del restaurante era acogedora y agradable?",
                                    "menu_text": "Experiencia en el Restaurante",
                                    "question_type": "Yes and no",
                                    "company_name": "Ginos"
                                },
                                {
                                    "id_questions": 16,
                                    "question_text": "¿La presentación de los platos y la decoración general del restaurante contribuyeron positivamente a tu experiencia?",
                                    "menu_text": "Experiencia en el Restaurante",
                                    "question_type": "Yes and no",
                                    "company_name": "Ginos"
                                },
                                {
                                    "id_questions": 17,
                                    "question_text": "¿Crees que el precio de los platos estaba justificado por la calidad y cantidad de comida que recibiste?",
                                    "menu_text": "Valor por el Dinero",
                                    "question_type": "Yes and no",
                                    "company_name": "Ginos"
                                },
                                {
                                    "id_questions": 18,
                                    "question_text": "¿Consideras que la relación calidad-precio en Ginos es favorable comparada con otros restaurantes de comida italiana en la zona?",
                                    "menu_text": "Valor por el Dinero",
                                    "question_type": "Yes and no",
                                    "company_name": "Ginos"
                                },
                                {
                                    "id_questions": 19,
                                    "question_text": "¿Hay algún comentario adicional que te gustaría compartir sobre tu experiencia con el servicio del personal en Ginos Restaurante?",
                                    "menu_text": "Servicio del Personal",
                                    "question_type": "Text",
                                    "company_name": "Ginos"
                                }
                            ]
            elif company_code =="E73463259":
                language_code='ES'

                results=[
                        {
                            "id_questions": 1,
                            "question_text": "¿Encontraste fácilmente los productos que estabas buscando?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 2,
                            "question_text": "¿Estaba la tienda bien organizada y limpia?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 3,
                            "question_text": "¿Había una buena disponibilidad de tallas y estilos?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 4,
                            "question_text": "¿Estabas satisfecho con la rapidez en el proceso de pago?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 5,
                            "question_text": "¿Estás satisfecho con la calidad de los materiales de la ropa?",
                            "menu_text": "Calidad de los Productos",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 6,
                            "question_text": "¿Consideras que las tallas son precisas y consistentes?",
                            "menu_text": "Calidad de los Productos",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 7,
                            "question_text": "¿La ropa que compraste ha mantenido su forma y color después de lavarla?",
                            "menu_text": "Calidad de los Productos",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 8,
                            "question_text": "¿Estás contento con la variedad de estilos disponibles en la tienda?",
                            "menu_text": "Calidad de los Productos",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 9,
                            "question_text": "¿Fuiste atendido de manera amable y cortés por el personal?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 10,
                            "question_text": "¿El personal estuvo disponible para ayudarte cuando lo necesitaste?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 11,
                            "question_text": "¿El personal pudo responder a tus preguntas sobre los productos?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 12,
                            "question_text": "¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        }
                    ]

        else:
            language_code='EN'

            if company_code == "U31477490":
                
                results =[
                        {
                            "id_questions": 13,
                            "question_text": "Did you find the food fresh and well-prepared during your visit?",
                            "menu_text": "Food Quality",
                            "question_type": "Yes and no",
                            "company_name": "Ginos"
                        },
                        {
                            "id_questions": 14,
                            "question_text": "Did you find the ingredients used in the dishes to be of high quality and tasty?",
                            "menu_text": "Food Quality",
                            "question_type": "Yes and no",
                            "company_name": "Ginos"
                        },
                        {
                            "id_questions": 15,
                            "question_text": "Did you feel that the atmosphere of the restaurant was cozy and pleasant?",
                            "menu_text": "Restaurant Experience",
                            "question_type": "Yes and no",
                            "company_name": "Ginos"
                        },
                        {
                            "id_questions": 16,
                            "question_text": "Did the presentation of the dishes and the overall restaurant decor positively contribute to your experience?",
                            "menu_text": "Restaurant Experience",
                            "question_type": "Yes and no",
                            "company_name": "Ginos"
                        },
                        {
                            "id_questions": 17,
                            "question_text": "Did you feel that the price of the dishes was justified by the quality and quantity of food you received?",
                            "menu_text": "Value for Money",
                            "question_type": "Yes and no",
                            "company_name": "Ginos"
                        },
                        {
                            "id_questions": 18,
                            "question_text": "Do you consider Ginos’ value for money to be favorable compared to other Italian restaurants in the area?",
                            "menu_text": "Value for Money",
                            "question_type": "Yes and no",
                            "company_name": "Ginos"
                        },
                        {
                            "id_questions": 19,
                            "question_text": "Is there any additional feedback you would like to share about your experience with the service of the staff at Ginos Restaurant?",
                            "menu_text": "Staff Service",
                            "question_type": "Text",
                            "company_name": "Ginos"
                        }
                    ]

            elif company_code =="E73463259":
                results=[
                        {
                            "id_questions": 1,
                            "question_text": "Did you easily find the products you were looking for?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 2,
                            "question_text": "¿Estaba la tienda bien organizada y limpia?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 3,
                            "question_text": "Was there good availability of sizes and styles?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 4,
                            "question_text": "¿Estabas satisfecho con la rapidez en el proceso de pago?",
                            "menu_text": "Experiencia de Compra",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 5,
                            "question_text": "Are you satisfied with the quality of the clothing materials?",
                            "menu_text": "Product Quality",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 6,
                            "question_text": "¿Consideras que las tallas son precisas y consistentes?",
                            "menu_text": "Product Quality",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 7,
                            "question_text": "Has the clothing you bought maintained its shape and color after washing?",
                            "menu_text": "Product Quality",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 8,
                            "question_text": "¿Estás contento con la variedad de estilos disponibles en la tienda?",
                            "menu_text": "Product Quality",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 9,
                            "question_text": "Were you attended to in a friendly and courteous manner by the staff?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 10,
                            "question_text": "¿El personal estuvo disponible para ayudarte cuando lo necesitaste?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 11,
                            "question_text": "Could the staff answer your questions about the products?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        },
                        {
                            "id_questions": 12,
                            "question_text": "¿Estás satisfecho con la resolución de cualquier problema o inquietud que tuviste?",
                            "menu_text": "Servicio al Cliente",
                            "question_type": "Yes and no",
                            "company_name": "Kiabi"
                        }
                    ]

                

        cursor = conn.cursor()
        try:
            sql_query = f"""
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
            """
            # cursor.execute(sql_query)
            # print(name_language,company_code)
            # rows = cursor.fetchall()
            # print(rows)
            # if not rows:
            #     return jsonify({"error": sql_query}), 500
            # results = [
            #     {description[0]: row[i] for i, description in enumerate(cursor.description)}for row in rows
            # ]
          
            return results, 200
 
        finally:
            cursor.close()
            conn.close()

    else:
        return jsonify({"error": "Método no permitido"}), 405

def calculate_score_perReview(idReview):
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql_query = """
            select *
            from question_condition qc
            inner join answer a on a.id_questions=qc.id_questions and a.id_questionaryMenu=qc.id_questionaryMenu
            where id_review = %s
        """
        cursor.execute(sql_query, idReview)
        rows = cursor.fetchall()
        scores_mapQuestionary = {}
        for row in rows:
            if row.answer_value==row.binary_answer:
                if row.id_questionaryMenu in scores_mapQuestionary:
                    scores_mapQuestionary[row.id_questionaryMenu]+=row.score_value
                else:
                    scores_mapQuestionary[row.id_questionaryMenu]=row.score_value
            else:
                if row.id_questionaryMenu in scores_mapQuestionary:
                    scores_mapQuestionary[row.id_questionaryMenu]+=0
                else:
                    scores_mapQuestionary[row.id_questionaryMenu]=0
        for id_mapQuestionary, score in scores_mapQuestionary.items():
            insert = """insert into scoring_per_map_review(id_review,id_questionaryMenu,mark) values(%s,%s,%s)"""
            cursor.execute(insert,(idReview,id_mapQuestionary,score))
        conn.commit()
        return scores_mapQuestionary       
    finally:
        
        cursor.close()
        conn.close()
        
def analizarTexto(texto):
    texto_filtrado = []
    palabras = word_tokenize(texto)
    texto_nuevo = ""
    for palabra in palabras:
        if palabra not in spanish_sw:
            texto_nuevo += palabra + " "
    
    score_texto=sia.polarity_scores(texto)
    return 100 * (1 + score_texto['compound']) / 2

   
@app.route('/setReview', methods=['POST'])
def setReview():
    try:
        conn = create_connection()
        datos = request.json
        cursor = conn.cursor(dictionary=True)
        
        company_code = datos.get("company_code")
        email = datos.get("email")
        
        # Obtener id_questionary y points_reward
        id_questionary_query = """SELECT id_questionary, points_reward FROM questionaries WHERE company_code = %s"""
        cursor.execute(id_questionary_query, (company_code,))
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({"error": "Company code not found"}), 400
        
        id_questionary = rows[0]['id_questionary']
        points_reward = rows[0]['points_reward']
        
        # Insertar la review
        insert_review = """INSERT INTO reviews (id_questionary, email) VALUES (%s, %s)"""
        cursor.execute(insert_review, (id_questionary, email))
        
        # Obtener el id_review recién insertado
        id_review_query = """SELECT id_review FROM reviews WHERE id_review = (SELECT MAX(id_review) FROM reviews)"""
        cursor.execute(id_review_query)
        rows = cursor.fetchall()
        id_review = rows[0]['id_review']
        
        preguntas = datos.get("questions", [])
        
        for question in preguntas:
            id_pregunta = question.get("id_question")
            respuesta = question.get("respuesta")
            
            id_questionaryMenu_query = """
                SELECT qm.id_questionaryMenu, qs.question_type 
                FROM mapQuestions mq
                INNER JOIN questions qs ON qs.id_questions = mq.id_questions
                INNER JOIN questionaryMenu qm ON qm.id_questionaryMenu = mq.id_questionaryMenu
                INNER JOIN questionaries q ON q.id_questionary = qm.id_questionary
                WHERE mq.id_questions = %s AND qm.id_questionary = %s
            """
            cursor.execute(id_questionaryMenu_query, (id_pregunta, id_questionary))
            rows = cursor.fetchall()
            
            if rows:
                id_questionaryMenu = rows[0]['id_questionaryMenu']
                question_type = rows[0]['question_type']
                
                if question_type == 'Yes and no':
                    insert_answer = """INSERT INTO answer (id_questions, id_questionaryMenu, id_review, binary_answer) VALUES (%s, %s, %s, %s)"""
                else:
                    insert_answer = """INSERT INTO answer (id_questions, id_questionaryMenu, id_review, text) VALUES (%s, %s, %s, %s)"""
                    score = analizarTexto(respuesta)
                    insert_score = """INSERT INTO scoring_per_map_review (id_review, id_questionaryMenu, mark) VALUES (%s, %s, %s)"""
                    cursor.execute(insert_score, (id_review, id_questionaryMenu, score))
                
                cursor.execute(insert_answer, (id_pregunta, id_questionaryMenu, id_review, respuesta))
        
        # Insertar en la tabla traces si no existe
        insert_traces = """
            INSERT INTO traces (company_code)
            SELECT %s
            WHERE NOT EXISTS (SELECT 1 FROM traces WHERE company_code = %s)
        """
        cursor.execute(insert_traces, (company_code, company_code))
        
        conn.commit()
        #calculate_score_perReview(id_review)
        return jsonify({"message": "Review creada exitosamente", "points_reward": points_reward})
    
    finally:
        cursor.close()
        conn.close()
        
# @app.route('/getImagen', methods=['POST'])
# def getImagen():
#     datos = request.json
#     ruta_imagen = 'companies-logo/'+datos.get("imagen")
#     return send_file(ruta_imagen, mimetype='image/jpeg')

@app.route('/setTicket',methods=['POST'])
def setTicket():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        data=request.json
        rewards_id=data.get('rewards_id')
        email=data.get('email')
        print(email)
        insert='insert into ticket(id_reward,email) values(%s,%s)'
        cursor.execute(insert,(rewards_id,email))
        conn.commit()
        return {'Response':'OK'}
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)