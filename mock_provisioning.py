from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, Task, create_app
from runner import run_task
from backend import provisioning_logic
import uuid
import json
import threading
import time

app = create_app()
CORS(app)

last_sync_time = time.time()

def ensure_tables_exist():
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if 'task' not in tables:
            print("[DB] Tables missing, creating...")
            db.create_all()
        else:
            print("[DB] Tables already exist, skipping create_all().")

ensure_tables_exist()

# Simulated steps
SIMULATED_STEPS = {
    "Manual Provisioning": [
        "Creating user...",
        "Assigning extension...",
        "Provisioning phone...",
        "Finalizing settings..."
    ],
    "Modify Extension": [
        "Fetching user data...",
        "Reassigning extension...",
        "Updating device config...",
        "Saving changes..."
    ],
    "Delete Services": [
        "Fetching associated devices...",
        "Unassigning extension...",
        "Removing user services...",
        "Cleanup complete..."
    ]
}

# Simulate task progress
def simulate_provisioning(task_id):
    with app.app_context():
        time.sleep(1)
        task = Task.query.get(task_id)
        if not task:
            print(f"[Simulate] Task {task_id} not found.")
            return

        if task.extension == "auto":
            task.extension = 9999

        steps = json.loads(task.steps)

        for step in steps:
            step["status"] = "done"
            task.steps = json.dumps(steps)
            task.last_updated = time.time()
            db.session.commit()
            time.sleep(3)

        task.status = "Success"
        task.last_updated = time.time()
        db.session.commit()

# API: Start provisioning
@app.route("/api/provision", methods=["POST"])
def provision_user():
    data = request.json
    user_id = data.get("user")
    extension = data.get("extension", "auto")
    action = data.get("type", "Manual Provisioning")
    source = data.get("source", "Manual")
    triggered_by = data.get("triggered_by", "Unknown")
    task_id = str(uuid.uuid4())

    new_task = Task(
        id=task_id,
        user=user_id,
        extension=extension,
        action=action,
        source=source,
        triggered_by=triggered_by,
        status="Running",
        steps=json.dumps([]),
        created=time.time(),
        last_updated=time.time()
    )
    db.session.add(new_task)
    db.session.commit()
    print("Start Provisiong")
    threading.Thread(target=run_task, args=(app, task_id, provisioning_logic, user_id, extension, source), daemon=True).start()

    return jsonify({"task_id": task_id})

# API: Get task status
@app.route("/api/task-status/<task_id>")
def get_task_status(task_id):
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Timeout protection
        max_task_duration = 300  # seconds (5 minutes)
        if task.status == "Running" and (time.time() - task.last_updated > max_task_duration):
            steps = json.loads(task.steps)
            for step in steps:
                print(type(step), step)
                if type(step) == str:
                    pass
                elif step["status"] == "pending":
                    step["status"] = "failed"
            task.steps = json.dumps(steps)
            task.status = "Failed"
            db.session.commit()
            print(f"[Timeout] Task {task_id} marked as Failed due to timeout.")

        return jsonify({
            "id": task.id,
            "user": task.user,
            "extension": task.extension,
            "action": task.action,
            "source": task.source,
            "status": task.status,
            "triggered_by": task.triggered_by,
            "timestamp": task.created,
            "steps": json.loads(task.steps)
        })

# API: Full task history
@app.route("/api/task-history")
def get_task_history():
    since = request.args.get("since")
    if since:
        cutoff = time.time() - 3600 * int(since[:-1])
        tasks = Task.query.filter(Task.created >= cutoff).order_by(Task.created.desc()).all()
    else:
        tasks = Task.query.order_by(Task.created.desc()).all()

    return jsonify([
        {
            "id": task.id,
            "user": task.user,
            "extension": task.extension,
            "action": task.action,
            "source": task.source,
            "status": task.status,
            "triggered_by": task.triggered_by,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task.created)),
            "steps": json.loads(task.steps)
        }
        for task in tasks
    ])

# API to trigger LDAP sync (mock)
@app.route("/api/ldap-sync", methods=["POST"])
def ldap_sync():
    global last_sync_time

    if time.time() - last_sync_time < 300:
        return jsonify({"status": "warning", "message": "LDAP Sync in progress... Wait at least 5 min and try again."})
    else:
        last_sync_time = time.time()

    # For now just simulate delay
    time.sleep(3)
    return jsonify({"status": "success", "message": "LDAP Sync finished."})

# API to trigger Auto Provisioning
@app.route("/api/auto-provision", methods=["POST"])
def auto_provision():

    time.sleep(3)
    return jsonify({"status": "success", "message": "Auto Provisioning Finished - 0 new users found."})


if __name__ == "__main__":
    app.run(debug=True, port=9999)
