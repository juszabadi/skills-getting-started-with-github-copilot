import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


TEST_ACTIVITY = "Basketball Team"
TEST_EMAIL = "test-student@mergington.edu"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_participants():
    original_participants = {
        name: activity["participants"].copy()
        for name, activity in activities.items()
    }

    yield

    for name, participants in original_participants.items():
        activities[name]["participants"][:] = participants


def test_get_activities_returns_all_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client):
    # Arrange
    activity = TEST_ACTIVITY
    email = TEST_EMAIL

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activities[TEST_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activities[TEST_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/participants",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {TEST_EMAIL} from {TEST_ACTIVITY}"
    }
    assert TEST_EMAIL not in client.get("/activities").json()[TEST_ACTIVITY][
        "participants"
    ]


def test_unregister_rejects_unregistered_participant(client):
    # Arrange

    # Act
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/participants",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student not signed up for this activity"
    }


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
