=======
taskmgr
=======


Task Manager

* Free software: MIT license

Features
--------

taskmgr is a simple python command-line tool for storing tasks in a redis database.

* Contains basic functions add, edit, delete, complete tasks
* The add and edit functions support normal language date expressions like:
    * Day of week
        su, m, tu, w, th, f, sa
    * Relative terms
        today, tomorrow, yesterday, last [week, month], this [week, month], next [week, month]
    * Recurring terms
        every day, every weekday, every [su,m,tu,w,th,f,sa]
    * Short date 
        jan-dec 1-31 (ie. jan 21)

* Attractive table structure provided by the BeautifulTable library https://pypi.org/project/beautifultable/
* The list task feature displays all tasks that have not been deleted and exports to csv file.
* The group command orders tasks by project and label. The results can be exported to a csv file.
* The filter command selects tasks by the status, project, complete/incomplete status, and label.
* The count command summarizes and displays the number of tasks in each project by date, date_range, label, project, and status. When the all command is used both the deleted and un-deleted tasks are included.
* The import command will now load tasks from a csv file
* Added support for a redis database with the redisearch plugin installed. The database type can be configured using the default command.
* Added rest api using FastApi library

**Rest Api Instructions**
pip install uvicorn[standard]
uvicorn taskmgr:app

**RediSearch Install**
git clone https://github.com/RediSearch/RediSearch.git
cd RediSearch
make build
cp RediSearch/bin/linux-x64-release/search/redisearch.so /etc/redis/modules/


**The commands available in version 0.2.5.**


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




Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
