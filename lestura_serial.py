import serial
import time
import pandas as pd
from tabulate import tabulate  # Para mostrar tabla bonita en consola

# Configuración del puerto serial
puerto = 'COM3'  # Cambiar según tu puerto
baud_rate = 9600
arduino = serial.Serial(puerto, baud_rate)
time.sleep(2)

# Lista para almacenar datos
datos = []

try:
    while True:
        linea = arduino.readline().decode('utf-8').strip()
        if linea:
            valores = linea.split(',')
            if len(valores) == 4:
                temperatura = float(valores[0])
                humedad = float(valores[1])
                presion = float(valores[2])
                luz = float(valores[3])
                
                datos.append([temperatura, humedad, presion, luz])

        if len(datos) >= 10:  # Puedes cambiar el número de lecturas
            break

except KeyboardInterrupt:
    print("Lectura interrumpida.")

finally:
    arduino.close()

    # Crear DataFrame
    df = pd.DataFrame(datos, columns=["Temperatura (°C)", "Humedad (%)", "Presión (hPa)", "Luz (lux)"])

    # Mostrar tabla en consola con estilo
    print("\nLecturas obtenidas:\n")
    print(tabulate(df, headers='keys', tablefmt='fancy_grid'))

    # Guardar en archivo CSV
    df.to_csv("datos_sensores.csv", index=False)
    print("\n✅ Datos guardados en datos_sensores.csv")
