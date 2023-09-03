from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from taskmgr.lib.database.db_manager import DatabaseManager, AuthenticationFailed
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.view.api_client import ApiClient
from taskmgr.lib.view.client_args import *


try:
    db_manager = DatabaseManager()
    api_client = ApiClient(DatabaseManager())
    logger = AppLogger("api").get_logger()
except AuthenticationFailed:
    exit(-1)


app = FastAPI()


def handle_response(json):
    if "error" in json:
        return JSONResponse(status_code=422, content=json)
    else:
        return JSONResponse(status_code=200, content=json)

# Tasks
@app.get("/tasks")
async def get_all_tasks(args: ListArgs):
    return api_client.list_all_tasks(args)


@app.post("/tasks")
async def add_task(args: AddArgs):
    json = api_client.add_task(args)
    return handle_response(json)


@app.delete("/tasks")
async def delete_tasks():
    api_client.remove_all_tasks()
    return api_client.count_all_tasks()


@app.put("/tasks")
async def edit_task(args: EditArgs):
    return api_client.edit_task(args)


@app.get("/task/{task_index}")
async def get_task(task_index: int):
    return api_client.get_task(GetArg(index=task_index))


@app.delete("/task/{action}/{task_index}")
async def delete_task(action: str, task_index: int):

    if action == "undelete":
        args = UndeleteArgs(indexes=(task_index,))
        return api_client.undelete_task(args)
    elif action == "delete":
        args = DeleteArgs(indexes=(task_index,))
        return api_client.delete_task(args)
    else:
        raise HTTPException(status_code=418, detail="action: [undelete, delete]")


@app.put("/task/complete/{task_index}")
async def complete_task(task_index: int, time_spent: float = 0.0):
    args = CompleteArgs(indexes=(task_index,), time_spent=time_spent)
    return api_client.complete_task(args)


@app.put("/task/incomplete/{task_index}")
async def incomplete_task(task_index: int):
    args = ResetArgs(indexes=(task_index,))
    return api_client.reset_task(args)


@app.put("/task/unique/{unique_type}")
async def get_unique_object(unique_type: str):

    if unique_type == "label":
        return api_client.get_unique_label_list()
    elif unique_type == "project":
        return api_client.get_unique_project_list()
    else:
        raise HTTPException(status_code=418, detail="name: [label, project]")


@app.put("/task/group/{group_type}")
async def group_by_object(group_type: str):

    if group_type == "label":
        return api_client.group_tasks_by_label()
    elif group_type == "project":
        return api_client.group_tasks_by_project()
    elif group_type == "due_date":
        return api_client.group_tasks_by_due_date()
    else:
        raise HTTPException(status_code=418, detail="name: [label, project, due_date]")


@app.put("/task/filter/project")
async def filter_tasks_by_project(args: ProjectArgs):
    return api_client.filter_tasks_by_project(args)


@app.put("/task/filter/label")
async def filter_tasks_by_label(args: LabelArgs):
    return api_client.filter_tasks_by_label(args)


@app.put("/task/filter/name")
async def filter_tasks_by_name(args: NameArgs):
    return api_client.filter_tasks_by_name(args)


@app.put("/task/filter/due_date")
async def filter_tasks_by_due_date(args: DueDateArgs):
    return api_client.filter_tasks_by_due_date(args)


@app.put("/task/filter/status")
async def filter_tasks_by_status(args: StatusArgs):
    return api_client.filter_tasks_by_status(args)


@app.put("/task/filter/due_date_range")
async def filter_tasks_by_due_date_range(args: DueDateRangeArgs):
    return api_client.filter_tasks_by_due_date_range(args)


@app.put("/task/count_all")
async def count_all_tasks(page: int = 1):
    return api_client.count_all_tasks(page)


@app.put("/task/count/due_date")
async def count_tasks_by_due_date(args: DueDateArgs):
    return api_client.count_tasks_by_due_date(args)


@app.put("/task/count/project")
async def count_tasks_by_project(args: ProjectArgs):
    return api_client.count_tasks_by_project(args)


@app.put("/task/count/due_date_range")
async def count_tasks_by_due_date_range(args: DueDateRangeArgs):
    return api_client.count_tasks_by_due_date_range(args)


@app.put("/task/count/label")
async def count_tasks_by_label(args: LabelArgs):
    return api_client.count_tasks_by_label(args)


@app.put("/task/count/name")
async def count_tasks_by_name(args: NameArgs):
    return api_client.count_tasks_by_name(args)


@app.put("/task/reschedule")
async def reschedule():
    api_client.reschedule_tasks()


