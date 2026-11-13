import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import get_db
from app.db.models import Base
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


BISHOP_REQUEST = {
    "method": "bishop",
    "geometry": {"height": 10.0, "angle": 26.565051},
    "slip_circle": {"center_x": 4.206, "center_y": 22.4018, "radius": 22.7932},
    "soil": {"cohesion": 10.0, "phi": 20.0, "gamma": 20.0, "ru": 0.25},
    "num_slices": 50,
}

FELLENIUS_REQUEST = {
    "method": "fellenius",
    "geometry": {"height": 10.0, "angle": 26.565051},
    "slip_circle": {"center_x": 5.9399, "center_y": 18.3567, "radius": 19.2938},
    "soil": {"cohesion": 10.0, "phi": 20.0, "gamma": 20.0, "ru": 0.25},
    "num_slices": 50,
}


def test_analyze_bishop(client):
    resp = client.post("/api/v1/analyze", json=BISHOP_REQUEST)
    assert resp.status_code == 201
    data = resp.json()
    assert data["method"] == "bishop"
    assert data["result"]["fs"] == pytest.approx(1.1001, rel=2e-2)
    assert data["result"]["converged"] is True
    assert data["result"]["iterations"] >= 1


def test_analyze_fellenius(client):
    resp = client.post("/api/v1/analyze", json=FELLENIUS_REQUEST)
    assert resp.status_code == 201
    data = resp.json()
    assert data["method"] == "fellenius"
    assert data["result"]["fs"] == pytest.approx(1.0768, rel=2e-2)
    assert data["result"]["iterations"] is None
    assert data["result"]["converged"] is None


def test_invalid_method_returns_422(client):
    req = {**BISHOP_REQUEST, "method": "janbu"}
    resp = client.post("/api/v1/analyze", json=req)
    assert resp.status_code == 422


def test_invalid_input_returns_422(client):
    req = {**BISHOP_REQUEST, "soil": {**BISHOP_REQUEST["soil"], "gamma": 0}}
    resp = client.post("/api/v1/analyze", json=req)
    assert resp.status_code == 422


def test_list_analyses(client):
    client.post("/api/v1/analyze", json=BISHOP_REQUEST)
    client.post("/api/v1/analyze", json=FELLENIUS_REQUEST)
    resp = client.get("/api/v1/analyses")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["method"] == "bishop"
    assert data[1]["method"] == "fellenius"
