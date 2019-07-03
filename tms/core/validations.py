from django.core.exceptions import ValidationError


def validate_mobile(value):
    """
    Validator for mobile field
    """
    if not value.isdigit():
        raise ValidationError(
            '%(value)s is invalid phone number',
            params={'value': value},
        )


def validate_username(value):
    """
    Validator for username field
    """
    if not value.isalnum():
        raise ValidationError(
            '%(value)s is invalid username, alphanumerics are only allowed',
            params={'value': value},
        )
