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
* The list task feature displays all tasks and list that groups tasks by project and label
* The show feature filters tasks by the status, project, and label.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
