from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mlfjdsaflfj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.bd'
db = SQLAlchemy(app)

from routes import *


if __name__ == '__main__':
   app.run(debug = True)


