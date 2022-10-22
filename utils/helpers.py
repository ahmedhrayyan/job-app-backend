import re
from sqlalchemy.exc import IntegrityError


def parse_integrity_error(error: IntegrityError) -> str:
    """ Format SQLAlchemy Integrity error """
    message = str(error.orig)
    # Select unique field key & value from error message (they usually exist in parentheses)
    unique_field = re.findall("(?:\()([^()]+)(?:\))", message)  # select everything in parentheses
    print(unique_field)
    if len(unique_field) == 2:
        return f'Account with {unique_field[0]} ({unique_field[1]}) already exists'
    else:
        # just return the error message if our regex was not able to select unique key field & value
        # happens because different databases have different message formats
        return message
