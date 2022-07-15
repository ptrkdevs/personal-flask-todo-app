from flask import Flask, render_template, request, redirect, url_for
from db import client
import datetime
from bson.errors import InvalidId

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

    @app.route("/collections/create", methods=["GET", "POST"])
    def create_collection():

        date = datetime.datetime.utcnow()

        action = "add-collection"

        if request.method == "POST":
            collection_name = request.form.get("item")

            if collection_name == "":
                print("collection should have a name")

            collection = {"name": collection_name, "date": date}

            app.db.todosList.insert_one(collection)

            return redirect(url_for("home"))

        return render_template("form.html", action=action)

    @app.route("/collections/delete/<string:id>", methods=["GET", "POST"])
    def delete_collection(id: str):

        object = "collection"

        try:
            collection = app.db.todosList.find_one({"_id": ObjectId(id)})

            if collection is None:
                return render_template(
                    "error.html", error_message="There is no collection with that ID"
                )

            if request.method == "POST":

                app.db.todos.delete_many(
                    {"list_id": ObjectId(collection["_id"])}
                )  # delete children
                app.db.todosList.delete_one({"_id": ObjectId(collection["_id"])})

                return redirect(url_for("home"))

        except InvalidId as e:
            return render_template(
                "error.html", error_message="There is no collection with that ID"
            )
        else:
            return render_template(
                "confirm.html", item=collection["name"], object=object
            )

    @app.route("/todos/create/<string:id>", methods=["GET", "POST"])
    def create_todo(id: str):

        action = "add-todo"

        if request.method == "POST":
            todo = request.form.get("item")

            try:
                _ = app.db.todosList.find_one({"_id": ObjectId(id)})

            except InvalidId:
                return render_template(
                    "error.html", error_message="There is no collection with that ID"
                )
            else:
                app.db.todos.insert_one(
                    {"list_id": ObjectId(id), "body": todo, "completed": False}
                )

                return redirect(url_for("todos", id=id))

        return render_template("form.html", action=action)

    @app.route("/todos/delete/<string:id>/", methods=["GET", "POST"])
    def delete_todo(id: str):

        object = "todo"

        try:
            todo = app.db.todos.find_one({"_id": ObjectId(id)})

            list_id = todo["list_id"]

            if todo is None:
                return render_template("error.html", error_message="Item Doesnt exists")

            if request.method == "POST":
                app.db.todos.delete_one({"_id": ObjectId(id)})

                return redirect(url_for("todos", id=list_id))

        except InvalidId:
            return render_template("error.html", error_message="Item Doesnt exists")

        return render_template("confirm.html", item=todo, object=object)

    @app.route("/todos/complete/<string:id>", methods=["GET", "POST"])
    def tag_todo(id: str):

        action = "tag"

        try:
            todo = app.db.todos.find_one({"_id": ObjectId(id)})

            if todo is None:
                return render_template("error.html", error_message="Item Doesnt exists")

            if request.method == "POST":

                # Update tag
                app.db.todos.update_one(
                    {"_id": ObjectId(id)}, {"$set": {"completed": True}}
                )

                return redirect(url_for("todos", id=todo["list_id"]))
        except InvalidId as e:
            return render_template("error.html", error_message="Item Doesnt exists")

        print(todo["list_id"])

        return render_template("confirm.html", action=action, item=todo)

    @app.route("/todos/<string:id>")
    def todos(id: str):

        try:
            print(id)
            todos = [item for item in app.db.todos.find({"list_id": ObjectId(id)})]

            archived_todos = [todo for todo in todos if todo["completed"]]

            active_todos = [todo for todo in todos if not todo["completed"]]

            date = datetime.datetime.now()

            kwargs = {
                "todos": todos,
                "active_todos": active_todos,
                "archived_todos": archived_todos,
                "date": {
                    "year": date.strftime("%Y"),
                    "month": date.strftime("%B"),
                    "day": date.strftime("%d"),
                },
            }
        except InvalidId:
            return render_template(
                "error.html", error_message="Item Doesnt exists, Go back!"
            )

        return render_template("todos.html", **kwargs)

    return app
