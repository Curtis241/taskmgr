from pathlib import Path

class CommonVariables:

    # Date formats
    date_format = "%Y-%m-%d"
    date_time_format = "%Y-%m-%d %H:%M:%S"
    rfc3339_date_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    recurring_month_limit = 2

    # Task defaults
    default_date_expression = "empty"
    default_project_name = "inbox"
    default_label = ""

    # Directories
    home = str(Path.home())
    resources_dir = f"{home}/.config/taskmgr/resources/"
    credentials_dir = f"{home}/.config/taskmgr/credentials/"
    log_dir = f"{home}/.config/taskmgr/log/"


    # CLI defaults
    default_text_field_length = 50
