from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from flask import request, jsonify

app = Flask(__name__)
CORS(app)

# Replace this with your Render External DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# MODELS
# ----------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------------
# TEST ROUTE
# ----------------------

@app.route("/")


def home():
    return "Reminder Backend Running 🚀"
@app.route("/check-tables")
def check_tables():
    tables = db.engine.table_names()
    return {"tables": tables}

# ----------------------
# REGISTER USER
# ----------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(
        name=name,
        email=email,
        password=password  # (we will hash later)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# ----------------------
# LOGIN USER
# ----------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.password != password:
        return jsonify({"message": "Incorrect password"}), 401

    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "name": user.name
    }), 200
# ----------------------
# ADD REMINDER
# ----------------------

@app.route("/add-reminder", methods=["POST"])
def add_reminder():
    data = request.get_json()

    user_id = data.get("user_id")
    title = data.get("title")
    date = data.get("date")  # format: YYYY-MM-DD
    reminder_type = data.get("type")

    from datetime import datetime

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    new_reminder = Reminder(
        user_id=user_id,
        title=title,
        date=date_obj,
        type=reminder_type
    )

    db.session.add(new_reminder)
    db.session.commit()

    return jsonify({"message": "Reminder added successfully"}), 201
# ----------------------
# GET REMINDERS
# ----------------------

@app.route("/reminders/<int:user_id>", methods=["GET"])
def get_reminders(user_id):
    reminders = Reminder.query.filter_by(user_id=user_id).all()

    result = []

    for r in reminders:
        result.append({
            "id": r.id,
            "title": r.title,
            "date": r.date.strftime("%Y-%m-%d"),
            "type": r.type
        })

    return jsonify(result), 200

# ----------------------
# CREATE TABLES
# ----------------------

with app.app_context():
    db.create_all()
    print("Tables Created Successfully ✅")

if __name__ == "__main__":
    app.run(debug=True)