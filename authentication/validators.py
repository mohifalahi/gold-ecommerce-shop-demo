import re

from django.core.exceptions import ValidationError


class HasLowerCaseValidator:
    def __init__(self):
        self.message = "The password must contain at least one lowercase character."

    def validate(self, password, user=None):
        if re.search('[a-z]', password) is None:
            raise ValidationError(self.message, code='missing_lower_case')

    def get_help_text(self):
        return self.message


class HasUpperCaseValidator:
    def __init__(self):
        self.message = "The password must contain at least one uppercase character."

    def validate(self, password, user=None):
        if re.search('[A-Z]', password) is None:
            raise ValidationError(self.message, code='missing_upper_case')

    def get_help_text(self):
        return self.message


class HasNumberValidator:
    def __init__(self):
        self.message = "The password must contain at least one numeric character."

    def validate(self, password, user=None):
        if re.search('[0-9]', password) is None:
            raise ValidationError(self.message, code='missing_numeric')

    def get_help_text(self):
        return self.message


class HasSymbolValidator:
    def __init__(self):
        self.message = "The password must contain at least one non-alphanumeric character (symbol)."

    def validate(self, password, user=None):
        if re.search('[^A-Za-z0-9]', password) is None:
            raise ValidationError(self.message, code='missing_symbol')

    def get_help_text(self):
        return self.message


def has_lower_case_validator(password):
    message = "The password must contain at least one lowercase character."
    if re.search('[a-z]', password) is None:
        raise ValidationError(message, code='missing_lower_case')

    return password


def has_upper_case_validator(password):
    message = "The password must contain at least one uppercase character."
    if re.search('[A-Z]', password) is None:
        raise ValidationError(message, code='missing_upper_case')

    return password


def has_number_validator(password):
    message = "The password must contain at least one numeric character."
    if re.search('[0-9]', password) is None:
        raise ValidationError(message, code='missing_numeric')

    return password


def has_symbol_validator(password):
    message = "The password must contain at least one non-alphanumeric character (symbol)."
    if re.search('[^A-Za-z0-9]', password) is None:
        raise ValidationError(message, code='missing_symbol')

    return password


def validate_phone_number(value):
    if str(value).__len__() != 10:
        raise ValidationError(
            '%(value) is not a phone number',
            params={'value': value},
        )
    else:
        return value


def validate_persian_alphabet(value):

    t = re.match(r'^[ آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]+$', value)
    if not t:
        raise ValidationError(
            'name must be in persian alphabet')
    else:
        return value


def validate_date(value):
    t = re.match(r'^[1-4]\d{3}\/((0[1-6]\/((3[0-1])|([1-2][0-9])|(0[1-9])))|((1[0-2]|(0[7-9]))\/(30|([1-2][0-9])|(0[1-9]))))$', value)
    if not t:
        raise ValidationError(
            'this is not a valid date. you must use yyyy-mm-dd format. for example 1366/09/15')

    y = int(value[0:4])
    m = int(value[5:7])
    d = int(value[8:])

    return value


