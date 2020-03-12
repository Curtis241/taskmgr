=======
taskmgr
=======


.. image:: https://img.shields.io/pypi/v/taskmgr.svg
        :target: https://pypi.python.org/pypi/taskmgr

.. image:: https://img.shields.io/travis/Curtis241/taskmgr.svg
        :target: https://travis-ci.org/Curtis241/taskmgr

.. image:: https://readthedocs.org/projects/taskmgr/badge/?version=latest
        :target: https://taskmgr.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Task Manager


* Free software: MIT license
* Documentation: https://taskmgr.readthedocs.io.


Features
--------

taskmgr is a simple python command-line tool for storing tasks in a file database and
can also import/export tasks from a Google tasks service. The service is the
backend storage for the Android Google Tasks app.

* Contains basic functions add, edit, delete, complete tasks
* The add and edit functions support normal language date expressions like:
    * Day of week (ie. su, m, tu, w, th, f, sa)
    * Relative terms (ie. today, tomorrow, next week, next month)
    * Recurring terms (ie. every day, every weekday, every su, every m, every tu, every w, every th, every f, every sa)
    * Short date - jan-dec 1-31
* Attractive table structure provided by the BeautifulTable library https://pypi.org/project/beautifultable/
* Import / Export of tasks to Google Tasks service
* The list task feature displays all tasks that have not been deleted.
* The group command orders tasks by project and label. The results can be exported to a csv file.
* The filter command selects tasks by the status, project, complete/incomplete status, and label.
* The count command summarizes and displays the number of tasks in each project by date, date_range, label, project, and
status. When the all command is used both the deleted and un-deleted tasks are included. The data is persisted to the
selected database.
* Added export of tasks to a csv file on results that are filtered. In addition to the csv file, the today command can
also export to a markdown file.
* Added support for a json or redis database. The database type can be configured using the default command.



The commands available in version 0.1.4.

Usage: tm [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add         Appends a task using the provided or default parameters
  complete    Marks the task as done
  count       Displays task count
  defaults    Sets the default variables
  delete      Toggles the delete parameter but keeps the object in the...
  edit        Replaces the task parameters with the provided parameters
  export      Exports the tasks to the Google Tasks service
  filter      Filters tasks
  group       Groups tasks
  import      Imports the tasks from the Google Tasks service
  list        Lists all un-deleted tasks
  reschedule  Moves all tasks from the past to today
  reset       Resets the done status
  today       Lists only the tasks that have today's date




Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
