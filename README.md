Collaboration management/monitoring dashboard for CUCM, CMS & Expressway.

Also includes a provisioning system for CUCM to manage users, extension and devices.

This is mainly a template for a frontend dashboard portal without the backend logic. Data is either generated with JS in the frontend or provided by a mock backend script. This makes the frontend fully functional and with the option to replace the backend to use real data.

To setup the DB with a local user:<br>
From the virtual environment, run: flask shell<br>
At the prompt run this:

from app import db; from models import User; db.create_all(); u = User(username='admin'); u.set_password('test123'); u.role = 'admin'; db.session.add(u); db.session.commit()

It will create user "admin" with password "test123"
