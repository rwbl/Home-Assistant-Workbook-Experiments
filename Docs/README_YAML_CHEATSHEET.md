# YAML for Home Assistant: Cheat Sheet

**Project: Home Assistant Workbook Experiments**

---

## Brief

This working document summarizes **YAML** usage within Home Assistant (HA), with focus on syntax, best practices, common tasks, and helpful tips.
**Disclaimer:** This guide is provided as-is, without any guarantee or liability for errors, omissions, or misconfigurations.

---

## YAML Basics

```yaml
# Key-value pair
key: value

# Lists
items:
  - item1
  - item2

# Nested dictionaries
parent:
  child1: value1
  child2: value2
```

- **Use 2 spaces** for indentation (never tabs!)
- Strings don't require quotes unless they contain `:` or start with special characters.
- Comments begin with `#`.

---

## Common HA Entities

```yaml
sensor:
  - platform: mqtt
    name: "Solar Power"
    state_topic: "hawe/solar_info/helper"
    unit_of_measurement: "W"
    value_template: "{{ value_json.power_from_solar }}"
```

- Top-level domains: `sensor`, `switch`, `light`, `binary_sensor`, etc.
- Use lists (`-`) when defining multiple entities.

---

## Templates in YAML (Jinja2)

```yaml
value_template: "{{ value_json.temperature }}"
availability_template: "{{ value_json.online == true }}"
```

### Expressions
```yaml
{{ now().hour }}
{{ states('sensor.solar_power') | int(0) > 1000 }}
```

### Conditional logic
```yaml
{% if is_state('binary_sensor.motion', 'on') %}
  Motion detected
{% else %}
  No motion
{% endif %}
```

---

## Local Variables

Use `set` inside `jinja` blocks:
```yaml
{% set power = states('sensor.power') | int %}
{{ power > 1000 }}
```

---

## Best Practices

- Use consistent spacing (2 spaces).
- Comment your YAML for clarity.
- Use `value_template` to parse JSON payloads.
- Split config into files (e.g. `sensor.yaml`, `automation.yaml`) using `!include` or `packages`.
- Use `friendly_name` and keep `entity_id`s lowercase with underscores.

---

## Common Pitfalls

- Using **tabs** instead of spaces.
- Forgetting to quote strings with colons or special characters.
- Wrong or missing `value_template` in MQTT sensors.
- Indentation mistakes (esp. nested structures).

---

## Advanced YAML Tricks

### Anchors and Aliases
Avoid duplication:
```yaml
defaults: &defaults
  qos: 1
  retain: true

sensor:
  - platform: mqtt
    <<: *defaults
    name: "Power"
    state_topic: "solar/power"
```

### Conditions in Automations
```yaml
condition:
  - condition: time
    after: "06:00:00"
    before: "22:00:00"
  - condition: state
    entity_id: binary_sensor.motion
    state: "on"
```

---

## Common Use Cases

### MQTT Binary Sensor
```yaml
binary_sensor:
  - platform: mqtt
    name: "Door"
    state_topic: "home/door/state"
    payload_on: "OPEN"
    payload_off: "CLOSED"
```

### Template Sensor
```yaml
sensor:
  - platform: template
    sensors:
      battery_ok:
        friendly_name: "Battery OK"
        value_template: "{{ states('sensor.battery_level') | int > 20 }}"
```

---

## Debugging & Tools

- **Check config**: `Developer Tools > YAML > Check Configuration`
- **Test templates**: `Developer Tools > Template`
- **Online YAML lint**: [https://yamllint.com](https://yamllint.com)
- Logs: `/config/home-assistant.log`

---

## Organizing Configs

Split config via:
```yaml
homeassistant:
  packages: !include_dir_named packages

sensor: !include sensors.yaml
automation: !include automations.yaml
```

---

## Tips

- Use `| int(0)` or `| float(0)` to avoid crashes on null/missing values.
- Use `| default('N/A')` to set fallback values.
- Always test templates in HA UI before deploying.

### Rounding
**Wrong**
```
{{ (b / 255) * 100 | round(0) }}
```
is actually interpreted as:
```
(b / 255) * (100 | round(0))
```
because the filter applies only to what’s immediately before it — 100 — not to the whole expression.

**Correct**
```
{{ ((b / 255) * 100) | round(0) }}
```
or even better, explicitly:
```
{{ ((b / 255) * 100) | round(0, 'common') }}
```
(the 'common' mode is usually what you expect: rounds half-up rather than banker's rounding.)

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---
