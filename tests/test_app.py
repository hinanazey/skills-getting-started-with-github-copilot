
import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from src.activities_db import activities_db
def reset_activities_db():
    for activity in activities_db.values():
        activity['participants'].clear()


@pytest.mark.asyncio
async def test_get_activities():
    reset_activities_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all('description' in v and 'participants' in v for v in data.values())

@pytest.mark.asyncio
async def test_signup_and_unregister():
    reset_activities_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get an activity name
        resp_activities = await ac.get("/activities")
        activities = resp_activities.json()
        print("Available activities:", list(activities.keys()))
        activity = next(iter(activities.keys()))
        print("Selected activity:", activity)
        test_email = "testuser@mergington.edu"
        # Sign up
        resp_signup = await ac.post(f"/activities/{activity}/signup?email={test_email}")
        print("Signup status:", resp_signup.status_code, resp_signup.text)
        assert resp_signup.status_code == 200
        # Check participant added
        resp_activities = await ac.get("/activities")
        print("Participants after signup:", resp_activities.json()[activity]['participants'])
        assert test_email in resp_activities.json()[activity]['participants']
        # Unregister
        resp_unreg = await ac.post(f"/activities/{activity}/unregister?email={test_email}")
        print("Unregister status:", resp_unreg.status_code, resp_unreg.text)
        assert resp_unreg.status_code == 200
        # Check participant removed
        resp_activities2 = await ac.get("/activities")
        print("Participants after unregister:", resp_activities2.json()[activity]['participants'])
        assert test_email not in resp_activities2.json()[activity]['participants']
