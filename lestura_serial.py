import serial
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import time
import os

# Configura tu puerto y velocidad según Arduino
puerto = 'COM3'  # Cambia esto si usas otro
baudrate = 9600
arduino = serial.Serial(puerto, baudrate)
time.sleep(2)  # Espera a que se conecte

# Conexión a SQLite (se crea si no existe)
conn = sqlite3.connect('sensores.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temperatura REAL,
        humedad REAL,
        presion REAL,
        luz REAL
    )
''')
conn.commit()

# Parámetros
block_size = 20
block_num = 1
limite_grafica = 50  # Mostrar últimas N muestras

# Activa el modo interactivo de matplotlib
plt.ion()
fig, ax = plt.subplots(figsize=(10, 5))

# Listas para las gráficas
temps, hums, press, luces, tiempos = [], [], [], [], []

while True:
    datos = []
    while len(datos) < block_size:
        try:
            linea = arduino.readline().decode().strip()
            valores = [float(x) for x in linea.split(',')]
            if len(valores) == 4:
                temp, hum, pres, luz = valores
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                datos.append([timestamp, temp, hum, pres, luz])
                
                # Guardar en SQLite
                cursor.execute('''
                    INSERT INTO mediciones (timestamp, temperatura, humedad, presion, luz)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, temp, hum, pres, luz))
                conn.commit()

                # Actualizar listas para gráfica
                tiempos.append(timestamp)
                temps.append(temp)
                hums.append(hum)
                press.append(pres)
                luces.append(luz)

                # Mantener solo últimas N muestras
                if len(temps) > limite_grafica:
                    tiempos = tiempos[-limite_grafica:]
                    temps = temps[-limite_grafica:]
                    hums = hums[-limite_grafica:]
                    press = press[-limite_grafica:]
                    luces = luces[-limite_grafica:]

                # Actualizar gráfica
                ax.clear()
                ax.plot(temps, label='Temp (°C)', color='red')
                ax.plot(hums, label='Humedad (%)', color='blue')
                ax.plot(press, label='Presión (hPa)', color='green')
                ax.plot(luces, label='Luz (lux)', color='orange')
                ax.set_title('Lecturas en tiempo real')
                ax.set_xlabel('Muestras recientes')
                ax.set_ylabel('Valor')
                ax.legend()
                ax.grid(True)
                plt.pause(0.01)

        except Exception as e:
            print("Error:", e)

    # Crear DataFrame
    df = pd.DataFrame(datos, columns=['Timestamp', 'Temperatura', 'Humedad', 'Presion', 'Luz'])
    print(df)

    # Guardar CSV y Excel
    nombre_base = f"datos_sensores_{block_num:04d}"
    df.to_csv(f"{nombre_base}.csv", index=False)
    df.to_excel(f"{nombre_base}.xlsx", index=False)

    print(f"\nBloque {block_num} guardado en CSV, Excel y base de datos SQLite.")
    block_num += 1

    # Preguntar si continuar
    continuar = input("\n¿Deseas seguir recolectando datos? (s/n): ").strip().lower()
    if continuar != 's':
        break

arduino.close()
conn.close()
print("Lectura finalizada.")
