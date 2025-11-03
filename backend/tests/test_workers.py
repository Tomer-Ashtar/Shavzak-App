from fastapi.testclient import TestClient
import random
from app.main import app
from app.init_db import init_db


init_db()
client = TestClient(app)


def test_workers_crud_flow():
    # Create
    name = f"Alice {random.randint(1000,9999)}"
    create_res = client.post(
        "/api/workers",
        json={
            "name": name,
            "title": "Engineer",
            "hard_chores_counter": 1,
            "outer_partner_counter": 0,
        },
    )
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    worker_id = created["id"]
    assert created["name"] == name

    # Get
    get_res = client.get(f"/api/workers/{worker_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == worker_id

    # List
    list_res = client.get("/api/workers")
    assert list_res.status_code == 200
    assert any(w["id"] == worker_id for w in list_res.json())

    # Update
    upd_res = client.put(
        f"/api/workers/{worker_id}",
        json={"title": "Senior Engineer", "hard_chores_counter": 2},
    )
    assert upd_res.status_code == 200
    upd = upd_res.json()
    assert upd["title"] == "Senior Engineer"
    assert upd["hard_chores_counter"] == 2

    # Delete
    del_res = client.delete(f"/api/workers/{worker_id}")
    assert del_res.status_code == 204

    # Not found after delete
    nf_res = client.get(f"/api/workers/{worker_id}")
    assert nf_res.status_code == 404

