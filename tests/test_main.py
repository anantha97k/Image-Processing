import pytest
from fastapi.testclient import TestClient
from main import app, get_db

from app.schemas.db_model import Users
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def test_endpoint_read_all_tasks():
    response = client.get("/")
    assert response.status_code == 200
    print(response)
    assert response.json() == {"test": 5}


def format_display(people) -> list:
    return [
        f"{item['given_name']} {item['family_name']}: {item['title']}"
        for item in people
    ]


def format_excel(people) -> str:

    header = "given,family,title"
    header += "\n"

    for line in people:
        header += ",".join(line.values()) + "\n"

    return header


@pytest.fixture
def people_data():
    return [
        {
            "given_name": "Alfonsa",
            "family_name": "Ruiz",
            "title": "Senior Software Engineer",
        },
        {
            "given_name": "Sayid",
            "family_name": "Khan",
            "title": "Project Manager",
        },
    ]


def test_format_display(people_data):
    assert format_display(people_data) == [
        "Alfonsa Ruiz: Senior Software Engineer",
        "Sayid Khan: Project Manager",
    ]


def test_format_excel(people_data):
    assert (
        format_excel(people_data)
        == """given,family,title
Alfonsa,Ruiz,Senior Software Engineer
Sayid,Khan,Project Manager
"""
    )


@pytest.fixture
def test_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_client(test_db_session):
    client = TestClient(app)
    app.dependency_overrides[get_db] = lambda: test_db_session
    return client


def test_client_can_add_read_the_item_from_database(test_client, test_db_session):

    response = test_client.get("/items/1")
    assert response.status_code == 404

    header = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = "username=d&password=e"

    response = test_client.post("/signup", headers=header, data=payload)
    assert response.status_code == 201

    user_id = response.json()
    user = test_db_session.query(Users).filter(Users.uid == user_id).first()
    assert user is not None

    response = response = test_client.get(f"/items/{user_id}")
    assert response.status_code == 200
