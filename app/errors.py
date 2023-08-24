# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""


class VacancyNotFoundError(Error):
    """Raised when vacancy with provided it doesn't exist"""
