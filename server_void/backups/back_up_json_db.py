import os
import sys
import json
from datetime import datetime
from enum import Enum
import traceback
import subprocess

script_loc_dir = os.path.split(os.path.realpath(__file__))[0]
project_dir = os.path.abspath( os.path.join(script_loc_dir, '..', '..'))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from apiutils.configs.ServerConfig import ServerConfig
from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from apiutils.generalUtils import getServerName

PROD_ENV_JSON = "C:\\Users\\omnic\\OneDrive\\Computer Collection\\Reaction Meme Server\\config_jsons\\prodenv.json"
BACKUP_DIR = "C:\\Users\\omnic\\OneDrive\\Computer Collection\\Reaction Meme Server\\backups\\database"
LOGFILE = os.path.join(BACKUP_DIR, 'log.txt')
PRINT_LOGS = False

class LogType(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

LEVELS_TXT = ['INFO', 'WARNING', 'ERROR' ]


def send_notification(title, body):
    command = [
        "C:\\Python310\\pythonw.exe",
        "C:\\Users\\omnic\\OneDrive\\Computer Collection\\Reaction Meme Server\\backups\\winnotif.py",
        "title",
        title,
        "body",
        body,
        "label",
        "See Log File",
        "attach",
        "C:\\Users\\omnic\\OneDrive\\Computer Collection\\Reaction Meme Server\\backups\\database\\log.txt"
    ]
    subprocess.Popen(command)

def make_backup_name():
    return 'db_{}.json'.format(datetime.today().strftime('%Y_%m_%d_%H_%M'))

def log(text, type=LogType.INFO):
    lvText = f'[{LEVELS_TXT[type.value]}]'

    nowTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    lgText = '{}: {:8s} {}'.format(nowTime, lvText, text)

    if PRINT_LOGS:
        print(lgText)

    with open(LOGFILE, 'a') as file:
        file.write(lgText + '\n')


def log_info(text):
    log(text, type=LogType.INFO)

def log_err(text):
    log(text, type=LogType.ERROR)

def main():
    global PRINT_LOGS
    args = sys.argv[1:]
    if 'print-logs' in args:
        PRINT_LOGS = True
    try:
        log_info('Backup Running')
        # Load production environment config
        ServerConfig.setConfigFromJSON(PROD_ENV_JSON)
        log_info(f'Loaded Produciton Configuration from {PROD_ENV_JSON}')


        accessToken = ServerConfig.PBFS_ACCESS_TOKEN
        serverIden = ServerConfig.PBFS_SERVER_IDENTIFIER

        # Get a file storage object
        pbfs = PBFSFileStorage(accessToken, serverIden)
        log_info(
            f'Connected to PBFS File Storage: accessToken={accessToken}, serverIdentifier={serverIden} ({getServerName(serverIden)})')
        log_info('Downloading JSON DB...')
        db = pbfs.getJSONDB()
        log_info('DB Downloaded Successfully...')

        save_path = os.path.join(BACKUP_DIR, make_backup_name())
        log_info(f'Saving DB to {save_path}...')
        with open(save_path, 'w') as file:
            json.dump(db, file, indent=4)

        log_info(f'DB Saved Successfully')
        log_info('Backup Completed Successfully')
        log_info('Sending Notification')
        send_notification('RMSVR Backup Task', 'The backup completed successfully.')
        log_info('Exiting')
        return 0

    except Exception as e:
        log_err(f'An error occurred running the script: {e}')
        log_err(f'Printing Traceback:')
        with open(LOGFILE, 'a') as file:
            traceback.print_exc(file=file)
        send_notification('RMSVR Backup Task', 'An error occured during the backup process.')
        return -1

if __name__ == '__main__':
    sys.exit(main())