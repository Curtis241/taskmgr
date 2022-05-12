import uvicorn
from fastapi import FastAPI, HTTPException

from taskmgr.lib.database.manager import DatabaseManager
from taskmgr.lib.view.api_client import ApiClient
from taskmgr.lib.view.client_args import *

api_client = ApiClient(DatabaseManager())
app = FastAPI()


@app.get("/tasks")
async def get_all_tasks():
    return api_client.list_all_tasks()


@app.post("/tasks")
async def add_task(args: AddArgs):
    return api_client.add(args)


@app.delete("/tasks")
async def delete_tasks():
    return api_client.remove_all_tasks()


@app.put("/tasks")
async def edit_task(args: EditArgs):
    return api_client.edit(args)


@app.get("/tasks/task/{task_index}")
async def get_task(task_index: int):
    return api_client.get_task(GetArg(index=task_index))


@app.delete("/tasks/task/{action}/{task_index}")
async def delete_task(action: str, task_index: int):

    if action == "undelete":
        args = UndeleteArgs(indexes=(task_index,))
        return api_client.undelete(args)
    elif action == "delete":
        args = DeleteArgs(indexes=(task_index,))
        return api_client.delete(args)
    else:
        raise HTTPException(status_code=418, detail="action: [undelete, delete]")


@app.put("/tasks/task/{action}/{task_index}")
async def update_task_status(action: str, task_index: int, time_spent: float = 0):

    if action == "complete":
        return api_client.complete(CompleteArgs(indexes=(task_index,), time_spent=time_spent))
    elif action == "incomplete":
        return api_client.reset(ResetArgs(indexes=(task_index,)))
    else:
        raise HTTPException(status_code=418, detail="action: [complete, incomplete]")


@app.put("/unique/{unique_type}")
async def get_unique_object(unique_type: str):

    if unique_type == "label":
        return api_client.get_unique_label_list()
    elif unique_type == "project":
        return api_client.get_unique_project_list()
    else:
        raise HTTPException(status_code=418, detail="name: [label, project]")


@app.put("/group/{group_type}")
async def group_by_object(group_type: str):

    if group_type == "label":
        return api_client.group_tasks_by_label()
    elif group_type == "project":
        return api_client.group_tasks_by_project()
    elif group_type == "due_date":
        return api_client.group_tasks_by_due_date()
    else:
        raise HTTPException(status_code=418, detail="name: [label, project, due_date]")


@app.put("/filter/project")
async def filter_tasks_by_project(args: ProjectArgs):
    return api_client.filter_tasks_by_project(args)


@app.put("/filter/label")
async def filter_tasks_by_label(args: LabelArgs):
    return api_client.filter_tasks_by_label(args)


@app.put("/filter/name")
async def filter_tasks_by_name(args: NameArgs):
    return api_client.filter_tasks_by_name(args)


@app.put("/filter/due_date")
async def filter_tasks_by_due_date(args: DueDateArgs):
    return api_client.filter_tasks_by_due_date(args)


@app.put("/filter/status")
async def filter_tasks_by_status(args: StatusArgs):
    return api_client.filter_tasks_by_status(args)


@app.put("/filter/due_date_range")
async def filter_tasks_by_due_date_range(args: DueDateRangeArgs):
    return api_client.filter_tasks_by_due_date_range(args)


@app.get("/count_all")
async def count_all_tasks(page: int = 1):
    return api_client.count_all_tasks(page)


@app.put("/count/due_date")
async def count_tasks_by_due_date(args: DueDateArgs):
    return api_client.count_tasks_by_due_date(args)


@app.put("/count/project")
async def count_tasks_by_project(args: ProjectArgs):
    return api_client.count_tasks_by_project(args)


@app.put("/count/due_date_range")
async def count_tasks_by_due_date_range(args: DueDateRangeArgs):
    return api_client.count_tasks_by_due_date_range(args)


@app.put("/count/label")
async def count_tasks_by_label(args: LabelArgs):
    return api_client.count_tasks_by_label(args)


@app.put("/count/name")
async def count_tasks_by_name(args: NameArgs):
    return api_client.count_tasks_by_name(args)


@app.put("/reschedule/")
async def reschedule():
    api_client.reschedule_tasks()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


