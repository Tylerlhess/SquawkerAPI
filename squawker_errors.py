from utils import get_logger

logger = get_logger('squawker_errors')


class LoggedBaseException(BaseException):
    def __init__(self, message=""):
        self.message = message
        logger.info(f"logging error {self.__name__} {self.message} ")
        super().__init__(self.message)


class InvalidProfileJSON(LoggedBaseException):
    pass


class NotMessage(LoggedBaseException):
    pass


class NotRegistered(LoggedBaseException):
    pass


class NoProfile(LoggedBaseException):
    pass


class BadCredentials(LoggedBaseException):
    pass


class AlreadyRegistered(LoggedBaseException):
    pass


class NotListing(LoggedBaseException):
    pass


class TransactionError(LoggedBaseException):
    pass


class InsufficientFunds(LoggedBaseException):
    pass


class NoFunds(LoggedBaseException):
    pass


class Funds(LoggedBaseException):
    pass
