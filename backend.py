from models import db, Task
import json
import time

PROVISIONING_STEPS = {
    "Provisioning": [
        "Connecting to CUCM...",
        "Assigning extension...",
        "Provisioning Jabber...",
        "Provisioning Device Profile...",
        "Configure user...",
        "Setup IM&Provisioning..."
    ],
    "Modify Extension": [
        "Connecting to CUCM...",
        "Fetching user data...",
        "Reassigning extension...",
        "Updating device config...",
        "Saving changes..."
    ],
    "Delete Services": [
        "Connecting to CUCM...",
        "Fetching associated devices...",
        "Unassigning extension...",
        "Removing user services...",
        "Cleanup complete..."
    ]
}

def provisioning_logic(task_id, user_id, extension, source="auto"):
    task = Task.query.get(task_id)
    steps = [{"label": step, "status": "pending"} for step in PROVISIONING_STEPS["Provisioning"]]

    if task.extension == "auto":
        task.extension = 9999

    task.steps = json.dumps(steps)
    task.last_updated = time.time()
    db.session.commit()

    # Simulate work
    steps = json.loads(task.steps)

    for step in steps:
        step["status"] = "done"
        task.steps = json.dumps(steps)
        task.last_updated = time.time()
        db.session.commit()
        time.sleep(3)

    steps.append({"label": f"Provisioned extension {extension} for user {user_id}", "status": "done"})
    task.steps = json.dumps(steps)
    task.last_updated = time.time()
    db.session.commit()
    
    if source == "auto":
        steps.append({"label": f"Send email notification...", "status": "done"})
        task.steps = json.dumps(steps)
        task.last_updated = time.time()
        db.session.commit()
