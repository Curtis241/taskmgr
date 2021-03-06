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
    * Day of week
        su, m, tu, w, th, f, sa
    * Relative terms
        today, tomorrow, next week, next month
    * Recurring terms
        every day, every weekday, every su, every m, every tu, every w, every th, every f, every sa
    * Short date - jan-dec 1-31
* Attractive table structure provided by the BeautifulTable library https://pypi.org/project/beautifultable/
* Download / Upload commands work with the Google Tasks service, but require setting up credentials
* The list task feature displays all tasks that have not been deleted and exports to csv file.
* The group command orders tasks by project and label. The results can be exported to a csv file.
* The filter command selects tasks by the status, project, complete/incomplete status, and label.
* The count command summarizes and displays the number of tasks in each project by date, date_range, label, project, and status. When the all command is used both the deleted and un-deleted tasks are included. The data is persisted to the selected database.
* The import command will now load tasks from a csv file
* Added support for a json or redis database. The database type can be configured using the default command.


**The commands available in version 0.2.0.**


::

        Usage: tm [OPTIONS] COMMAND [ARGS]...

        Options:
        --help  Show this message and exit.

        Commands:
          add         Appends a task using the provided or default parameters
          complete    Marks the task as done
          count       Displays task count
          defaults    Sets the default variables
          delete      Soft delete
          download    Imports tasks from the Google Tasks service
          edit        Replaces the task parameters with the provided parameters
          filter      Filters tasks
          group       Groups tasks
          import      Imports tasks from csv file
          incomplete  Marks the task as not done
          list        Lists all tasks
          reschedule  Moves all tasks from the past to today
          today       Lists only the tasks that have today's date
          undelete    Reverts deleted tasks
          unique      Displays unique tasks
          upload      Exports tasks to the Google Tasks service




Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
