import os

from flask import Flask, jsonify, request, make_response, Response

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
    content = request.json
    print(content)
    return Response()
    # if "text" in content:
    #     return jsonify(api_client.add_task(content.text, content.label,
    #                                        content.project, content.due_date))
    # else:
    #     return 404


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)