# Quick Tips for Raspberry Pi Pico 2 W + Thonny

**Project: Home Assistant Workbook Experiments**

---

## Brief
This working document captures key lessons learned and best practices related to the Raspberry Pi Pico W (version 1 & 2) + Thonny, based on the Hawe experiments.
**Disclaimer:** This guide is provided as-is, without any guarantee or liability for errors, omissions, or misconfigurations.

---

## Flashing MicroPython Firmware

1. **Put the Pico 2 W into bootloader mode**  
   - Hold the **BOOTSEL** button while connecting the Pico via USB  
   - It appears as a USB drive named `RPI-RP2`

2. **Flash MicroPython using Thonny**  
   - In Thonny:  
     `Tools → Options → Interpreter → Install or update MicroPython`  
   - Choose: **Board: Raspberry Pi Pico W**

> **Recommended**: Use [official MicroPython builds](https://micropython.org/download/rp2-pico-w/)

---

## Auto-start a Script on Boot

To run an experiment (e.g., `hawe_sht20.py`) automatically on boot:

1. Create a `main.py` file with:

   ```python
   import hawe_sht20
   hawe_sht20.main()  # Adjust if needed
   ```

2. Save `main.py` to the Pico via:  
   `File → Save As… → MicroPython device`

> On reboot, the Pico runs `main.py` automatically.

> Ensure to define globals for wlan & mqtt.

---

## Fixing Thonny Memory or Connection Errors

If you see **`MemoryError`** or REPL connection issues:

- Press **Ctrl + F2** in Thonny (interrupt + soft reset)
- Press it **2–3 times**, if needed, to recover REPL
- Run `gc.collect()` to force garbage collection
- Delete or comment out large/unnecessary code during debugging

---

## Wi-Fi / MQTT Debug Tips

- Double-check `secrets.py` for correct Wi-Fi and MQTT credentials
- Use the onboard LED or `print()` logs to indicate:
  - Wi-Fi connected
  - MQTT broker connected
  - Data publishing status
- If Home Assistant doesn’t show new entities:
  - Check MQTT discovery topic syntax
  - Ensure MQTT discovery messages are **retained**

---

## Best Practices

- Keep code modular: `main.py`, `connect.py`, `utils.py`, etc.
- Exclude sensitive or unnecessary files:
  - Use `.gitignore` to ignore:

    ```
    secrets.py
    __pycache__/
    .fseventsd/
    ```

- Document MQTT topics, discovery paths, and entity IDs clearly
- Restart Pico after flashing changes to ensure fresh state

---

## Troubleshooting Checklist

| Issue                           | Fix                                                                 |
|--------------------------------|----------------------------------------------------------------------|
| Pico not appearing as `RPI-RP2` | Hold **BOOTSEL** before plugging into USB                           |
| Thonny shows REPL stuck         | Press **Ctrl + F2** a few times                                     |
| `MemoryError` in REPL           | Use `gc.collect()` or simplify code                                 |
| MQTT sensor not visible         | Check topic names, `retain=True`, and restart Home Assistant        |
| Script doesn’t run on boot      | Make sure it’s named **`main.py`** and stored on the Pico device    |

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---
