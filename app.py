from flask import Flask, render_template
from db import client

from bson.objectid import ObjectId


def create_app():

    # init app

    app = Flask(__name__)

    app.db = client.todos

    @app.route("/")
    def home():

        todo_list = [todo for todo in app.db.todosList.find()]

        kwargs = {"todos": todo_list}

        return render_template("index.html", **kwargs)

    @app.route("/todos/<string:id>")
    def todos(id: str):

        todos = [item for item in app.db.todos.find({"list_id": ObjectId(id)})]

        kwargs = {"todos": todos}

        return render_template("todos.html", **kwargs)

    return app
