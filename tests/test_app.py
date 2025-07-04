import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_preprocesar(client):
    # Simula una petición POST con un ID válido
    response = client.post('/api/preprocesar', json={"id": "1725279812"})
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert "resultado" in data
