import base64
import pandas as pd
import pyodbc as odbc
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
import datetime
import io
import json

spanish_sw = set(stopwords.words('spanish'))

with open("lexico", "r") as archivo:
    lexicon_personalizado = json.load(archivo)
    
sia = SentimentIntensityAnalyzer()

sia.lexicon.update(lexicon_personalizado)
app = Flask(__name__)


#server = '(localdb)\localhostAdrian'
server = '(localdb)\opinapp'
database = 'OpinAppDB'

 

def create_connection():
    try:
        conn = odbc.connect(Trusted_Connection='Yes',Driver='{ODBC Driver 17 for SQL Server}',Server=server,Database=database)
        print("Conexión exitosa")
        return conn
    except Exception as e:
        print("Error al conectar:", e)
        return None



@app.route('/test', methods=['GET'])
def test():
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
                    where email = ?;
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
        insert = """insert into users (email,username,gender,birth_date,points) values (?,?,?,?,?)"""
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
        query = """ select scoring_name,mark 
                    from scorings s 
                    join scoring_per_map_review smp on s.id_questionaryMenu = smp.id_questionaryMenu
                    join questionaryMenu mp on smp.id_questionaryMenu = mp.id_questionaryMenu
                    join questionaries q on mp.id_questionary = q.id_questionary
                    where q.company_code = ?
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
        query = """ select FORMAT(r.insert_date, 'dd/MM/yyyy') AS insert_date, c.company_name, q.points_reward
                    from reviews r join questionaries q on r.id_questionary=r.id_questionary
                    join company c on q.company_code = c.company_code 
                    where r.email = ?
                    order by r.insert_date desc
                    """
        cursor.execute(query,email)
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
                        SELECT  c.company_name, c.company_code,c.address,c.coords,coalesce(gsv.mark, -1.00) as mark, ROW_NUMBER() OVER (PARTITION BY c.company_code ORDER BY gsv.id_global_scoring_value DESC) AS rank
                        FROM company c
                        LEFT JOIN global_scorings_value gsv ON gsv.company_code = c.company_code
                    )
                    SELECT company_name,company_code,address,coords,mark
                    FROM ranked_scores
                    WHERE rank = 1;
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
                    where i.name_language = ?
                    """
        cursor.execute(query, language_code)
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
            query = "SELECT image_reward FROM rewards WHERE id_reward = ?"

        elif tipo == 'company':
            query = "SELECT image_company FROM company WHERE company_code = ?"
            
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
            language_code='ES'
        else:
            language_code='EN'

        cursor = conn.cursor()
        try:
            sql_query = """
                DECLARE @language VARCHAR(50) = ?;

                WITH TextQuestions AS (
                    SELECT 
                        mtq.id_questions, 
                        qt.id_text, 
                        qt.text,
                        ROW_NUMBER() OVER (PARTITION BY mtq.id_questions ORDER BY CASE @language 
                            WHEN 'ES' THEN (CASE qt.id_language WHEN (SELECT id_language FROM languages WHERE name_language = 'ES') THEN 1 ELSE 2 END)
                            WHEN 'EN' THEN (CASE qt.id_language WHEN (SELECT id_language FROM languages WHERE name_language = 'EN') THEN 1 ELSE 2 END)
                            WHEN 'PT' THEN (CASE qt.id_language WHEN (SELECT id_language FROM languages WHERE name_language = 'PT') THEN 1 ELSE 2 END)
                            ELSE 2
                        END) AS rn
                    FROM mapTextQuestions mtq
                    LEFT JOIN texts qt ON mtq.id_text = qt.id_text
                )
                , FilteredTextQuestions AS (
                    SELECT id_questions, id_text, text
                    FROM TextQuestions
                    WHERE rn = 1
                )
                , TextMenus AS (
                    SELECT 
                        mtm.id_questionaryMenu, 
                        tm.id_text, 
                        tm.text,
                        ROW_NUMBER() OVER (PARTITION BY mtm.id_questionaryMenu ORDER BY CASE @language 
                            WHEN 'ES' THEN (CASE tm.id_language WHEN (SELECT id_language FROM languages WHERE name_language = 'ES') THEN 1 ELSE 2 END)
                            WHEN 'EN' THEN (CASE tm.id_language WHEN (SELECT id_language FROM languages WHERE name_language = 'EN') THEN 1 ELSE 2 END)
                            WHEN 'PT' THEN (CASE tm.id_language WHEN (SELECT id_language FROM languages WHERE name_language = 'PT') THEN 1 ELSE 2 END)
                            ELSE 2
                        END) AS rn
                    FROM mapTextMenu mtm
                    LEFT JOIN texts tm ON mtm.id_text = tm.id_text
                )
                , FilteredTextMenus AS (
                    SELECT id_questionaryMenu, id_text, text
                    FROM TextMenus
                    WHERE rn = 1
                )
                SELECT 
                    q.id_questions, 
                    COALESCE(ftq.text, qt_default.text) as question_text, 
                    COALESCE(ftm.text, tm_default.text) as menu_text,
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
                WHERE qn.company_code = ?;
            """
            cursor.execute(sql_query, (language_code,company_code))
            rows = cursor.fetchall()
            print(rows)
            if not rows:
                return jsonify({"error": "No se encontraron registros para el email proporcionado"}), 500
            results = [
                {description[0]: row[i] for i, description in enumerate(cursor.description)}for row in rows
            ]
          
            return jsonify(results)
 
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
            where id_review = ?
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
            insert = """insert into scoring_per_map_review(id_review,id_questionaryMenu,mark) values(?,?,?)"""
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
        cursor = conn.cursor()
        
        company_code = datos.get("company_code")

        id_questionary_query = """select id_questionary,points_reward from questionaries where company_code= ? """
        cursor.execute(id_questionary_query,company_code)
        rows = cursor.fetchall()
        id_questionary=rows[0].id_questionary
        points_reward=rows[0].points_reward

        email = datos.get("email")
        
        insert = """
        insert into reviews (id_questionary,email) values (?,?)
        """
        cursor.execute(insert,(id_questionary,email))
        
        id_review_query = """select id_review from reviews where id_review =  (select max(id_review) from reviews)"""
        cursor.execute(id_review_query)
        rows = cursor.fetchall()
        id_review=rows[0].id_review

        preguntas = datos.get("questions",[])
        
        for question in preguntas:
            id_pregunta = question.get("id_question")
            print(id_pregunta)
            id_questionaryMenu_query="""
                                        select * 
                                        from mapQuestions mq
                                        inner join questions qs on qs.id_questions=mq.id_questions
                                        inner join questionaryMenu qm on qm.id_questionaryMenu=mq.id_questionaryMenu
                                        inner join questionaries q on q.id_questionary=qm.id_questionary
                                        where mq.id_questions=? and qm.id_questionary=?
                                    """
            cursor.execute(id_questionaryMenu_query,(id_pregunta,id_questionary))
            rows = cursor.fetchall()
            if rows:
                id_questionaryMenu=rows[0].id_questionaryMenu
                print(id_questionaryMenu)
                respuesta = question.get("respuesta")
                type=rows[0].question_type
                if type=='Yes and no':
                    insert = """insert into answer (id_questions,id_questionaryMenu,id_review,binary_answer) values (?,?,?,?)"""
                else:
                    insert = """insert into answer (id_questions,id_questionaryMenu,id_review,text) values (?,?,?,?)"""
                    score = analizarTexto(respuesta)
                    insert_score = """insert into scoring_per_map_review(id_review,id_questionaryMenu,mark) values(?,?,?)"""
                    cursor.execute(insert_score,(id_review,id_questionaryMenu,score)) 
                    print(insert)
                cursor.execute(insert,(id_pregunta,id_questionaryMenu,id_review,respuesta))
        
        insert_traces= """if not exists (select 1 from traces where company_code like ?)
                            begin 
                            insert into traces values(?);
                            end"""
        cursor.execute(insert_traces,(company_code,company_code))
        
        conn.commit()
        calculate_score_perReview(id_review)
        return jsonify({"message": "review creada exitosamente","points_reward":points_reward})
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
        insert='insert into ticket(id_reward,email) values(?,?)'
        cursor.execute(insert,(rewards_id,email))
        conn.commit()
        return {'Response':'OK'}
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)