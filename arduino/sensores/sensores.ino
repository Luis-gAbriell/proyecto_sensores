#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <DHT.h>
#include <BH1750.h>

// Configurar sensores
#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;
BH1750 lightMeter;

void setup() {
  Serial.begin(9600);
  dht.begin();
  bmp.begin();
  lightMeter.begin();
  delay(1000);
}

void loop() {
  float temperatura = dht.readTemperature();
  float humedad = dht.readHumidity();
  float presion = bmp.readPressure() / 100.0; // hPa
  float luz = lightMeter.readLightLevel();    // Lux

  // Validar lectura
  if (isnan(temperatura) || isnan(humedad)) {
    Serial.println("Error al leer DHT11");
    return;
  }

  // Enviar datos en formato CSV
  Serial.print(temperatura); Serial.print(",");
  Serial.print(humedad);     Serial.print(",");
  Serial.print(presion);     Serial.print(",");
  Serial.println(luz);

  delay(2000); // 2 segundos entre lecturas
}
