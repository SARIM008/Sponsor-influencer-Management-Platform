from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('Config.Config')  # Ensure you have a Config class in your config module
db = SQLAlchemy(app)
