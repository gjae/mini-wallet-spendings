class ExceptionsMessages:
    NOT_FUND_AVAILABLE = 'User funds not cover this movement on this account'


class NotFundAvailableException(Exception):
    """
        Exception used when funds no cover some spent
    """
    pass