"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

from fastapi import Request
# In-memory activity database (shared)
from src.activities_db import activities_db
from fastapi import Depends

def get_activities_db():
    return activities_db

# Unregister a participant from an activity
@app.post("/activities/{activity}/unregister")
async def unregister_participant(activity: str, email: str, db=Depends(get_activities_db)):
    if activity not in db:
        raise HTTPException(status_code=404, detail="Activity not found")
    participants = db[activity]["participants"]
    if email not in participants:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")
    participants.remove(email)
    return {"message": f"{email} has been removed from {activity}."}




@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")



@app.get("/activities")
def get_activities(db=Depends(get_activities_db)):
    return db



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db=Depends(get_activities_db)):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in db:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = db[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
