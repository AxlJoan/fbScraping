from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import pandas as pd
import os

# Crear una ruta absoluta para guardar los archivos
# Esto asegura que se guarden en una ubicación conocida
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_excel = os.path.join(directorio_actual, 'comentarios_facebook.xlsx')
ruta_csv = os.path.join(directorio_actual, 'comentarios_facebook.csv')
ruta_screenshot = os.path.join(directorio_actual, 'facebook_scraping_comentarios.png')

print(f"Los archivos se guardarán en: {directorio_actual}")

# Configuración inicial
url_publicacion = "https://www.facebook.com/share/p/16aDygJp1M/"
email = "paseyin536@iminko.com"
password = "contraseña"
comentario_aBuscar = "Felicidades Cancún por todo lo que nos has dado, llegamos e hicimos nuestra vida y hemos logrado salir adelante hay quien se queja pero el que vino a trabajar a logrado salir adelante"

# Iniciar navegador con opciones
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

# Lista para almacenar los comentarios extraídos
comentarios_extraidos = []

try:
    print("Iniciando el proceso de scraping...")
    
    # Login en Facebook
    print("Iniciando login...")
    email_input = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.NAME, "email"))
    )
    email_input.send_keys(email)

    pass_input = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.NAME, "pass"))
    )
    pass_input.send_keys(password)

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
    
    # Buscar y hacer clic en el botón de "Comentar"
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
    
    # Buscar y hacer clic en el menú de "Más relevantes" y luego "Todos los comentarios"
    try:
        print("Buscando el menú de ordenación de comentarios...")
        ordenar_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Más relevantes")]//ancestor::div[@role="button"]'))
        )
        ordenar_menu.click()
        print("Se hizo clic en el menú de ordenación")
        time.sleep(1)
        todos_comentarios = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Todos los comentarios")]'))
        )
        todos_comentarios.click()
        print("Se seleccionó 'Todos los comentarios'")
        time.sleep(2)
    except Exception as e:
        print(f"No se pudo cambiar el orden de los comentarios: {str(e)}")

    # Definir funciones de scroll y expansión
    def contar_comentarios():
        selectors = [
            "//div[contains(@class, 'x1lliihq') and contains(@role, 'article')]",
            "//div[@data-testid='UFI2Comment/root_depth_0']"
        ]
        for sel in selectors:
            elems = driver.find_elements(By.XPATH, sel)
            if elems:
                return len(elems)
        return 0

    def hacer_scroll_lento():
        window_height = driver.execute_script("return window.innerHeight")
        scroll_top = driver.execute_script("return document.documentElement.scrollTop")
        target = scroll_top + window_height * 0.7
        current = scroll_top
        step = (target - current) / 10
        for _ in range(10):
            current += step
            driver.execute_script(f"window.scrollTo(0, {current})")
            time.sleep(0.1)

    def hacer_scroll_hasta_comentarios_nuevos():
        inicial = contar_comentarios()
        try:
            elems = driver.find_elements(By.XPATH, '//div[contains(@role, "article")]')
            if elems:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elems[-1])
                time.sleep(1.5)
                driver.execute_script("window.scrollBy(0, 500);")
        except:
            hacer_scroll_lento()
        time.sleep(random.uniform(2,3))
        return contar_comentarios() > inicial

    def click_ver_mas_comentarios():
        try:
            botones = driver.find_elements(By.XPATH, '//div[contains(text(), "Ver más comentarios") or contains(text(), "Ver comentarios anteriores")]')
            for boton in botones:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
                time.sleep(0.5)
                boton.click()
                time.sleep(2)
                return True
        except:
            pass
        return False

    def expandir_respuestas():
        try:
            botones = driver.find_elements(By.XPATH, 
                '//span[contains(text(), "respuesta") or contains(text(), "respuestas")]//ancestor::div[@role="button"]')
            for boton in botones[:5]:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
                time.sleep(0.5)
                boton.click()
                time.sleep(1)
            return True
        except:
            return False

    # Función para buscar y detener el scroll en el comentario buscado
    def buscar_comentario(texto_objetivo, max_intentos=50):
        for intento in range(max_intentos):
            expandir_respuestas()
            bloques = driver.find_elements(By.XPATH, "//div[contains(@role, 'article')]")
            for bloque in bloques:
                try:
                    texto = bloque.find_element(By.XPATH, ".//div[@dir='auto']").text
                    if texto_objetivo.lower() in texto.lower():
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", bloque)
                        print("Comentario encontrado.")
                        # Resaltar el comentario
                        driver.execute_script("arguments[0].style.border='3px solid red'; arguments[0].style.backgroundColor='yellow';", bloque)
                        # Pausa antes de continuar
                        for i in range(30, 0, -1):
                            print(f"Deteniendo {i} segundos...", end="\r")
                            time.sleep(1)
                        print("Continuando...")
                        return True
                except:
                    continue
            # scroll strategies
            if not click_ver_mas_comentarios():
                hacer_scroll_lento()
        print("Comentario no encontrado.")
        return False

    # Ejecutar búsqueda integrada
    encontrado = buscar_comentario(comentario_aBuscar)
    if encontrado:
        print("Comentario encontrado. Procesamiento detenido.")
    else:
        print("No se encontró el comentario. Continuando con extracción...")

    # Mantener el navegador abierto para inspección manual
    input("Presiona Enter para cerrar el navegador...")

    driver.quit()

except Exception as e:
    print(f"Error general en el proceso: {e}")
