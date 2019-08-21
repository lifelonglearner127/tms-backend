from django.shortcuts import get_object_or_404
from rest_framework import serializers
from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField, Base64ImageField


class FuelConsumptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelConsumption
        fields = '__all__'


class TireSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Tire
        fields = '__all__'


class ShortVehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of vehicle
    """
    class Meta:
        model = m.Vehicle
        fields = (
            'id', 'plate_num'
        )


class VehicleSerializer(serializers.ModelSerializer):
    """
    Vehicle serializer
    """
    model = TMSChoiceField(choices=c.VEHICLE_MODEL_TYPE)
    brand = TMSChoiceField(choices=c.VEHICLE_BRAND)
    model_2 = TMSChoiceField(choices=c.VEHICLE_MODEL_TYPE)
    brand_2 = TMSChoiceField(choices=c.VEHICLE_BRAND)

    class Meta:
        model = m.Vehicle
        fields = '__all__'

    # def validate(self, data):
    #     if data['actual_load'] != sum(data['branches']):
    #         raise serializers.ValidationError({
    #             'branches': 'Sum of branches weight exceed total weight'
    #         })
    #     return data

    def to_internal_value(self, data):
        """
        Exclude date, datetimefield if its string is empty
        """
        for key, value in self.fields.items():
            if isinstance(value, serializers.DateField) and data[key] == '':
                data.pop(key)

        ret = super().to_internal_value(data)
        return ret


class VehiclePositionSerializer(serializers.Serializer):
    """
    Serializer for vehicle playback
    """
    plate_num = serializers.CharField()
    lnglat = serializers.SerializerMethodField()
    speed = serializers.SerializerMethodField()

    def get_lnglat(self, obj):
        return [
            float(obj['data']['loc']['lng']), float(obj['data']['loc']['lat'])
        ]

    def get_speed(self, obj):
        return [int(obj['data']['loc']['speed'])]


class VehicleMaintenanceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleMaintenanceRequest
        fields = '__all__'

    def validate(self, data):
        maintenance_from = data.get('maintenance_from', None)
        maintenance_to = data.get('maintenance_to', None)

        if maintenance_from > maintenance_to:
            raise serializers.ValidationError({
                'maintenance_to': 'Error'
            })

        return data


class VehicleStatusSerializer(serializers.Serializer):

    plate_num = serializers.CharField()
    driver = serializers.CharField()
    status = serializers.CharField()


class VehicleCheckItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleCheckItem
        fields = '__all__'


class VehicleCheckItemNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleCheckItem
        fields = (
            'id', 'name',
        )


class VehicleBeforeDrivingItemCheckSerializer(serializers.ModelSerializer):

    item = VehicleCheckItemNameSerializer(read_only=True)

    class Meta:
        model = m.VehicleBeforeDrivingItemCheck
        fields = ('item', 'is_checked')


class VehicleDrivingItemCheckSerializer(serializers.ModelSerializer):

    item = VehicleCheckItemNameSerializer(read_only=True)

    class Meta:
        model = m.VehicleDrivingItemCheck
        fields = ('item', 'is_checked')


class VehicleAfterDrivingItemCheckSerializer(serializers.ModelSerializer):

    item = VehicleCheckItemNameSerializer(read_only=True)

    class Meta:
        model = m.VehicleAfterDrivingItemCheck
        fields = ('item', 'is_checked')


class VehicleCheckDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleCheckDocument
        fields = '__all__'


class ShortVehicleCheckDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleCheckDocument
        fields = (
            'document',
        )


class VehicleCheckHistorySerializer(serializers.ModelSerializer):

    before_driving_checked_items = VehicleBeforeDrivingItemCheckSerializer(
        source='vehiclebeforedrivingitemcheck_set', many=True, read_only=True
    )
    driving_checked_items = VehicleDrivingItemCheckSerializer(
        source='vehicledrivingitemcheck_set', many=True, read_only=True
    )
    after_driving_checked_items = VehicleAfterDrivingItemCheckSerializer(
        source='vehicleafterdrivingitemcheck_set', many=True, read_only=True
    )

    before_driving_images = serializers.SerializerMethodField()
    driving_images = serializers.SerializerMethodField()
    after_driving_images = serializers.SerializerMethodField()
    before_driving_checked_time = serializers.DateTimeField(format='%Y-%m-%d', required=False)
    driving_checked_time = serializers.DateTimeField(format='%Y-%m-%d', required=False)
    after_driving_checked_time = serializers.DateTimeField(format='%Y-%m-%d', required=False)

    class Meta:
        model = m.VehicleCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        images = self.context.get('images')
        check_type = self.context.get('check_type')
        if check_type == c.VEHICLE_CHECK_TYPE_BEFORE_DRIVING:
            args = {'is_before_driving_item': True}
            model_class = m.VehicleBeforeDrivingItemCheck
        elif check_type == c.VEHICLE_CHECK_TYPE_DRIVING:
            args = {'is_driving_item': True}
            model_class = m.VehicleDrivingItemCheck
        elif check_type == c.VEHICLE_CHECK_TYPE_AFTER_DRIVING:
            args = {'is_after_driving_item': True}
            model_class = m.VehicleAfterDrivingItemCheck

        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'), **args)
            model_class.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        for image in images:
            image['vehicle_check_history'] = check_history.id
            image['document_type'] = check_type
            serializer = VehicleCheckDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return check_history

    def update(self, instance, validated_data):
        items = self.context.get('items')
        images = self.context.get('images')
        check_type = self.context.get('check_type')

        if check_type == c.VEHICLE_CHECK_TYPE_BEFORE_DRIVING:
            args = {'is_before_driving_item': True}
            model_class = m.VehicleBeforeDrivingItemCheck
            instance.before_driving_checked_items.clear()
            m.VehicleCheckDocument.objects.filter(
                vehicle_check_history=instance, document_type=c.VEHICLE_CHECK_TYPE_BEFORE_DRIVING
            ).delete()
        elif check_type == c.VEHICLE_CHECK_TYPE_DRIVING:
            args = {'is_driving_item': True}
            model_class = m.VehicleDrivingItemCheck
            instance.driving_checked_items.clear()
            m.VehicleCheckDocument.objects.filter(
                vehicle_check_history=instance, document_type=c.VEHICLE_CHECK_TYPE_DRIVING
            ).delete()
        elif check_type == c.VEHICLE_CHECK_TYPE_AFTER_DRIVING:
            args = {'is_after_driving_item': True}
            model_class = m.VehicleAfterDrivingItemCheck
            instance.after_driving_checked_items.clear()
            m.VehicleCheckDocument.objects.filter(
                vehicle_check_history=instance, document_type=c.VEHICLE_CHECK_TYPE_AFTER_DRIVING
            ).delete()

        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'), **args)
            model_class.objects.create(
                vehicle_check_history=instance,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        for image in images:
            image['vehicle_check_history'] = instance.id
            image['document_type'] = check_type
            serializer = VehicleCheckDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def get_before_driving_images(self, instance):
        ret = []
        for image in instance.images.filter(document_type=c.VEHICLE_CHECK_TYPE_BEFORE_DRIVING):
            ret.append(ShortVehicleCheckDocumentSerializer(
                image, context={'request': self.context.get('request')}).data
            )

        return ret

    def get_driving_images(self, instance):
        ret = []
        for image in instance.images.filter(document_type=c.VEHICLE_CHECK_TYPE_DRIVING):
            ret.append(ShortVehicleCheckDocumentSerializer(
                image, context={'request': self.context.get('request')}).data
            )

        return ret

    def get_after_driving_images(self, instance):
        ret = []
        for image in instance.images.filter(document_type=c.VEHICLE_CHECK_TYPE_AFTER_DRIVING):
            ret.append(ShortVehicleCheckDocumentSerializer(
                image, context={'request': self.context.get('request')}).data
            )

        return ret

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['before'] = {
            'items': ret.pop('before_driving_checked_items'),
            'problems': ret.pop('before_driving_problems'),
            'description': ret.pop('before_driving_description'),
            'images': ret.pop('before_driving_images')
        }

        ret['driving'] = {
            'items': ret.pop('driving_checked_items'),
            'problems': ret.pop('driving_problems'),
            'description': ret.pop('driving_description'),
            'images': ret.pop('driving_images')
        }

        ret['after'] = {
            'items': ret.pop('after_driving_checked_items'),
            'problems': ret.pop('after_driving_problems'),
            'description': ret.pop('after_driving_description'),
            'images': ret.pop('after_driving_images')
        }
        return ret


class VehicleDriverDailyBindSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleDriverDailyBind
        fields = '__all__'
