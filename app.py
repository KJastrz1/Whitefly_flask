from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from celery_config import make_celery

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["broker_url"] = os.environ.get("CELERY_BROKER_URL")
app.config["result_backend"] = os.environ.get("CELERY_RESULT_BACKEND")
app.config["broker_connection_retry_on_startup"] = True
app.config["DEBUG"] = os.environ.get("DEBUG") == "True"


db = SQLAlchemy(app)
migrate = Migrate(app, db)
celery = make_celery(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Message('{self.content}')"


import tasks


@app.route("/")
def index():
    messages = Message.query.all()
    return render_template("index.html", messages=messages)


@app.route("/sync-form", methods=("GET", "POST"))
def sync_form():
    if request.method == "POST":
        content = request.form["content"]
        if not content:
            flash("Content is required!")
        else:
            message = Message(content=content)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("form.html")


@app.route("/async-form", methods=("GET", "POST"))
def async_form():
    if request.method == "POST":
        content = request.form["content"]
        if not content:
            flash("Content is required!")
        else:            
            task = tasks.process_message.apply_async(args=[content], queue='default')
            print("id taska", task.id)
            return redirect(url_for("index"))
    return render_template("async_form.html")


if __name__ == "__main__":
    app.run(debug=True)
