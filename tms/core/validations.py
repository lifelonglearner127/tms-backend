from django.core.exceptions import ValidationError


def validate_mobile(value):
    if not value.isdigit():
        raise ValidationError(
            '%(value)s is invalid phone number',
            params={'value': value},
        )
