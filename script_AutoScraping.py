import mysql.connector
from scraping_tools.scraping import ejecutar_scraping  # Función que llamará al script de scraping
from scraping_tools.scraping import guardar_comentarios_en_db  # tu función que guarda los datos

# 1. Conectarse a la base donde están los URLs
conexion_fuente = mysql.connector.connect(
    host='rimgsa.com',
    port=3306,
    user='Facebook_user',
    password='user_facebook123',
    database='practicas_facebook_scrapper'
)
cursor_fuente = conexion_fuente.cursor(dictionary=True)

# 2. Obtener los posts del día actual
cursor_fuente.execute("""
    SELECT URL_Post, Nombre_Pagina
    FROM clientes_facebook
    WHERE STR_TO_DATE(Fecha, '%d-%m-%Y') = CURDATE();
""")
posts = cursor_fuente.fetchall()
print(f"Se encontraron {len(posts)} publicaciones para procesar.")
cursor_fuente.close()
conexion_fuente.close()

# 3. Para cada publicación, ejecutar scraping y guardar
for post in posts:
    url = post["URL_Post"]
    nombre_pagina = post["Nombre_Pagina"]
    print(f"Procesando: {url} de {nombre_pagina}")

    try:
        comentarios = ejecutar_scraping(url)
        if comentarios:
            guardar_comentarios_en_db(comentarios, url, nombre_pagina)  # función modificada
    except Exception as e:
        print(f"Error en {url}: {e}")
