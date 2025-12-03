# Flight Journey Search – FastAPI Challenge

Este proyecto implementa un servicio HTTP que permite:

- Obtener eventos de vuelo desde un JSON local.
- Buscar journeys (viajes) entre dos ciudades para una fecha dada.
- Aplicar reglas de conexión:
  - Conexiones < **4 horas**
  - Duración total del viaje < **24 horas**
  - Orden cronológico válido

El backend está construido con **FastAPI**, **Poetry** y arquitectura modular usando **Dependency Injector**.

---

## 1. Requisitos previos

Necesitás:

- Python **3.12+**
- Poetry instalado

Si no tenés Poetry:

```bash
pip install poetry
```

---

## 2. Instalación de dependencias

Cloná el repositorio y ubicáte en el proyecto:

```bash
git clone https://github.com/MauroPerna/flight-journey-search
cd flight-journey-search
```

Instalá dependencias:

```bash
poetry install
```

Activá el entorno virtual creado por Poetry:

```bash
# primero instala el plugin para activar el entorno virtual
poetry self add poetry-plugin-shell
```

```bash
poetry shell
```

---

## 3. Ejecutar el servidor

### Opción A — usando Poetry (recomendada)

```bash
poetry run uvicorn main:app --reload --port 8000
```

### Opción B — usando Python directo

```bash
python main.py
```

El servidor quedará disponible en:

```
http://localhost:8000
```

---

## 4. Estructura del proyecto

```
src/
  main.py
  application/
    app.py
    container.py
    lifecycle.py
    register_modules.py
  domain/
    flight_events/
      controller.py
      module.py
      service.py
      flight_events.json
    journeys/
      controller.py
      module.py
      service.py
      test.py
  infrastructure/
    config/
      settings.py
```

---

## 5. Endpoints disponibles

---

### 5.1 Listar eventos de vuelo

```
GET /flight-events
```

Ejemplo:

```bash
curl http://localhost:8000/flight-events
```

---

### 5.2 Buscar journeys

```
GET /journeys/search?date=2025-02-01&from_city=EZE&to_city=MIA
```

Ejemplo con curl:

```bash
curl "http://localhost:8000/journeys/search?date=2025-02-01&from_city=EZE&to_city=MIA"
```

---

## 6. Ejecutar tests

```bash
poetry run pytest
```

---

