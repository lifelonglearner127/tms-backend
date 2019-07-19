from rest_framework import serializers


class ChoiceSerializer(serializers.Serializer):
    """
    Used for serializing backend constant choices
    """
    value = serializers.CharField()
    text = serializers.CharField()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        if isinstance(data, six.string_types) and\
           data.startswith('data:image'):

            header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class TMSChoiceField(serializers.Field):

    def __init__(self, choices, **kwargs):
        self.choices = dict((x, y) for x, y in choices)
        super().__init__(**kwargs)

    def to_representation(self, value):
        try:
            text = self.choices[value]
        except KeyError:
            text = 'Unknown'
        ret = {
            'value': value,
            'text': text
        }
        return ret

    def to_internal_value(self, data):
        return data['value']
