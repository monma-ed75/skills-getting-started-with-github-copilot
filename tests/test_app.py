from fastapi.testclient import TestClient
import copy
import pytest

from src.app import app, activities

client = TestClient(app)

# Snapshot the original activities so each test runs with a fresh copy
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    email = "newstudent@example.com"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert "Signed up" in resp.json()["message"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_duplicate_signup():
    existing = ORIGINAL_ACTIVITIES["Chess Club"]["participants"][0]
    resp = client.post("/activities/Chess Club/signup", params={"email": existing})
    assert resp.status_code == 400


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307)
    assert resp.headers["location"] == "/static/index.html"
