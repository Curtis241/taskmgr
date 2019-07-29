import os
import time
from string import Template

from taskmgr.lib.date_generator import Today
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task import Task
from taskmgr.lib.variables import CommonVariables


class FileExporter:
    logger = AppLogger("file_exporter").get_logger()

    def __init__(self, output_dir):
        assert type(output_dir) is str

        self.file_name = Template("tasks_results_$timestamp.md")
        self.output_dir = output_dir

        self.header_template = Template("# $today \n")
        self.completed_title = "## Completed \n"
        self.task_row_template = Template("* $task_row \n")
        self.task_label_row_template = Template("* $task_row : $label \n")
        self.not_completed_title = "## Not Completed \n"

    def save(self, task_list):
        if task_list is not None:
            assert type(task_list) is list

            if len(task_list) > 0:
                assert type(task_list[0]) is Task

            if self.exists():
                path = self.get_path()
                with open(self.get_path(), 'w') as outfile:
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
                self.logger.info(f"Exported results to {path}")
            else:
                self.logger.info(f"Provided path {self.output_dir} does not exist")

    def write_row(self, outfile, task):
        if len(task.label) == 0:
            outfile.write(self.task_row_template.substitute(task_row=task.text))
        else:
            outfile.write(self.task_label_row_template.substitute(task_row=task.text, label=task.label))

    def exists(self):
        return os.path.exists(self.output_dir)

    def get_path(self):
        return self.make_path()

    def make_path(self):
        timestamp_string = time.strftime(CommonVariables.file_name_timestamp)
        file_name = self.file_name.substitute(timestamp=timestamp_string)
        path = f"{self.output_dir}/{file_name}"
        return path


