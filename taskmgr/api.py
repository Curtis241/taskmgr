

from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic.class_validators import validator

from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.view.api_client import ApiClient

api_client = ApiClient(DatabaseManager())
app = FastAPI()


class TaskModel(BaseModel):
    index: Optional[int] = 0
    text: str
    label: str
    project: str
    date_expression: str

    @validator('*')
    def check_values_not_empty(cls, value):
        assert value != '', 'Empty strings are not allowed.'
        return value


class RequestBody(BaseModel):
    name: str
    value1: Optional[str] = str()
    value2: Optional[str] = str()


@app.get("/tasks")
async def get_all_tasks():
    return api_client.list_all_tasks()


@app.post("/tasks")
async def add_task(task: TaskModel, status_code=status.HTTP_201_CREATED):
    return api_client.add_task(task.text, task.label, task.project, task.date_expression)


@app.delete("/tasks")
async def delete_tasks():
    api_client.remove_all_tasks()
    return api_client.count_all_tasks()


@app.put("/tasks")
async def edit_task(task: TaskModel):
    return api_client.edit_task(task.index, task.text,
                                task.label, task.project, task.date_expression)


@app.get("/tasks/task/{task_index}")
async def get_task(task_index: int):
    return api_client.get_task(task_index)


@app.delete("/tasks/task/{action}/{uuid}")
async def delete_task(action: str, uuid: str):

    if action == "undelete":
        return api_client.undelete_task(uuid)
    elif action == "delete":
        return api_client.delete_task(uuid)
    else:
        raise HTTPException(status_code=418, detail="action: [undelete, delete]")


@app.put("/tasks/task/{action}/{uuid}")
async def update_task_status(action: str, uuid: str):

    if action == "complete":
        return api_client.complete_task(uuid)
    elif action == "incomplete":
        return api_client.reset_task(uuid)
    else:
        raise HTTPException(status_code=418, detail="action: [complete, incomplete]")


@app.put("/unique/")
async def get_unique_object(body: RequestBody):

    if body.name == "label":
        return api_client.get_unique_label_list()
    elif body.name == "project":
        return api_client.get_unique_project_list()
    else:
        raise HTTPException(status_code=418, detail="name: [label, project]")


@app.put("/group/")
async def group_by_object(body: RequestBody):

    if body.name == "label":
        return api_client.group_tasks_by_label()
    elif body.name == "project":
        return api_client.group_tasks_by_project()
    elif body.name == "due_date":
        return api_client.group_tasks_by_due_date()
    else:
        raise HTTPException(status_code=418, detail="name: [label, project, due_date]")


@app.put("/filter/")
async def filter_tasks(body: RequestBody):

    if not body.value1:
        raise HTTPException(status_code=418, detail=f"value1 {body.value1} is invalid")

    if body.name == "project":
        return api_client.filter_tasks_by_project(body.value1)
    elif body.name == "label":
        return api_client.filter_tasks_by_label(body.value1)
    elif body.name == "text":
        return api_client.filter_tasks_by_text(body.value1)
    elif body.name == "due_date":
        return api_client.filter_tasks_by_due_date(body.value1)
    elif body.name == "status":
        return api_client.filter_tasks_by_status(body.value1)
    elif body.name == "due_date_range":

        if not body.value2:
            raise HTTPException(status_code=418, detail=f"value2 {body.value2} is invalid")

        return api_client.filter_tasks_by_due_date_range(body.value1, body.value2)
    else:
        raise HTTPException(status_code=418, detail="name: [project, label, text, due_date, status, due_date_range]")


@app.get("/count_all")
async def count_all_tasks():
    return api_client.count_all_tasks()


@app.put("/count/")
async def count_tasks_by_type(body: RequestBody):

    if not body.value1:
        raise HTTPException(status_code=418, detail=f"value1 {body.value1} is invalid")

    if body.name == "due_date":
        return api_client.count_tasks_by_due_date(body.value1)
    elif body.name == "project":
        return api_client.count_tasks_by_project(body.value1)
    elif body.name == "due_date_range":

        if not body.value2:
            raise HTTPException(status_code=418, detail=f"value2 {body.value2} is invalid")

        return api_client.count_tasks_by_due_date_range(body.value1, body.value2)
    else:
        raise HTTPException(status_code=418, detail="name: [due_date, project, due_date_range")


@app.put("/reschedule/")
async def reschedule():
    api_client.reschedule_tasks()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


