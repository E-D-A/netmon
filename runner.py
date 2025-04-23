from models import db, Task
import json
import time

def run_task(app, task_id, task_function, *args, **kwargs):
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            print(f"[TaskRunner] Task {task_id} not found!")
            return

        try:
            task_function(task_id, *args, **kwargs)

            task.status = "Success"
            task.last_updated = time.time()
            db.session.commit()

        except Exception as e:
            print(f"[TaskRunner] Exception: {str(e)}")
            steps = json.loads(task.steps)
            for step in steps:
                if step["status"] == "pending":
                    step["status"] = "failed"
            task.steps = json.dumps(steps)
            task.status = "Failed"
            task.last_updated = time.time()
            db.session.commit()
