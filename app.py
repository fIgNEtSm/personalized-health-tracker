from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://postgres:VMwZTYIa67oJ5Cvi@bashfully-placid-oriole.data-1.use1'
                                         '.tembo.io:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# from api import api
# app.register_blueprint(api, url_prefix="/api")

@app.route('/')
def dashboard():
    return render_template("index.html", active_page="dashboard")


@app.route("/login/")
def login():
    return render_template("login.html", active_page="login")


@app.route("/registration/")
def registration():
    return render_template("registration.html")


@app.route("/add-recipe/")
def add_recipe():
    return render_template("add_recipe.html", active_page="add_recipe")


@app.route("/profile/")
def profile():
    return render_template("my_profile.html", active_page="profile")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
