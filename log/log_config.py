import logging
import os
import sys
import logging.handlers


format_log = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'main.log')

server_handler = logging.StreamHandler(sys.stderr)
server_handler.setFormatter(format_log)
server_handler.setLevel(logging.ERROR)

log_file = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
log_file.setFormatter(format_log)

log = logging.getLogger('main')
log.addHandler(server_handler)
log.addHandler(log_file)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    log.critical('Критическая ошибка')
    log.error('Ошибка')
    log.debug('Отладочная информация')
    log.info('Информационное сообщение')