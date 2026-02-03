from flask import Flask
from models import db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mad1-secret-key'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# THIS LINE FIXES my ERROR of accessing issue
os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, 'database', 'db.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return "Placement Portal App - MAD I"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
