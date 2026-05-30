"""
Tests de integración para los endpoints de la API.
Usa el TestClient de FastAPI para no levantar el servidor.
"""


class TestPostReports:
    """POST /reports — subir un XML y obtener un report_id."""

    def test_upload_valid_xml_returns_report_id(self, client, sample_xml_bytes):
        response = client.post(
            "/reports",
            files={"file": ("report.xml", sample_xml_bytes, "application/xml")},
        )
        assert response.status_code == 200
        body = response.json()
        assert "report_id" in body
        assert isinstance(body["report_id"], str)
        assert len(body["report_id"]) > 0

    def test_each_upload_creates_unique_id(self, client, sample_xml_bytes):
        ids = set()
        for _ in range(3):
            response = client.post(
                "/reports",
                files={"file": ("r.xml", sample_xml_bytes, "application/xml")},
            )
            ids.add(response.json()["report_id"])
        assert len(ids) == 3


class TestGetSummary:
    """GET /summary/{report_id} — resumen por severidad."""

    def test_get_existing_summary(self, client, sample_xml_bytes):
        upload = client.post(
            "/reports",
            files={"file": ("r.xml", sample_xml_bytes, "application/xml")},
        )
        report_id = upload.json()["report_id"]

        response = client.get(f"/summary/{report_id}")
        assert response.status_code == 200
        summary = response.json()
        assert summary == {"critical": 1, "high": 1, "medium": 1, "low": 1}

    def test_get_nonexistent_summary_returns_404(self, client):
        response = client.get("/summary/no-existe-este-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Report not found"


class TestGetReportById:
    """GET /reports/{report_id} — reporte completo."""

    def test_get_existing_report(self, client, sample_xml_bytes):
        upload = client.post(
            "/reports",
            files={"file": ("r.xml", sample_xml_bytes, "application/xml")},
        )
        report_id = upload.json()["report_id"]

        response = client.get(f"/reports/{report_id}")
        assert response.status_code == 200
        body = response.json()
        assert "summary" in body
        assert "vulnerabilities" in body
        assert len(body["vulnerabilities"]) == 4

    def test_get_nonexistent_report_returns_404(self, client):
        response = client.get("/reports/no-existe")
        assert response.status_code == 404

    def test_vulnerability_json_has_expected_shape(self, client, sample_xml_bytes):
        upload = client.post(
            "/reports",
            files={"file": ("r.xml", sample_xml_bytes, "application/xml")},
        )
        report_id = upload.json()["report_id"]
        body = client.get(f"/reports/{report_id}").json()

        vuln = body["vulnerabilities"][0]
        expected_keys = {
            "severity", "cvss_score", "cve", "host", "port",
            "name", "family", "description", "impact", "solution",
        }
        assert set(vuln.keys()) == expected_keys


class TestPdfDownload:
    """GET /report/{report_id}/pdf — descarga PDF generado."""

    def test_download_existing_pdf(self, client, sample_xml_bytes, tmp_path, monkeypatch):
        # Cambiamos cwd para que el PDF temporal se genere en tmp_path
        # y no contamine el repo durante los tests.
        monkeypatch.chdir(tmp_path)

        upload = client.post(
            "/reports",
            files={"file": ("r.xml", sample_xml_bytes, "application/xml")},
        )
        report_id = upload.json()["report_id"]

        response = client.get(f"/report/{report_id}/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        # Los PDFs siempre comienzan con la firma %PDF-
        assert response.content[:5] == b"%PDF-"

    def test_download_nonexistent_pdf_returns_404(self, client):
        response = client.get("/report/no-existe/pdf")
        assert response.status_code == 404


class TestEndToEndFlow:
    """Flujo completo: subir → consultar summary → consultar reporte → descargar PDF."""

    def test_full_flow(self, client, sample_xml_bytes, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        # 1. Upload
        upload = client.post(
            "/reports",
            files={"file": ("r.xml", sample_xml_bytes, "application/xml")},
        )
        assert upload.status_code == 200
        report_id = upload.json()["report_id"]

        # 2. Summary
        summary = client.get(f"/summary/{report_id}")
        assert summary.status_code == 200
        assert sum(summary.json().values()) == 4

        # 3. Reporte completo
        report = client.get(f"/reports/{report_id}")
        assert report.status_code == 200

        # 4. PDF
        pdf = client.get(f"/report/{report_id}/pdf")
        assert pdf.status_code == 200
        assert len(pdf.content) > 100  # No vacío


class TestHealthCheck:
    """GET /health — endpoint de salud para Docker."""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "environment" in body
        assert "version" in body
