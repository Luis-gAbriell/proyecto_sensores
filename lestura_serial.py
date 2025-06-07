import serial
import pandas as pd
import time
import os

# --------- CONFIGURACIÓN ---------
PUERTO = 'COM3'        # Ajusta según tu sistema (ej. COM3, COM7)
BAUDIOS = 9600
LECTURAS_POR_BLOQUE = 20
# ---------------------------------

# Iniciar conexión serial
ser = serial.Serial(PUERTO, BAUDIOS)
time.sleep(2)  # Esperar a que se estabilice la conexión

seguir = True

while seguir:
    print("⏳ Iniciando nueva lectura de datos...")
    datos = []

    # Leer 100 líneas del puerto serial
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

    # Nombre único usando timestamp
    timestamp = int(time.time())
    nombre_csv = f"datos_sensores_{timestamp}.csv"
    nombre_xlsx = f"datos_sensores_{timestamp}.xlsx"

    # Guardar como CSV
    df.to_csv(nombre_csv, index=False)
    print(f" Archivo .csv guardado: {nombre_csv}")

    # Guardar como Excel
    try:
        df.to_excel(nombre_xlsx, index=False, engine='openpyxl')
        print(f" Archivo .xlsx guardado: {nombre_xlsx}")
    except Exception as e:
        print(f" Error guardando Excel: {e}")

    # Abrir Excel automáticamente (esto abre el .xlsx si se puede, si no, abre el .csv)
    try:
        os.startfile(nombre_xlsx)  # En Windows
    except:
        try:
            os.startfile(nombre_csv)
        except:
            print("⚠️ No se pudo abrir el archivo automáticamente.")

    # Preguntar si deseas seguir
    seguir = input("\n¿Deseas seguir recolectando datos? (s/n): ").lower() == 's'

ser.close()
print(" Lectura finalizada.")
