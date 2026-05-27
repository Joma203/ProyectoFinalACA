"""
Configuración global de pytest.
Las fixtures definidas aquí están disponibles en todos los tests
sin necesidad de importarlas.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Asegurar que el paquete `app` sea importable cuando se corre pytest
# desde la raíz del proyecto.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402
from app.storage import memory_store  # noqa: E402


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_xml_bytes():
    """Contenido binario de un reporte OpenVAS válido."""
    path = FIXTURES_DIR / "sample_openvas_report.xml"
    return path.read_bytes()


@pytest.fixture
def sample_xml_path():
    """Ruta al archivo XML de ejemplo."""
    return FIXTURES_DIR / "sample_openvas_report.xml"


@pytest.fixture
def malformed_xml_bytes():
    """Contenido binario de un XML malformado."""
    path = FIXTURES_DIR / "malformed_report.xml"
    return path.read_bytes()


@pytest.fixture
def client():
    """Cliente HTTP de pruebas para la API FastAPI."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_memory_store():
    """
    Limpia el store en memoria antes de cada test para que
    no se contamine entre pruebas.
    """
    memory_store.REPORTS.clear()
    yield
    memory_store.REPORTS.clear()
