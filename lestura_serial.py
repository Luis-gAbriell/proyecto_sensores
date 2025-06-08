import serial
import pandas as pd
import time
import os
import requests

# --------- CONFIGURACIÓN ---------
PUERTO = 'COM3'        # Cambia según tu sistema
BAUDIOS = 9600
LECTURAS_POR_BLOQUE = 20

# Tu API Key de escritura de ThingSpeak (cambia esto por la tuya)
API_KEY = 'H96OCP4HL5F0PXYU'
# ---------------------------------

# Iniciar conexión serial
ser = serial.Serial(PUERTO, BAUDIOS)
time.sleep(2)  # Esperar a que se estabilice la conexión

seguir = True

while seguir:
    print("\n Iniciando nueva lectura de datos...")
    datos = []

    # Leer datos del puerto serial
    while len(datos) < LECTURAS_POR_BLOQUE:
        try:
            linea = ser.readline().decode().strip()
            if linea:
                valores = linea.split(',')
                if len(valores) == 4:
                    datos.append({
                        'Temperatura (°C)': float(valores[0]),
                        'Humedad (%)': float(valores[1]),
                        'Presión (hPa)': float(valores[2]),
                        'Luz (lux)': float(valores[3])
                    })
        except Exception as e:
            print(f" Error leyendo datos: {e}")

    # Crear DataFrame
    df = pd.DataFrame(datos)
    print("\n Datos recolectados:")
    print(df)

    # Guardar archivos locales
    timestamp = int(time.time())
    nombre_csv = f"datos_sensores_{timestamp}.csv"
    nombre_xlsx = f"datos_sensores_{timestamp}.xlsx"

    df.to_csv(nombre_csv, index=False)
    print(f" Archivo .csv guardado: {nombre_csv}")

    try:
        df.to_excel(nombre_xlsx, index=False, engine='openpyxl')
        print(f" Archivo .xlsx guardado: {nombre_xlsx}")
    except Exception as e:
        print(f" Error guardando Excel: {e}")

    # Abrir Excel automáticamente (opcional)
    try:
        os.startfile(nombre_xlsx)
    except:
        try:
            os.startfile(nombre_csv)
        except:
            print(" No se pudo abrir el archivo automáticamente.")

    # Enviar la última lectura a ThingSpeak
    try:
        ultima = df.iloc[-1]
        temperatura = ultima['Temperatura (°C)']
        humedad = ultima['Humedad (%)']
        presion = ultima['Presión (hPa)']
        luz = ultima['Luz (lux)']

        url = f"https://api.thingspeak.com/update?api_key={API_KEY}&field1={temperatura}&field2={humedad}&field3={presion}&field4={luz}"
        respuesta = requests.get(url)

        if respuesta.status_code == 200 and respuesta.text != '0':
            print(" Datos enviados a ThingSpeak.")
        else:
            print(f" Error al subir datos a ThingSpeak. Código: {respuesta.status_code} | Respuesta: {respuesta.text}")

    except Exception as e:
        print(f" Excepción al conectar con ThingSpeak: {e}")

    # Preguntar si deseas continuar
    seguir = input("\n¿Deseas seguir recolectando datos? (s/n): ").lower() == 's'

ser.close()
print("\n Lectura finalizada.")
