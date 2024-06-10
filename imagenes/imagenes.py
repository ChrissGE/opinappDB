from PIL import Image
import io
import mysql.connector

config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',  # Solo especifica el host aquí
  'port': 3306,  # Especifica el puerto por separado
  'database': 'opinapp',
  'raise_on_warnings': True
}
def create_connection():
    try:
        conn = mysql.connector.connect(**config)
        print("Conexión exitosa")
        return conn
    except Exception as e:
        print("Error al conectar:", e)
        return None
        
def toVarBinary(image_path, id, image_type, query):
    conn = create_connection()
    if conn is None:
        return

    # Carga la imagen
    image = Image.open(image_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convierte la imagen a bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image_type)  # Cambia 'JPEG' al formato de tu imagen si es diferente
    image_bytes = image_bytes.getvalue()
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (image_bytes, id))
        conn.commit()
    except mysql.Error as e:
        print("Error al ejecutar la consulta:", e)
    finally:
        # Cierra la conexión
        cursor.close()
        conn.close()

toVarBinary(r'./star.png','1','png',"UPDATE rewards SET image_reward=%s WHERE id_reward=%s")
toVarBinary(r'./star.png','2','png',"UPDATE rewards SET image_reward=%s WHERE id_reward=%s")
toVarBinary(r'./star.png','3','png',"UPDATE rewards SET image_reward=%s WHERE id_reward=%s")
toVarBinary(r'./star.png','4','png',"UPDATE rewards SET image_reward=%s WHERE id_reward=%s")
toVarBinary(r'./star.png','5','png',"UPDATE rewards SET image_reward=%s WHERE id_reward=%s")
toVarBinary(r'./star.png','6','png',"UPDATE rewards SET image_reward=%s WHERE id_reward=%s")

toVarBinary(r'./star.png','E73463259','png',"UPDATE company SET image_company=%s WHERE company_code=%s")
toVarBinary(r'./star.png','U31477490','png',"UPDATE company SET image_company=%s WHERE company_code=%s")
