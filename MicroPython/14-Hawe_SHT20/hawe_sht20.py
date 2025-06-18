"""
hawe_sht20.py
Read the temperature & humidity from SHT20 module.
The SHT20 is a temperature and humidity sensor compatible with the SHT2x series from Sensirion.
Communication via I2C (default address 0x40) using specific command codes.
SHT20 I2C Command Set (important codes)
0xF3 → Trigger temperature measurement (no hold)
0xF5 → Trigger humidity measurement (no hold)
Read back 3 bytes: [MSB][LSB][CRC]

Date: 2025-06-15

Author: Robert W.B. Linn

Notes: This script publishes readings via MQTT to Home Assistant.

Wiring:
Encoder Pin | Pico Pin  | Purpose                 |
----------- | ----------| ------------------------|
VCC         | 3V3       | Power supply (MUST 3V3) |
SCL         | GP01 (#2) | Clock                   |
SDA         | GP00 (#1) | Data                    |
GND         | GND       | Ground reference        |

Script Output:
[publish_sensor] t=24.57,h=68.58,dp=18.40
"""

# SCRIPT START
import network
import time
import machine
# import ubinascii
import ujson
from math import log
import gc

# Import own modules
import secrets
import connect
import utils

print(f"[initialize] hawe_sht20")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- DEVICE CONFIG ----
DEVICE_NAME = "Hawe SHT20"
DEVICE_ID = "sht20"
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
                            #"homeassistant/sensor/hawe/sht20/availability"
TOPIC_AVAILABILITY          = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}/{DEVICE_ID}/availability"

# IMPORTANT REMINDER FOR MQTT DISCOVERY
# homeassistant/<component>/<unique_id>/config

# Temperature - Entity = sensor.hawe_sht20_temperature
                            #"homeassistant/sensor/hawe_sht20_temperature/config"
TOPIC_CONFIG_TEMPERATURE    = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature/config"
                            #"hawe/sht20/temperature/state"
TOPIC_STATE_TEMPERATURE     = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/temperature/state"

# Humidity - Entity = sensor.hawe_sht20_humidity
                            #"homeassistant/sensor/hawe_sht20_humidity/config"
TOPIC_CONFIG_HUMIDITY       = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity/config"
                            #"hawe/sht20/humidity/state"
TOPIC_STATE_HUMIDITY        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/humidity/state"

# Dewpoint - Entity = sensor.hawe_sht20_dewpoint
                            #"homeassistant/sensor/hawe_sht20_dewpoint/config"
TOPIC_CONFIG_DEWPOINT       = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_dewpoint/config"
                            #"hawe/sht20/dewpoint/state"
TOPIC_STATE_DEWPOINT        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/dewpoint/state"

# --- SENSOR (SHT20) ---

# Read every 10 seconds
SHT20_READ_INTERVAL = 10

# Class to init and read data from the SHT20
class SHT20:
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x40

    def read(self, cmd):
        self.i2c.writeto(self.addr, bytes([cmd]))
        time.sleep(0.1)
        return self.i2c.readfrom(self.addr, 3)

    def measure(self):
        raw = self.read(0xF3)
        temp_raw = (raw[0] << 8) | raw[1]
        temp = -46.85 + (175.72 * temp_raw / 65536)

        raw = self.read(0xF5)
        hum_raw = (raw[0] << 8) | raw[1]
        hum = -6 + (125.0 * hum_raw / 65536)

        return temp, hum

def dewpoint(t, rh):
    a = 17.62
    b = 243.12
    gamma = (a * t) / (b + t) + log(rh / 100.0)
    return (b * gamma) / (a - gamma)

# ---- MQTT ----
def publish_availability():
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def publish_discovery():
    device_info = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME
    }

    # MQTTAD_TOPIC_TEMPERATURE = "homeassistant/sensor/hawe_sht20_temperature/config"
    configs = [
        (TOPIC_CONFIG_TEMPERATURE, {
         "device_class": "temperature",
         "name": "Temperature",
         "state_topic": TOPIC_STATE_TEMPERATURE,
         "unit_of_measurement": "°C",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        })
        ,
        (TOPIC_CONFIG_HUMIDITY, {
         "device_class": "humidity",
         "name": "Humidity",
         "state_topic": TOPIC_STATE_HUMIDITY,
         "unit_of_measurement": "%",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        })
        ,
        (TOPIC_CONFIG_DEWPOINT, {
         "device_class": "temperature",
         "name": "Dewpoint",
         "state_topic": TOPIC_STATE_DEWPOINT,
         "unit_of_measurement": "°C",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_dewpoint",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_dewpoint",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        })

    ]

    for topic, cfg in configs:
        # The empty payload to clear retained messages is usually sent as a zero-length byte string (b"") rather than an empty Unicode string ("").
        # Some MQTT brokers (or clients) can interpret these differently, and b"" is the standard to clear a retained message.

        payload = b""
        mqtt.publish(topic, payload, retain=True)
        print(f"[publish_discovery] removed topic={topic}")
        time.sleep(1)

        payload = ujson.dumps(cfg)
        mqtt.publish(topic, payload.encode('utf-8'), retain=True)
        print(f"[publish_discovery] added topic={topic}")
        # print(f"[publish_discovery] added topic={topic},payload={payload}")
        time.sleep(1)

def publish_sensor(temp, hum, dew):
    temp_str = "{:.2f}".format(temp)
    hum_str = "{:.2f}".format(hum)
    dew_str = "{:.2f}".format(dew)
    mqtt.publish(TOPIC_STATE_TEMPERATURE, temp_str.encode('utf-8'), retain=True)
    mqtt.publish(TOPIC_STATE_HUMIDITY, hum_str, retain=True)
    mqtt.publish(TOPIC_STATE_DEWPOINT, dew_str, retain=True)
    print(f"[publish_sensor] t={temp_str},h={hum_str},dp={dew_str}")
    # print(f"[publish_sensor] {TOPIC_STATE_TEMPERATURE}={temp_str}")

# Initialize sensor - if error then show error and stop script
sensor_initialized = False
try:
    sht20 = SHT20(machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0)))
    sensor_initialized = True
    print(f"[initialize_sensor] SHT20 OK")
except Exception as e:
    print(f"[ERROR] Failed to initialize SHT20 sensor - {repr(e)}.")
    utils.onboard_led_blink(times=5)  # Optional: visual feedback
    print(f"[ERROR] Script stopped.")
    sensor_initialized = False

# --- MAIN ---
def main_loop():
    while True:
        utils.onboard_led_on()

        temp, hum = sht20.measure()
        dew = dewpoint(temp, hum)
        # print(f"[main] t={temp:.2f}°C, h={hum:.2f}%, dp={dew:.2f}°C")
        publish_sensor(temp, hum, dew)
        mqtt.check_msg()  # Keeps MQTT alive
        
        utils.onboard_led_off()
        time.sleep(SHT20_READ_INTERVAL)

# ---- BOOT ----
# Only start if the sensor is properly initialized
if sensor_initialized:
    # WiFi Connect
    wlan = connect.connect_wifi()

    # MQTT Connect
    mqtt = connect.connect_mqtt(MQTT_CLIENT_ID,
        None,
        last_will_topic=TOPIC_AVAILABILITY,
        last_will_message="offline"
    )
    
    publish_availability()

    # MQTT Publish MQTT Discovery topics
    publish_discovery()

    # Turn the onboard led on
    utils.onboard_led_on()

    # Run the main loop
    main_loop()
