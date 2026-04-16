/**
 * Smart Sensor Data Acquisition & Test System
 * --------------------------------------------
 * Target MCU : ESP32 (DevKit v1)
 * Sensors    : BME280 (I2C), DS18B20 (1-Wire)
 * Author     : Ghulam Sarwar
 *
 * Streams CSV data over USB-serial for the Python logger:
 *   TS_MS,TEMP_BME,HUM,PRES,TEMP_DS,STATUS
 *
 * MIT License
 */

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define I2C_SDA        21
#define I2C_SCL        22
#define ONE_WIRE_PIN    4
#define LED_HEARTBEAT   2

constexpr uint32_t SAMPLE_PERIOD_MS = 1000;
constexpr uint32_t SERIAL_BAUD      = 115200;
constexpr uint8_t  BME280_ADDR      = 0x76;

Adafruit_BME280    bme;
OneWire            oneWire(ONE_WIRE_PIN);
DallasTemperature  ds18(&oneWire);
bool               bmeOk = false;
bool               dsOk  = false;

void setup() {
    pinMode(LED_HEARTBEAT, OUTPUT);
    Serial.begin(SERIAL_BAUD);
    delay(200);
    Serial.println(F("# Smart Sensor DAQ boot"));

    Wire.begin(I2C_SDA, I2C_SCL);
    bmeOk = bme.begin(BME280_ADDR);
    Serial.printf("# BME280: %s\n", bmeOk ? "OK" : "FAIL");

    ds18.begin();
    dsOk = (ds18.getDeviceCount() > 0);
    Serial.printf("# DS18B20: %s\n", dsOk ? "OK" : "FAIL");

    Serial.println(F("TS_MS,TEMP_BME,HUM,PRES,TEMP_DS,STATUS"));
}

void loop() {
    static uint32_t tNext = 0;
    uint32_t now = millis();
    if (now < tNext) return;
    tNext = now + SAMPLE_PERIOD_MS;

    float tBme = NAN, h = NAN, p = NAN, tDs = NAN;
    if (bmeOk) {
        tBme = bme.readTemperature();
        h    = bme.readHumidity();
        p    = bme.readPressure() / 100.0f;
    }
    if (dsOk) {
        ds18.requestTemperatures();
        tDs = ds18.getTempCByIndex(0);
    }

    const char* status = (bmeOk && dsOk) ? "OK"
                        : (!bmeOk && !dsOk) ? "BOTH_FAIL"
                        : (!bmeOk) ? "BME_FAIL" : "DS_FAIL";

    Serial.printf("%lu,%.2f,%.2f,%.2f,%.2f,%s\n",
                  now, tBme, h, p, tDs, status);

    digitalWrite(LED_HEARTBEAT, !digitalRead(LED_HEARTBEAT));
}
