# Script de validación del despliegue local con Docker Compose.
# Levanta el contenedor, espera a que esté healthy, prueba los endpoints
# críticos y reporta resultado.
#
# Uso:
#   .\scripts\validate_deployment.ps1

$ErrorActionPreference = "Stop"
$BaseUrl = "http://localhost:8000"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "  [FAIL] $msg" -ForegroundColor Red
    exit 1
}

Write-Step "1. Levantando contenedor con docker-compose..."
docker-compose up -d --build
if ($LASTEXITCODE -ne 0) { Write-Fail "docker-compose up fallo" }
Write-Ok "Contenedor levantado"

Write-Step "2. Esperando a que el health check pase (max 60s)..."
$maxAttempts = 12
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 5
    $attempt++
    $status = docker inspect --format='{{.State.Health.Status}}' openvas-enhancer 2>$null
    Write-Host "  Intento $attempt/$maxAttempts - status: $status"
    if ($status -eq "healthy") {
        $healthy = $true
        break
    }
}

if (-not $healthy) {
    Write-Fail "El contenedor no llego a estado healthy en 60s"
}
Write-Ok "Contenedor reporta healthy"

Write-Step "3. Probando endpoint GET /health..."
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
    if ($response.status -ne "ok") { Write-Fail "/health no respondio status=ok" }
    Write-Ok "/health respondio: status=$($response.status), env=$($response.environment), version=$($response.version)"
} catch {
    Write-Fail "Error al llamar /health: $_"
}

Write-Step "4. Probando endpoint GET /docs (Swagger UI)..."
try {
    $resp = Invoke-WebRequest -Uri "$BaseUrl/docs" -Method Get -UseBasicParsing
    if ($resp.StatusCode -ne 200) { Write-Fail "/docs respondio $($resp.StatusCode)" }
    Write-Ok "/docs accesible (Swagger UI disponible)"
} catch {
    Write-Fail "Error al llamar /docs: $_"
}

Write-Step "5. Probando endpoint GET /summary/no-existe (debe dar 404)..."
try {
    Invoke-RestMethod -Uri "$BaseUrl/summary/no-existe" -Method Get
    Write-Fail "Esperabamos 404 pero la peticion fue exitosa"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 404) {
        Write-Ok "/summary/no-existe respondio 404 como esperado"
    } else {
        Write-Fail "Codigo inesperado: $($_.Exception.Response.StatusCode.value__)"
    }
}

Write-Step "6. Probando upload real de un XML..."
$xmlPath = "tests\fixtures\sample_openvas_report.xml"
if (-not (Test-Path $xmlPath)) { Write-Fail "No se encontro $xmlPath" }

try {
    # Construir multipart/form-data manualmente (compatible con PowerShell 5.1)
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    $fileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $xmlPath))
    $fileContent = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes)

    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"sample.xml`"",
        "Content-Type: application/xml$LF",
        $fileContent,
        "--$boundary--$LF"
    ) -join $LF

    $upload = Invoke-RestMethod -Uri "$BaseUrl/reports" -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines

    if (-not $upload.report_id) { Write-Fail "El upload no devolvio report_id" }
    Write-Ok "Upload exitoso, report_id=$($upload.report_id)"

    $summary = Invoke-RestMethod -Uri "$BaseUrl/summary/$($upload.report_id)" -Method Get
    Write-Ok "/summary respondio: critical=$($summary.critical), high=$($summary.high), medium=$($summary.medium), low=$($summary.low)"
} catch {
    Write-Fail "Error en flujo de upload: $_"
}

Write-Host ""
Write-Host "==> VALIDACION DE DESPLIEGUE COMPLETADA EXITOSAMENTE" -ForegroundColor Green
Write-Host ""
Write-Host "Tu API esta corriendo en: $BaseUrl"
Write-Host "Swagger UI disponible en: $BaseUrl/docs"
Write-Host "Para detener el contenedor: docker-compose down"
Write-Host ""
