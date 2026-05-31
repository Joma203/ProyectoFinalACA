# ProyectoFinalACA
# Guia de instalacion
## Despliegue local con Docker

### Requisitos
- Docker Desktop instalado y corriendo

### Despliegue paso a paso

1. **Copia el archivo de variables de entorno:**
```powershell
   Copy-Item .env.example .env
```
   Edita `.env` si necesitas cambiar puerto, log level, etc.

2. **Levanta el contenedor:**
```powershell
   docker-compose up -d --build
```

3. **Valida el despliegue automáticamente:**
```powershell
   .\scripts\validate_deployment.ps1
```
   Este script levanta el contenedor, espera al health check, prueba los endpoints críticos y reporta resultado.

4. **Accede a la API:**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Variables de entorno disponibles

| Variable | Default | Descripción |
|----------|---------|-------------|
| `APP_NAME` | OpenVAS Analyzer API | Nombre mostrado en Swagger |
| `APP_VERSION` | 1.0.0 | Versión de la API |
| `HOST` | 0.0.0.0 | Host del servidor uvicorn |
| `PORT` | 8000 | Puerto expuesto |
| `LOG_LEVEL` | info | Nivel de log (debug, info, warning, error) |
| `ENVIRONMENT` | development | Entorno (development, testing, production) |

### Health check

El contenedor incluye un health check automático que pega cada 30s a `/health`. Para ver el estado:

```powershell
docker inspect --format='{{.State.Health.Status}}' openvas-enhancer
```

Valores posibles: `starting`, `healthy`, `unhealthy`.

### Detener el servicio

```powershell
docker-compose down
```
# Manual de usuario

## OpenVAS Analyzer API
---

# 1. Introducción

OpenVAS Analyzer API es una aplicación diseñada para procesar reportes XML generados por OpenVAS y convertirlos en información estructurada que facilite el análisis de vulnerabilidades.

La aplicación permite:

* Cargar reportes XML de OpenVAS.
* Procesar automáticamente las vulnerabilidades detectadas.
* Consultar resúmenes de resultados.
* Visualizar información detallada del análisis.
* Generar reportes en formato PDF.

---

# 2. Objetivo del Sistema

Automatizar el procesamiento de reportes de vulnerabilidades generados por OpenVAS, facilitando la identificación y análisis de riesgos de seguridad.

---

# 3. Acceso a la Aplicación

Una vez iniciada la aplicación, la documentación interactiva estará disponible en:

```text
http://localhost:8000/docs
```

Documentación alternativa:

```text
http://localhost:8000/redoc
```

---

# 4. Flujo General de Uso

1. Generar un reporte XML desde OpenVAS.
2. Cargar el archivo XML en la API.
3. Obtener el identificador del reporte.
4. Consultar el resumen generado.
5. Consultar el reporte completo.
6. Descargar el reporte PDF.

---

# 5. Carga de Reportes XML

## Endpoint

```http
POST /reports
```

## Procedimiento

1. Ingresar a Swagger UI.
2. Seleccionar el endpoint POST /reports.
3. Presionar "Try it out".
4. Seleccionar el archivo XML exportado desde OpenVAS.
5. Presionar "Execute".

## Respuesta

```json
{
  "report_id": "abc123"
}
```

El valor report_id identifica el reporte procesado y será necesario para las consultas posteriores.

---

# 6. Consulta de Resumen

## Endpoint

```http
GET /summary/{report_id}
```

## Descripción

Devuelve un resumen de las vulnerabilidades encontradas durante el análisis.

---

# 7. Consulta de Reporte Completo

## Endpoint

```http
GET /reports/{report_id}
```

## Información mostrada

* Vulnerabilidades detectadas.
* CVEs asociados.
* Hosts afectados.
* Puertos vulnerables.
* Severidad.
* Puntuación CVSS.
* Descripción técnica.
* Soluciones recomendadas.

---

# 8. Generación de Reporte PDF

## Endpoint

```http
GET /report/{report_id}/pdf
```

## Procedimiento

1. Obtener el report_id después de cargar el XML.
2. Ejecutar el endpoint de descarga.
3. Descargar el archivo PDF generado.

Nombre del archivo:

```text
report.pdf
```

---

# 9. Verificación del Estado del Sistema

## Endpoint

```http
GET /health
```

## Respuesta esperada

```json
{
  "status": "ok",
  "environment": "development",
  "version": "1.0.0"
}
```

---

# 10. Interpretación de Severidades

| Severidad | Descripción                                    |
| --------- | ---------------------------------------------- |
| Critical  | Riesgo crítico que requiere atención inmediata |
| High      | Riesgo alto                                    |
| Medium    | Riesgo moderado                                |
| Low       | Riesgo bajo                                    |

---

# 11. Mensajes de Error

## Reporte no encontrado

```json
{
  "detail": "Report not found"
}
```

Código HTTP:

```http
404 Not Found
```

---

# 12. Recomendaciones

* Utilizar únicamente archivos XML exportados desde OpenVAS.
* Conservar el report_id generado.
* Revisar primero las vulnerabilidades críticas y altas.
* Descargar y respaldar los reportes PDF.
* Restringir el acceso a los reportes debido a la información sensible que contienen.
