"""
This module contains the code for the Log variable.
"""

from os import mkdir
from os.path import exists

from settings import Settings
from tamga import Tamga

if not exists(Settings.LOG_FOLDER_ROOT):
    mkdir(Settings.LOG_FOLDER_ROOT)

Log = Tamga(
    file_output=Settings.LOG_TO_FILE,
    json_output=Settings.LOG_TO_JSON,
    console_output=Settings.TAMGA_LOGGER,
    file_path=Settings.LOG_FILE_ROOT,
    json_path=Settings.LOG_JSON_ROOT,
)
