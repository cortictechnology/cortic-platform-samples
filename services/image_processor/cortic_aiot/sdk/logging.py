""" 
COPYRIGHT_NOTICE:
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2022-2023
COPYRIGHT_NOTICE

The logging module provides function to log messages to the Cortic Hub's console widget.

"""

from enum import Enum


class LogLevel(Enum):
    Info = 0
    Warning = 1
    Error = 2


def log(message, log_level=LogLevel.Info):
    """
    Allows developers to create logs that can be viewed in a Cortic Hub's console widget.
    Logs created with this function will have an associated tag. There are three log levels:

    +--------------------+-------------------------+
    | Log Levels         | Description             |
    +====================+=========================+
    | LogLevel.Info      | Informational message.  |
    +--------------------+-------------------------+
    | LogLevel.Warning   | Warning message.        |
    +--------------------+-------------------------+
    | LogLevel.Error     | Error message.          |
    +--------------------+-------------------------+


    :param message: String to log; may contain HTML color tags to display parts of the string
            in different colors in the Hub's console widget.
    :type message: str

    :param log_level: Log severity levels.
    :type log_level: LogLevel


    :Example:

    .. code-block:: python

        log("Done <p style='color:blue'>creating</p> <p style='color:red'>UI</p> and <p style='color:orange'>counters</p> <p style='color:green'>in</p> setup")

    """
    log_level_string = ""
    if log_level == LogLevel.Info:
        log_level_string = "<cortic_log_info>"
    elif log_level == LogLevel.Warning:
        log_level_string = "<cortic_log_warning>"
    elif log_level == LogLevel.Error:
        log_level_string = "<cortic_log_error>"
    print(log_level_string + message)
