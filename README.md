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
<img width="958" height="596" alt="image" src="https://github.com/user-attachments/assets/cee5e190-76c5-4d17-b9b7-1256414a3463" />
<img width="943" height="614" alt="image" src="https://github.com/user-attachments/assets/5c9beb9c-188d-44c7-89b6-a26aa83443ff" />


3. **Valida el despliegue automáticamente:**
```powershell
   .\scripts\validate_deployment.ps1
```
   Este script levanta el contenedor, espera al health check, prueba los endpoints críticos y reporta resultado.

   <img width="948" height="607" alt="image" src="https://github.com/user-attachments/assets/43f4a782-d2e8-41bd-9eed-89d4123c8e28" />


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
<img width="1366" height="675" alt="image" src="https://github.com/user-attachments/assets/56c3370d-99a3-4b19-a98c-019da382fb95" />


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
<img width="1366" height="598" alt="image" src="https://github.com/user-attachments/assets/d485c78a-2877-4a25-ba7d-5734d14a781e" />

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
<img width="1366" height="596" alt="image" src="https://github.com/user-attachments/assets/80330adc-d241-4e4e-b47d-d01ee3e27360" />

# 6. Consulta de Resumen

## Endpoint

```http
GET /summary/{report_id}
```
<img width="1366" height="597" alt="image" src="https://github.com/user-attachments/assets/cb0b5062-e3ea-4119-bc42-e21cc3202751" />

## Descripción

Devuelve un resumen de las vulnerabilidades encontradas durante el análisis.

---
<img width="1366" height="601" alt="image" src="https://github.com/user-attachments/assets/90750d53-144c-45fe-9a7c-bf1c069bfda9" />

# 7. Consulta de Reporte Completo

## Endpoint

```http
GET /reports/{report_id}
```
<img width="1366" height="595" alt="image" src="https://github.com/user-attachments/assets/2504be84-6e65-41c2-b622-8c050c418b07" />

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
<img width="1366" height="597" alt="image" src="https://github.com/user-attachments/assets/ed690a04-596b-423a-86e9-16cb20951144" />

# 8. Generación de Reporte PDF

## Endpoint

```http
GET /report/{report_id}/pdf
```
<img width="1366" height="597" alt="image" src="https://github.com/user-attachments/assets/2963428b-e74b-4476-afdf-61d97d14dab8" />

## Procedimiento

1. Obtener el report_id después de cargar el XML.
2. Ejecutar el endpoint de descarga.
3. Descargar el archivo PDF generado.

Nombre del archivo:

```text
report.pdf
```

---
<img width="1366" height="596" alt="image" src="https://github.com/user-attachments/assets/ce364376-48d7-48fb-b8e6-64bc37e57a02" />


<img width="1366" height="676" alt="image" src="https://github.com/user-attachments/assets/1a822952-39ef-475e-918a-9b9f4250decb" />

# 9. Verificación del Estado del Sistema

## Endpoint

```http
GET /health
```
<img width="1363" height="598" alt="image" src="https://github.com/user-attachments/assets/b90867f0-8de9-412b-98c9-e323e6b5b38a" />

## Respuesta esperada

```json
{
  "status": "ok",
  "environment": "development",
  "version": "1.0.0"
}
```
<img width="1366" height="599" alt="image" src="https://github.com/user-attachments/assets/a53da3b0-d689-4675-b552-66d6bfbf467a" />

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
