# ProyectoFinalACA
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
