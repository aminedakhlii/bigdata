from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba2451'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

import routes
