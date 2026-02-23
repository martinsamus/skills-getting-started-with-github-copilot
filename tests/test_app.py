from urllib.parse import quote

import src.app as app_module


def _activity_path(activity_name: str) -> str:
    return quote(activity_name, safe="")


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity_count = len(app_module.activities)

    # Act
    response = client.get("/activities")
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert len(response_data) == expected_activity_count
    assert "Chess Club" in response_data


def test_signup_adds_new_student_when_activity_exists_and_has_capacity(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"
    signup_url = f"/activities/{_activity_path(activity_name)}/signup"

    # Act
    response = client.post(signup_url, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_returns_400_when_student_already_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]
    signup_url = f"/activities/{_activity_path(activity_name)}/signup"

    # Act
    response = client.post(signup_url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_400_when_activity_is_full(client):
    # Arrange
    activity_name = "Science Olympiad"
    max_participants = app_module.activities[activity_name]["max_participants"]
    app_module.activities[activity_name]["participants"] = [
        f"student{index}@mergington.edu" for index in range(max_participants)
    ]
    new_email = "late.student@mergington.edu"
    signup_url = f"/activities/{_activity_path(activity_name)}/signup"

    # Act
    response = client.post(signup_url, params={"email": new_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_returns_404_when_activity_does_not_exist(client):
    # Arrange
    missing_activity = "Robotics Club"
    signup_url = f"/activities/{_activity_path(missing_activity)}/signup"

    # Act
    response = client.post(signup_url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_student_when_enrolled(client):
    # Arrange
    activity_name = "Basketball Club"
    enrolled_email = app_module.activities[activity_name]["participants"][0]
    unregister_url = f"/activities/{_activity_path(activity_name)}/unregister"

    # Act
    response = client.post(unregister_url, params={"email": enrolled_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {enrolled_email} from {activity_name}"}
    assert enrolled_email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_404_when_student_not_in_activity(client):
    # Arrange
    activity_name = "Basketball Club"
    missing_email = "missing.student@mergington.edu"
    unregister_url = f"/activities/{_activity_path(activity_name)}/unregister"

    # Act
    response = client.post(unregister_url, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"


def test_unregister_returns_404_when_activity_does_not_exist(client):
    # Arrange
    missing_activity = "Robotics Club"
    unregister_url = f"/activities/{_activity_path(missing_activity)}/unregister"

    # Act
    response = client.post(unregister_url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"