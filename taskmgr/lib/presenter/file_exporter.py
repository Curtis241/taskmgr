import csv
import os
import time
from abc import abstractmethod
from operator import attrgetter
from string import Template

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import Today
from taskmgr.lib.variables import CommonVariables


class File:
    logger = AppLogger("file").get_logger()

    def __init__(self):
        self.__output_dir = CommonVariables().resources_dir

    @staticmethod
    def get_timestamp():
        return time.strftime(CommonVariables().file_name_timestamp)

    def save(self, obj_list) -> str:
        if obj_list is not None:
            assert type(obj_list) is list

            file_name = self.get_filename()
            path = self.__make_path(file_name)

            if self.__exists():
                self.write_file(path, obj_list)
                self.logger.info(f"Exported results to {path}")
                return path
            else:
                self.logger.info(f"Provided path {path} does not exist")

    def __exists(self) -> bool:
        return os.path.exists(self.__output_dir)

    def __make_path(self, file_name) -> str:
        if str(self.__output_dir).endswith("/"):
            path = f"{self.__output_dir}{file_name}"
        else:
            path = f"{self.__output_dir}/{file_name}"
        return path

    @abstractmethod
    def write_file(self, path, task_list):
        pass

    @abstractmethod
    def get_filename(self):
        pass


class MarkdownTasksFile(File):
    """
    Exports a task_list to a markdown file with name (ie. tasks_results_20190813_210046.md) using the format:

    YYYY-MM-DD

    Completed:
    * Task 1: <label>
    * Task 2: <label>

    Not-Completed:
    * Task 3: <label>
    * Task 4: <label>

    A FileExporter class was created to encapsulate the export functionality and reduce the complexity of
    the Client base class. Since there is only 1 file template type, the template is built into the write_file
    and write_row methods. The template portion could be placed into an external template file
    so that the user could pick a template name and convert the tasks to the markdown file.
    """

    logger = AppLogger("markdown_file").get_logger()

    def __init__(self):
        super().__init__()
        self.header_template = Template("# $today \n")
        self.completed_title = "## Completed \n"
        self.task_row_template = Template("* $text \n")
        self.task_label_row_template = Template("* $text : $label \n")
        self.not_completed_title = "## Not Completed \n"

    def write_file(self, path, task_list):
        with open(path, 'w') as outfile:
            today_string = Today().to_date_string()
            outfile.write(self.header_template.substitute(today=today_string))
            outfile.write("")
            outfile.write(self.completed_title)

            for task in task_list:
                if task.is_completed():
                    self.__write_row(outfile, task)

            outfile.write("")
            outfile.write(self.not_completed_title)

            for task in task_list:
                if not task.is_completed():
                    self.__write_row(outfile, task)

    def get_filename(self):
        return f"tasks_{self.get_timestamp()}.md"

    def __write_row(self, outfile, task):
        assert type(task) is Task
        if len(task.label) == 0:
            outfile.write(self.task_row_template.substitute(text=task.text))
        else:
            outfile.write(self.task_label_row_template.substitute(text=task.text, label=task.label))


class CsvTasksFile(File):

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"tasks_{self.get_timestamp()}.csv"

    def write_file(self, path, task_list):
        with open(path, 'w', newline='') as csvfile:
            if len(task_list) > 0:
                writer = csv.DictWriter(csvfile, fieldnames=self.__get_field_names())
                writer.writeheader()
                for task in sorted(task_list, key=attrgetter('index')):
                    writer.writerow(self.__write_row(task))

    @staticmethod
    def __get_field_names():
        return ["index", "done", "text", "project", "label", "due_date", "until", "last_updated", "deleted"]

    @staticmethod
    def __write_row(task):
        due_date = task.get_date_string_list()
        return {"index": task.index, "done": task.is_completed(), "text": task.text, "project": task.project,
                "label": task.label,
                "due_date": due_date[0], "until": due_date[1],
                "last_updated": task.last_updated,
                "deleted": task.deleted}


class CsvSnapshotsFile(File):

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"snapshots_{self.get_timestamp()}.csv"

    def write_file(self, path, snapshot_list):
        with open(path, 'w', newline='') as csvfile:
            if len(snapshot_list) > 0:
                writer = csv.DictWriter(csvfile, fieldnames=self.__get_field_names())
                writer.writeheader()
                for snapshot in sorted(snapshot_list, key=attrgetter('index')):
                    writer.writerow(self.__write_row(snapshot))

    @staticmethod
    def __get_field_names():
        return ["index", "count", "completed", "incomplete", "deleted", "project", "timestamp"]

    @staticmethod
    def __write_row(snapshot):
        return {"index": snapshot.index, "count": snapshot.count, "completed": snapshot.completed,
                "incomplete": snapshot.incomplete,
                "deleted": snapshot.deleted,
                "project": snapshot.project,
                "timestamp": snapshot.timestamp}


class FileExporter:
    MARKDOWN = "markdown"
    CSV = "csv"

    @staticmethod
    def save_tasks(task_list, file_type):
        assert type(task_list) is list

        if len(task_list) > 0 and isinstance(task_list[0], Task):
            if file_type == FileExporter.MARKDOWN:
                return MarkdownTasksFile().save(task_list)

            if file_type == FileExporter.CSV:
                return CsvTasksFile().save(task_list)

    @staticmethod
    def save_snapshots(snapshot_list):
        assert type(snapshot_list) is list

        if len(snapshot_list) > 0 and isinstance(snapshot_list[0], Snapshot):
            return CsvSnapshotsFile().save(snapshot_list)
