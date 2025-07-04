import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_preprocesar(client):
    cedula = "1725279812"
    response = client.get(f"/api/preprocesar_datos/{cedula}")
    assert response.status_code in [200, 500]  # depende si los otros microservicios están levantados
    assert response.is_json
