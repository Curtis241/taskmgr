from flask import Flask, jsonify

from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.view.api_client import ApiClient

app = Flask(__name__)
api_client = ApiClient(DatabaseManager(), FileManager())


@app.route("/task/list")
def get_tasks_list():
    return jsonify(api_client.list_all_tasks(**{}))


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)