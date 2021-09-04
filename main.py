from zipfile import ZipFile
import os
import datetime
from paramiko import SSHClient
import sys
from time import sleep
import json
import psutil
from common.variable import *
import logging
from log.my_log import log
from log import log_config


LOG = logging.getLogger('log.main')


@log
def check_date(date_storage: list):
    """ Функция проверяет запускалась ли прогграмма сегодня сверяя дату с date_storage. """
    LOG.info('Проверка от повторного копирования данных согласно date_storage.json')
    return True if (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y/%m/%d/") in date_storage \
        else False


@log
def run(storage: str, archive: str, days: int = 90):
    """ Функция архивирует файлы старше 90 дней и отправляет их по ssh на сервер
     через функцию send_to_archive() """
    date = datetime.datetime.now() - datetime.timedelta(days=days)
    date = date.strftime("%Y/%m/%d/")
    storage += date
    archive += date
    for file in os.listdir(f'{storage}'):
        jungle_zip = ZipFile(f'{storage}{file}.zip', 'w')
        jungle_zip.write(f'{storage}{file}')
        jungle_zip.close()
        source_path = f'{storage}{file}.zip'
        LOG.info(f'Создан {source_path}')
        new_location = f'{archive}{file}.zip'
        send_to_archive(archive, source_path, new_location)  # удалять не стал для тестов
        # send_to_archive_ssh(my_server, my_username, my_password, f'{storage}{file}.zip', archive)
        # Начал проверять все ли верно сделал по заданию и увидел Архив-сервер смонтирован как папка...
        # для работы с Архив-сервер через ssh, в текущей задаче не нужно


@log
def check_space(dick_path):
    """ Функция проверяет наличие свободного места на диске """
    LOG.debug('Проверка свободного места на диске')
    disk = psutil.disk_usage(dick_path)
    return True if disk.percent > 90 else False


@log
def send_to_archive(archive, source_path, new_location):
    if os.path.exists(archive):
        os.replace(source_path, new_location)
    else:
        os.makedirs(archive)
        os.replace(source_path, new_location)
    LOG.info("% s перемещен в % s" % (source_path, new_location))


@log
def send_to_archive_ssh(server: str, username: str, password: str, storage_path: str, archive_path: str):
    # для работы с Архив-сервер через ssh, в текущей задаче не нужно
    """ Функция устанавливает соединеие с сервером через ssh и передает файлы
     используя sftp из storage_path в archive_path """
    ssh = SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.put(storage_path, archive_path)
    sftp.close()
    ssh.close()


if __name__ == '__main__':
    if '-s' in sys.argv:
        i = sys.argv.index('-s')
        storage = sys.argv[i+1]
    else:
        storage = DEFAULT_STORAGE_PATH
    if '-a' in sys.argv:
        i = sys.argv.index('-a')
        archive = sys.argv[i+1]
    else:
        archive = DEFAULT_ARCHIVE_PATH

    my_server = DEFAULT_SERVER
    my_username = DEFAULT_USERNAME
    my_password = DEFAULT_PASSWORD

    if os.path.exists("common/date_storage.json"):
        with open('common/date_storage.json') as json_file:
            date_storage = json.load(json_file)
    else:
        date_storage = []
    day = 0
    while True:
        days = 90 - day
        if check_date(date_storage):
            print(date_storage)
            pass
        else:
            run(storage, archive, days)
            date_storage.append((datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y/%m/%d/"))
            print(date_storage)
            with open('common/date_storage.json', 'w', encoding='utf-8') as f:
                json.dump(date_storage, f, ensure_ascii=False, indent=4)
        if check_space(DEFAULT_STORAGE_DICK):
            day += 1
        sleep(DEFAULT_TIME_CHECK_INTERVAL)