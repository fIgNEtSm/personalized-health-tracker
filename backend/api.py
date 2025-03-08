from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

app = Flask(__name__)

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    diseases = db.Column(db.String(200))  # Example: "Diabetes, Hypertension"


class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=db.func.current_date())
    food_item = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float)
    nutrients = db.Column(db.Text)  # JSON data stored as a string


class HealthLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=db.func.current_date())
    heart_rate = db.Column(db.Float)
    blood_pressure = db.Column(db.String(10))  # Example: "120/80"
    glucose_level = db.Column(db.Float)  # mg/dL


class UserStreak(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    streak_count = db.Column(db.Integer, default=0)
    last_logged = db.Column(db.Date)


@app.route('/users', methods=['GET'])
@app.route('/users/<int:user_id>', methods=['GET'])
def get_users(user_id=None):
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify(
                {"id": user.id, "name": user.name, "email": user.email, "age": user.age, "weight": user.weight,
                 "diseases": user.diseases})
        return jsonify({"message": "User not found"}), 404

    users = User.query.all()
    return jsonify(
        [{"id": u.id, "name": u.name, "email": u.email, "age": u.age, "weight": u.weight, "diseases": u.diseases} for u
         in users])


@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'], age=data['age'], weight=data['weight'],
                    diseases=data.get('diseases', ""))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully"}), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.age = data.get('age', user.age)
    user.weight = data.get('weight', user.weight)
    user.diseases = data.get('diseases', user.diseases)
    db.session.commit()

    return jsonify({"message": "User updated successfully"})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})


@app.route('/foodlog/<int:user_id>', methods=['GET'])
def get_food_logs(user_id):
    logs = FoodLog.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": log.id, "date": str(log.date), "food_item": log.food_item, "calories": log.calories,
                     "nutrients": log.nutrients} for log in logs])


@app.route('/foodlog', methods=['POST'])
def add_food_log():
    data = request.get_json()
    new_log = FoodLog(user_id=data['user_id'], food_item=data['food_item'], calories=data['calories'],
                      nutrients=data.get('nutrients', ""))
    db.session.add(new_log)
    db.session.commit()

    update_streak(data['user_id'])

    return jsonify({"message": "Food log added successfully"}), 201


@app.route('/healthlog', methods=['POST'])
def add_health_log():
    data = request.get_json()
    new_log = HealthLog(
        user_id=data['user_id'],
        heart_rate=data.get('heart_rate'),
        blood_pressure=data.get('blood_pressure'),
        glucose_level=data.get('glucose_level')
    )
    db.session.add(new_log)
    db.session.commit()

    update_streak(data['user_id'])

    return jsonify({"message": "Health log added successfully"}), 201


@app.route('/healthscore/<int:user_id>', methods=['GET'])
def get_health_score(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"user_id": user_id, "health_score": "Not yet Implemented"})


@app.route('/streak/<int:user_id>', methods=['GET'])
def get_user_streak(user_id):
    streak = UserStreak.query.get(user_id)
    if not streak:
        return jsonify({"streak_count": 0, "last_logged": None})

    return jsonify({"streak_count": streak.streak_count, "last_logged": str(streak.last_logged)})


def update_streak(user_id):
    streak = UserStreak.query.get(user_id)
    today = date.today()

    if streak:
        if streak.last_logged == today - timedelta(days=1):
            streak.streak_count += 1
        elif streak.last_logged < today - timedelta(days=1):
            streak.streak_count = 1
        streak.last_logged = today
    else:
        streak = UserStreak(user_id=user_id, streak_count=1, last_logged=today)
        db.session.add(streak)
    db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
