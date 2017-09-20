from flask_login import current_user
from seaborn.logger import log


def report(path, link, severity, message, user=None):
    """
        This should email the site admin on the message
    :param path:     str of the sub url path
    :param link:     str of a link to the error
    :param severity: int of the severity 1-10
    :param message:  str of a message of the error
    :param user:     str of the user unique id
    :return:         None
    """
    username = (user or current_user).username
    msg = 'Report: [%s] <%s> %s' % (username, path, message)
    if severity < 3:
        log.debug(msg)
    elif severity < 6:
        log.info(msg)
    elif severity < 7:
        log.warning(msg)
    elif severity < 10:
        log.error(msg)
    else:
        log.critical(msg)


def report_email(path, link, severity, message, user):
    """
        This should email the site admin on the message
    :param path:     str of the sub url path
    :param link:     str of a link to the error
    :param severity: int of the severity 1-10
    :param message:  str of a message of the error
    :param user:     str of the user unique id
    :return:         None
    """
    pass # todo make this report really email
