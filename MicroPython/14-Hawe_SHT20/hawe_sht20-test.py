## hawesht20.py
## Read the temperature & humidity from SHT20 module.
## 202506014
## Notes
##Dew Point Calculation
## A widely used approximation is the Magnus-Tetens formula:
## DewPoint=(b.γ(T,RH))/(a−γ(T,RH))
## Where:
## γ(T,RH)=((a.T)/(b+T))+ln(RH/100)
## TT = temperature in °C
## RHRH = relative humidity in %
## Constants: a=17.62,b=243.12°C
## This gives good accuracy for typical environmental temperatures (0–50 °C).

## Script Output:
## Temp: 22.62 °C, RH: 63.21 %, Dew Point: 15.27 °C
## Temp: 24.76 °C, RH: 66.56 %, Dew Point: 18.11 °C
## Temp: 23.89 °C, RH: 70.71 %, Dew Point: 18.24 °C

from machine import I2C, Pin
import time
import math

# I2C address of the module. Default is 0x40, but check out using the I2CScanner.
SHT20_ADDR = 0x40

# I2C init on Pico GP0=SDA, GP1=SCL
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

def read_temperature():
    i2c.writeto(SHT20_ADDR, b'\xF3')
    time.sleep_ms(85)
    data = i2c.readfrom(SHT20_ADDR, 3)
    raw = (data[0] << 8) | data[1]
    raw &= 0xFFFC
    return round(-46.85 + 175.72 * raw / 65536, 2)

def read_humidity():
    i2c.writeto(SHT20_ADDR, b'\xF5')
    time.sleep_ms(29)
    data = i2c.readfrom(SHT20_ADDR, 3)
    raw = (data[0] << 8) | data[1]
    raw &= 0xFFFC
    return round(-6 + 125.0 * raw / 65536, 2)

def calculate_dewpoint(temp_c, humidity):
    a = 17.62
    b = 243.12
    gamma = (a * temp_c) / (b + temp_c) + math.log(humidity / 100.0)
    dew_point = (b * gamma) / (a - gamma)
    return round(dew_point, 2)

# Main loop
while True:
    try:
        temp = read_temperature()
        rh = read_humidity()
        dew = calculate_dewpoint(temp, rh)
        print("Temp: {} °C, RH: {} %, Dew Point: {} °C".format(temp, rh, dew))
    except Exception as e:
        print("Error:", e)
    time.sleep(2)
