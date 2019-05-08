from django.core.exceptions import ValidationError


def validate_mobile(value):
    """
    Validator for mobile model field
    """
    if not value.isdigit():
        raise ValidationError(
            '%(value)s is invalid phone number',
            params={'value': value},
        )
