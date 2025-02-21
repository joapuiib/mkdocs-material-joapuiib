---
template: exam.html
title: Exam
icon: material/lock
inject_id: protected
password: 1234
start_time: 2024-10-21 12:30:00
---

## Exam
La contrasenya és `1234`.

---

/// html | div#protected
## Contingut
Aquest contingut està protegit per contrasenya.

### Hola
### Exercici 1

```mermaid
classDiagram
    class Lamp {
        - consumption: double
        - on: boolean
        + Lamp(consumption: double)
        + Lamp(consumption: double, on: boolean)
        + isOn(): boolean
        + getConsumption(): double
        + turnOn(): void
        + turnOff(): void
        + toggle(): void
        + consume(seconds: double): double
    }
```

$$
kW = kWh \cdot \frac{seconds}{3600}
$$
///
