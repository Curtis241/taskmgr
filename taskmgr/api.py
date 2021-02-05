import os

from flask import Flask, jsonify, request, make_response, Response
from werkzeug.exceptions import abort

from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.view.api_client import ApiClient

app = Flask(__name__)
api_client = ApiClient(DatabaseManager(), FileManager())


@app.route("/tasks/list", methods=["GET"])
def get_tasks_list():
    return jsonify(api_client.list_all_tasks(**{}))


@app.route("/task/add", methods=["POST"])
def add_task():
    app.logger.debug("Request Headers %s", request.headers)
    app.logger.debug("Request Body %s", request.json)
    if not request.json or 'text' not in request.json:
        abort(400)
    return jsonify(api_client.add_task(request["text"], request["label"],
                                       request["project"], request["due_date"]))


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
