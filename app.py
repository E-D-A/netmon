# app.py
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_required, current_user
from functools import wraps
from models import db, User
from auth import auth

app = Flask(__name__)
app.secret_key = 'dev-key'  # change in prod
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netmon.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return "Access Denied", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Dashboard route
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# PROD1 Collaboration Overview and systems
@app.route('/collaboration/prod1')
def collab_prod1():
    return render_template('collaboration/prod1/collab_prod1.html')

@app.route('/collaboration/prod1/cucm')
def cucm_prod1():
    return render_template('collaboration/prod1/cucm_prod1.html')

@app.route('/collaboration/prod1/cms')
def cms_prod1():
    return render_template('collaboration/prod1/cms_prod1.html')

@app.route('/collaboration/prod1/expressway')
def expressway_prod1():
    return render_template('collaboration/prod1/expressway_prod1.html')

# PROD2 Collaboration Overview and systems
@app.route('/collaboration/prod2')
def collab_prod2():
    return render_template('collaboration/prod2/collab_prod2.html')

@app.route('/collaboration/prod2/cucm')
def cucm_prod2():
    return render_template('collaboration/prod2/cucm_prod2.html')

@app.route('/collaboration/prod2/cms')
def cms_prod2():
    return render_template('collaboration/prod2/cms_prod2.html')

@app.route('/collaboration/prod2/expressway')
def expressway_prod2():
    return render_template('collaboration/prod2/expressway_prod2.html')

@app.route('/provisioning')
@login_required
def provisioning():
    return render_template('provisioning.html')

@app.route("/task-history")
def task_history_page():
    return render_template("task_history.html")

@app.route('/usermgmt', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def manage_users():
    users = User.query.all()

    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        new_role = request.form['role']

        # Prevent changing your own role
        if user_id == current_user.id:
            flash("You cannot change your own role.", "warning")
            return redirect(url_for('manage_users'))

        user = User.query.get(user_id)
        if user:
            old_role = user.role
            user.role = new_role
            db.session.commit()
            flash(f"Updated {user.username}'s role from {old_role} to {new_role}.", "success")
        else:
            flash("User not found.", "danger")
        return redirect(url_for('manage_users'))

    return render_template('manage_users.html', users=users)

if __name__ == '__main__':
    # Consider setting host='0.0.0.0' if deploying outside localhost
    app.run(debug=True)
