import os
import time
from string import Template

from taskmgr.lib.presenter.date_generator import Today
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.task import Task
from taskmgr.lib.variables import CommonVariables


class FileExporter:
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
    logger = AppLogger("file_exporter").get_logger()

    def __init__(self):
        self.file_name = Template("tasks_results_$timestamp.md")
        self.header_template = Template("# $today \n")
        self.completed_title = "## Completed \n"
        self.task_row_template = Template("* $text \n")
        self.task_label_row_template = Template("* $text : $label \n")
        self.not_completed_title = "## Not Completed \n"

    def save(self, task_list, output_dir) -> str:
        assert type(output_dir) is str

        if task_list is not None:
            assert type(task_list) is list

            if len(task_list) > 0:
                assert type(task_list[0]) is Task

            if self.exists(output_dir):
                path = self.make_path(output_dir)
                self.write_file(path, task_list)
                self.logger.info(f"Exported results to {path}")
                return path
            else:
                self.logger.info(f"Provided path {output_dir} does not exist")

    def write_file(self, path, task_list):
        with open(path, 'w') as outfile:
            today_string = Today().to_date_string()
            outfile.write(self.header_template.substitute(today=today_string))
            outfile.write("")
            outfile.write(self.completed_title)

            for task in task_list:
                if task.is_completed():
                    self.write_row(outfile, task)

            outfile.write("")
            outfile.write(self.not_completed_title)

            for task in task_list:
                if not task.is_completed():
                    self.write_row(outfile, task)

    def write_row(self, outfile, task):
        assert type(task) is Task
        if len(task.label) == 0:
            outfile.write(self.task_row_template.substitute(text=task.text))
        else:
            outfile.write(self.task_label_row_template.substitute(text=task.text, label=task.label))

    @staticmethod
    def exists(output_dir):
        return os.path.exists(output_dir)

    def make_path(self, output_dir):
        timestamp_string = time.strftime(CommonVariables().file_name_timestamp)
        file_name = self.file_name.substitute(timestamp=timestamp_string)

        if str(output_dir).endswith("/"):
            path = f"{output_dir}{file_name}"
        else:
            path = f"{output_dir}/{file_name}"
        return path
