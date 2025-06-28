# Home Assistant Workbook - Experiment Hawe_SolarInfo_LCD1602 (MicroPython)

This experiment reads live solar power data from a Home Assistant production system via MQTT and displays it on a **1602 LCD with I2C (PCF8574 backpack)**.  
Data is published from the HA production system via a Node-RED REST/MQTT bridge and visualized on the development system.

---

## Contents

| File                                      | Purpose                                         |
|-------------------------------------------|-------------------------------------------------|
| `hawe_solarinfo_lcd1602.py`               | Main MicroPython application                    |
| `secrets.py`                              | WiFi and MQTT credentials (user-defined)        |
| `connect.py`                              | WiFi and MQTT connection utility                |
| `utils.py`                                | Helper functions (e.g. LED blink, etc.)         |
| `lcd_api.py`                              | LCD display abstraction                         |
| `i2c_lcd.py`                              | I2C LCD driver for PCF8574                      |
| `node-red-flow-solar_info_collector.json` | Node-RED Solar Info data Collector              |
| `README.md`                               | This documentation                              |

---

## Prepare Node-RED

A Node-RED flow is required to collect solar info data in JSON format.  
The flow runs every minute and publishes a JSON string to:  
`hawe/solar_info/helper`

**Example Payload:**
```json
{
  "power_to_house": 161,
  "power_date_stamp": 20250620,
  "power_from_solar": 3306,
  "power_from_grid": 0,
  "power_to_grid": 3145,
  "power_time_stamp": 753,
  "power_battery_charge": 100,
  "power_to_battery": 0,
  "power_from_battery": 0
}
```

---

## Usage

1. Edit `secrets.py` with your WiFi and MQTT configuration.
2. Upload all files to your Raspberry Pi Pico W using Thonny or ampy.
3. Connect the LCD1602 with I2C backpack to the correct pins (see wiring).
4. Run `hawe_solarinfo_lcd1602.py`.
5. View solar data in real time.

---

## 🔌 Wiring

### LCD1602 (I2C backpack via PCF8574)

| LCD Pin | Connect to Pico Pin      | Function      |
|---------|---------------------------|---------------|
| **GND** | GND                       | Ground        |
| **VCC** | 5V                        | Power         |
| **SCL** | GP27 (physical pin 32)    | I2C Clock     |
| **SDA** | GP26 (physical pin 31)    | I2C Data      |

> **Important**: LCD1602 often requires 5V power, unlike OLEDs which run on 3.3V.

> I2C device address: ['0x27']; Channel: 1

 **Hint**
It might happen that after an I/O error (like EIO), a Pico 2 W sometimes needs a full unplug-replug to reset I2C hardware properly.
That’s a common quirk when an I2C peripheral (like OLED) hangs or is partially initialized.

---

## Display Example (LCD 1602)

```
S3306 G0     0753
H186  T3145  B100
```

- `S` = Solar Power (W)
- `G` = Grid Power (W)
- `H` = House Power (W)
- `T` = To Grid (W)
- `B` = Battery Charge (%)
- Right-top = Time (HHMM)

---

## Notes

- Display updates on each MQTT message.
- LCD stays awake via periodic backlight keep-alive (`lcd.backlight_on()`).
- Make sure the LCD power supply is stable and steady 5V.
- If the LCD has a contrast potentiometer, ensure it's set correctly to avoid apparent “blank” screens.
- If possible, try a simple “keep alive” loop displaying static text every 30 seconds, without backlight toggling, to isolate whether it’s a hardware or software issue.
- Check if your particular LCD or backpack module datasheet mentions any power-saving or sleep modes and how to disable them.

## LCD 2004
Should also work with LCD 2004 (adjust rows/columns accordingly)... BUT not tested.
The i2c_lcd.py driver used is generally compatible with 16x2 and 20x4 HD44780-based LCDs because it uses standard commands for these LCD controllers.
To use an LCD 2004:
Change the initialization call to:
```
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)  # 4 rows, 20 columns
```
Adjust the display text to fit 20 columns and 4 rows.
The rest of the driver functions remain the same.

---

## Related Documentation

- Node-RED flow in HA production system handles REST + MQTT publishing.
- MQTT topics are defined manually via `solar_sensors.yaml`.
- Lovelace Dashboard displays values using standard MQTT sensors.

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---
