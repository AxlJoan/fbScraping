from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import os
import random
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Conectar a la base de datos fb_scrap y guardar comentarios
def guardar_comentarios_en_db(comentarios, post_url, nombre_pagina):
    try:
        conexion = mysql.connector.connect(
            host='158.69.26.160',
            user='admin',
            password='S3gur1d4d2025',
            database='fb_scrap'
        )
        cursor = conexion.cursor()

        query = """
            INSERT IGNORE INTO comentarios 
            (post_url, usuario, comentario, fecha, usuario_url, nombre_pagina)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        datos = []
        for c in comentarios:
            datos.append((
                post_url,
                c["nombre"],
                c["texto"],
                datetime.now(),
                c["perfil"],
                nombre_pagina
            ))
        cursor.executemany(query, datos)
        conexion.commit()
        print(f"{cursor.rowcount} comentarios insertados.")
    except Exception as e:
        print(f"Error al insertar comentarios: {e}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def ejecutar_scraping(url_publicacion):
    comentarios_extraidos = []
    
    # Crear una ruta absoluta para guardar los archivos
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_excel = os.path.join(directorio_actual, 'comentarios_facebook.xlsx')
    ruta_csv = os.path.join(directorio_actual, 'comentarios_facebook.csv')
    ruta_screenshot = os.path.join(directorio_actual, 'facebook_scraping_comentarios.png')

    print(f"Los archivos se guardarán en: {directorio_actual}")
    
    # Configuración de Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get("https://www.facebook.com/")

    try:
        print("Iniciando el proceso de scraping...")
        
        # Login en Facebook
        email_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.NAME, "email"))
        )
        email_input.send_keys("paseyin536@iminko.com")

        pass_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.NAME, "pass"))
        )
        pass_input.send_keys("contraseña")

        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@name="login"]'))
        )
        login_button.click()
        
        # Esperar a que cargue la página principal
        print("Esperando que cargue la página principal...")
        try:
            WebDriverWait(driver, 30).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label, "¿Qué estás pensando?")]')),
                    EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "¿Qué estás pensando?")]')),
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Crear")]'))
                )
            )
            print("Página principal cargada correctamente")
        except TimeoutException:
            print("No se detectó la interfaz principal, pero continuando...")
        
        # Manejar posibles notificaciones emergentes
        try:
            actions = ActionChains(driver)
            actions.move_by_offset(100, 100).click().perform()
            time.sleep(1)
        except:
            print("No fue necesario cerrar notificaciones")
        
        # Ir a la publicación directamente
        print(f"Navegando a la publicación: {url_publicacion}")
        driver.get(url_publicacion)
        time.sleep(5)
        
        # Buscar y hacer clic en el botón de "Comentar" para asegurarnos de que se muestran los comentarios
        try:
            print("Buscando el botón de comentarios...")
            comentar_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Comentar") and @data-ad-rendering-role="comment_button"]'))
            )
            comentar_button.click()
            print("Se hizo clic en el botón de comentarios")
            time.sleep(2)
        except Exception as e:
            print(f"No se pudo hacer clic en el botón de comentarios: {str(e)}")
            # Continuamos de todos modos, ya que los comentarios podrían estar visibles
        
        # Buscar y hacer clic en el menú de "Más relevantes"
        try:
            print("Buscando el menú de ordenación de comentarios...")
            ordenar_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Más relevantes")]//ancestor::div[@role="button"]'))
            )
            ordenar_menu.click()
            print("Se hizo clic en el menú de ordenación")
            time.sleep(1)
            
            # Hacer clic en "Todos los comentarios"
            todos_comentarios = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Todos los comentarios")]'))
            )
            todos_comentarios.click()
            print("Se seleccionó 'Todos los comentarios'")
            time.sleep(2)
        except Exception as e:
            print(f"No se pudo cambiar el orden de los comentarios: {str(e)}")
            # Continuamos de todos modos
        
        # Scroll para cargar todos los comentarios
        print("Iniciando scroll mejorado para cargar todos los comentarios...")
        num_comentarios_anterior = 0
        max_intentos_sin_cambio = 2
        intentos_sin_cambio = 0
        max_intentos_totales = 50
        
        # Función para contar comentarios
        def contar_comentarios():
            for selector in [
                '//div[contains(@class, "x1y1aw1k") and contains(@class, "xn6708d")]',
                '//div[@data-testid="UFI2Comment/root_depth_0"]',
                '//div[contains(@class, "x1lliihq") and contains(@role, "article")]',
                '//div[contains(@aria-label, "Comentario")]',
                '//span[contains(@class, "x193iq5w") and contains(@class, "xeuugli")]//ancestor::div[contains(@role, "article")]'
            ]:
                try:
                    comentarios = driver.find_elements(By.XPATH, selector)
                    if comentarios and len(comentarios) > 0:
                        return len(comentarios)
                except:
                    continue
            return 0
        
        # Funciones para scroll
        def hacer_scroll_lento():
            """Realiza un scroll lento para simular comportamiento humano"""
            # Altura de la ventana
            window_height = driver.execute_script("return window.innerHeight")
            # Desplazamiento gradual
            scroll_top = driver.execute_script("return document.documentElement.scrollTop")
            # Scroll por pasos, no todo de una vez
            target = scroll_top + window_height * 0.7  # Scroll del 70% de la pantalla
            
            # Hacer scroll gradual
            current = scroll_top
            step = (target - current) / 10
            for i in range(10):
                current += step
                driver.execute_script(f"window.scrollTo(0, {current})")
                time.sleep(0.1)
        
        def hacer_scroll_hasta_comentarios_nuevos():
            """Realiza scrolls hasta encontrar nuevos comentarios o llegar al final"""
            global intentos_sin_cambio
            inicial = contar_comentarios()
            
            # Buscar un punto de anclaje para hacer scroll
            try:
                comentarios_elementos = driver.find_elements(By.XPATH, '//div[contains(@role, "article")]')
                if comentarios_elementos:
                    # Hacer scroll hasta el último comentario visible
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                        comentarios_elementos[-1])
                    time.sleep(1.5)
                    
                    # Hacer scroll adicional para cargar más
                    driver.execute_script("window.scrollBy(0, 500);")
            except:
                # Si no se encuentran comentarios, hacer scroll normal
                hacer_scroll_lento()
            
            # Esperar que carguen los nuevos comentarios
            time.sleep(random.uniform(2, 3))
            
            # Verificar si aparecieron nuevos comentarios
            final = contar_comentarios()
            if final > inicial:
                return True
            return False
        
        # Hacer scroll para cargar "Ver más comentarios" si existe
        def click_ver_mas_comentarios():
            try:
                # Buscar botones "Ver más comentarios" y hacer clic en ellos
                botones_ver_mas = driver.find_elements(By.XPATH, 
                    '//div[contains(text(), "Ver más comentarios") or contains(text(), "Ver comentarios anteriores")]')
                
                if botones_ver_mas:
                    print(f"Se encontraron {len(botones_ver_mas)} botones 'Ver más comentarios'")
                    for boton in botones_ver_mas:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
                            time.sleep(0.5)
                            boton.click()
                            print("Se hizo clic en 'Ver más comentarios'")
                            time.sleep(2)
                            return True
                        except:
                            continue
            except Exception as e:
                print(f"Error al buscar 'Ver más comentarios': {str(e)}")
            return False
        
        # Mejorar la detección de "Mostrar más respuestas"
        def expandir_respuestas():
            try:
                # Buscar enlaces para expandir respuestas
                mostrar_respuestas = driver.find_elements(By.XPATH, 
                    '//span[contains(text(), "respuesta") or contains(text(), "respuestas") or contains(text(), "Respuesta") or contains(text(), "Respuestas")]//ancestor::div[@role="button"]')
                
                if mostrar_respuestas:
                    print(f"Se encontraron {len(mostrar_respuestas)} botones para expandir respuestas")
                    for boton in mostrar_respuestas[:5]:  # Expandir los primeros 5 para no ralentizar demasiado
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
                            time.sleep(0.5)
                            boton.click()
                            print("Se expandieron respuestas")
                            time.sleep(1)
                        except:
                            continue
                    return True
            except Exception as e:
                print(f"Error al expandir respuestas: {str(e)}")
            return False
        
        
        # Bucle principal de scroll mejorado
        for intento in range(max_intentos_totales):
            print(f"Intento de scroll #{intento+1}")
            
            # Contar comentarios actuales
            num_comentarios_actual = contar_comentarios()
            print(f"Comentarios actuales: {num_comentarios_actual}")
            
            # Si hay nuevos comentarios, resetear contador de intentos sin cambio
            if num_comentarios_actual > num_comentarios_anterior:
                print(f"Nuevos comentarios encontrados: {num_comentarios_actual - num_comentarios_anterior}")
                num_comentarios_anterior = num_comentarios_actual
                intentos_sin_cambio = 0
            else:
                intentos_sin_cambio += 1
                print(f"No hay nuevos comentarios. Intentos sin cambio: {intentos_sin_cambio}/{max_intentos_sin_cambio}")
            
            # Intentar diferentes estrategias para cargar más comentarios
            estrategias = [
                hacer_scroll_hasta_comentarios_nuevos,
                click_ver_mas_comentarios,
                expandir_respuestas
            ]
            
            # Aplicar estrategias aleatorias para parecer más humano
            random.shuffle(estrategias)
            for estrategia in estrategias:
                if estrategia():
                    # Si una estrategia tuvo éxito, esperar antes de continuar
                    time.sleep(random.uniform(1, 2))
            
            # Si llevamos muchos intentos sin ver cambios, intentar acciones más drásticas
            if intentos_sin_cambio >= max_intentos_sin_cambio // 2:
                # Scroll a una posición aleatoria
                altura_total = driver.execute_script("return document.body.scrollHeight")
                posicion_aleatoria = random.randint(altura_total // 4, altura_total * 3 // 4)
                driver.execute_script(f"window.scrollTo(0, {posicion_aleatoria});")
                print(f"Scroll a posición aleatoria: {posicion_aleatoria}")
                time.sleep(2)
            
            # Verificar si debemos terminar el bucle
            if intentos_sin_cambio >= max_intentos_sin_cambio:
                print(f"No se detectan nuevos comentarios después de {max_intentos_sin_cambio} intentos. Finalizando scroll.")
                
                # Un último intento: scroll hasta el final y luego hacia arriba
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Si después de todo esto no hay cambios, terminamos
                if contar_comentarios() <= num_comentarios_anterior:
                    break
                else:
                    # Si hay nuevos comentarios, reiniciar el contador
                    num_comentarios_anterior = contar_comentarios()
                    intentos_sin_cambio = 0
                    print(f"Se encontraron nuevos comentarios después del intento final: {num_comentarios_anterior}")
        
        print(f"Proceso de scroll terminado. Total de comentarios encontrados: {contar_comentarios()}")
        
        # Extraer comentarios según los selectores que proporcionaste
        print("Extrayendo información de los comentarios...")
        
        # Intentar diferentes métodos para localizar los comentarios
        comentarios = []
        
        # Método 1: usando los selectores que proporcionaste
        try:
            # Buscar elementos que contienen nombre, lo que probablemente indique un comentario completo
            contenedores_comentarios = driver.find_elements(By.XPATH, '//span[contains(@class, "x193iq5w") and contains(@class, "xeuugli") and contains(@class, "x13faqbe")]//ancestor::div[contains(@role, "article")]')
            if contenedores_comentarios:
                comentarios = contenedores_comentarios
                print(f"Método 1: Encontrados {len(comentarios)} comentarios")
        except Exception as e:
            print(f"Error en Método 1: {str(e)}")
        
        # Método 2: otros selectores comunes si el método 1 falla
        if not comentarios:
            try:
                comentarios = driver.find_elements(By.XPATH, '//div[contains(@role, "article")]')
                print(f"Método 2: Encontrados {len(comentarios)} comentarios")
            except Exception as e:
                print(f"Error en Método 2: {str(e)}")
        
        # Método 3: otro intento
        if not comentarios:
            try:
                comentarios = driver.find_elements(By.XPATH, '//div[contains(@class, "x1y1aw1k")]')
                print(f"Método 3: Encontrados {len(comentarios)} comentarios")
            except Exception as e:
                print(f"Error en Método 3: {str(e)}")
        
        print(f"Total de comentarios a procesar: {len(comentarios)}")
        
        # Procesar cada comentario encontrado
        for i, comentario in enumerate(comentarios):
            try:
                # Extraer nombre según el selector que proporcionaste
                try:
                    nombre = comentario.find_element(By.XPATH, './/span[contains(@class, "x193iq5w") and contains(@class, "xeuugli") and contains(@class, "x13faqbe")]').text
                except:
                    try:
                        nombre = comentario.find_element(By.XPATH, './/a[contains(@class, "x1i10hfl")]').text
                    except:
                        nombre = "Nombre no encontrado"
                
                # Extraer texto del comentario según el selector que proporcionaste
                try:
                    texto = comentario.find_element(By.XPATH, './/div[@dir="auto" and @style="text-align: start;"]').text
                except:
                    try:
                        texto = comentario.find_element(By.XPATH, './/div[contains(@class, "x1iorvi4")]').text
                    except:
                        texto = "Texto no encontrado"
                
                # Extraer enlace al perfil
                try:
                    # Intentar obtener el enlace desde la imagen de perfil o desde el nombre
                    try:
                        # Desde el nombre (más común)
                        perfil = comentario.find_element(By.XPATH, './/a[contains(@class, "x1i10hfl")]').get_attribute("href")
                    except:
                        try:
                            # Desde la imagen
                            img = comentario.find_element(By.XPATH, './/image')
                            # Buscar el enlace padre de la imagen
                            perfil_link = img.find_element(By.XPATH, './ancestor::a').get_attribute("href")
                            perfil = perfil_link
                        except:
                            perfil = "Perfil no encontrado"
                except:
                    perfil = "Perfil no encontrado"
                
                # Guardar la información extraída
                comentario_info = {
                    "nombre": nombre,
                    "texto": texto,
                    "perfil": perfil
                }
                comentarios_extraidos.append(comentario_info)
                
                print(f"Comentario #{i+1}:")
                print(f"Nombre: {nombre}")
                print(f"Texto: {texto}")
                print(f"Perfil: {perfil}")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error al procesar comentario #{i+1}: {str(e)}")
            
        # Guardar los comentarios en un archivo Excel
        if comentarios_extraidos:
            try:
                # Crear un DataFrame con pandas
                guardar_comentarios_en_db(comentarios_extraidos, url_publicacion)
                df = pd.DataFrame(comentarios_extraidos)
                
                # Intentar guardar como Excel con ruta absoluta
                print(f"Intentando guardar Excel en: {ruta_excel}")
                df.to_excel(ruta_excel, index=False)
                print(f"Se han guardado {len(comentarios_extraidos)} comentarios en '{ruta_excel}'")
                
            except Exception as e:
                print(f"Error al guardar Excel: {str(e)}")
                
                # Intentar guardar en el directorio de documentos del usuario (alternativa)
                try:
                    ruta_documentos = os.path.join(os.path.expanduser('~'), 'Documents', 'comentarios_facebook.xlsx')
                    print(f"Intentando guardar en Documentos: {ruta_documentos}")
                    df.to_excel(ruta_documentos, index=False)
                    print(f"Se guardó el Excel en '{ruta_documentos}'")
                except Exception as e2:
                    print(f"Error al guardar en Documentos: {str(e2)}")
                    
                    # Intentar guardar como CSV si falla Excel
                    try:
                        print(f"Intentando guardar como CSV en: {ruta_csv}")
                        df.to_csv(ruta_csv, index=False, encoding='utf-8-sig')  # utf-8-sig para soporte de caracteres especiales en Excel
                        print(f"Se guardó como CSV en '{ruta_csv}'")
                    except Exception as e3:
                        print(f"Error al guardar CSV: {str(e3)}")
                        
                        # Último intento: guardar en el escritorio
                        try:
                            ruta_escritorio = os.path.join(os.path.expanduser('~'), 'Desktop', 'comentarios_facebook.xlsx')
                            print(f"Intentando guardar en Escritorio: {ruta_escritorio}")
                            df.to_excel(ruta_escritorio, index=False)
                            print(f"Se guardó el Excel en '{ruta_escritorio}'")
                        except Exception as e4:
                            print(f"No se pudo guardar en ningún formato: {str(e4)}")

    except Exception as e:
        print(f"Error general en el proceso: {str(e)}")

    finally:
        # Tomar screenshot con ruta absoluta
        try:
            print(f"Guardando screenshot en: {ruta_screenshot}")
            driver.save_screenshot(ruta_screenshot)
            print(f"Screenshot guardado como '{ruta_screenshot}'")
            
            # Intentar guardar screenshot en Documentos si falla
            if not os.path.exists(ruta_screenshot):
                ruta_alt_screenshot = os.path.join(os.path.expanduser('~'), 'Documents', 'facebook_scraping_comentarios.png')
                driver.save_screenshot(ruta_alt_screenshot)
                print(f"Screenshot guardado como alternativa en '{ruta_alt_screenshot}'")
        except Exception as e:
            print(f"Error al guardar screenshot: {str(e)}")
            
        driver.quit()
        return comentarios_extraidos