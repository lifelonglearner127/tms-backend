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

    class Meta:
        model = m.VehicleBeforeDrivingItemCheck
        exclude = ('vehicle_check_history', )


class VehicleBeforeDrivingDocumentOnlySerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleBeforeDrivingDocument
        fields = (
            'document',
        )


class VehicleBeforeDrivingDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleBeforeDrivingDocument
        fields = '__all__'


class VehicleBeforeDrivingCheckHistorySerializer(serializers.ModelSerializer):

    check_items = VehicleBeforeDrivingItemCheckSerializer(
        source='vehiclebeforedrivingitemcheck_set', many=True, read_only=True
    )

    images = serializers.SerializerMethodField()

    class Meta:
        model = m.VehicleBeforeDrivingCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleBeforeDrivingCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        images = self.context.get('images')
        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'), is_before_driving_item=True)
            m.VehicleBeforeDrivingItemCheck.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        for image in images:
            image['vehicle_check_history'] = check_history.id
            serializer = VehicleBeforeDrivingDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return check_history

    def get_images(self, instance):
        ret = []
        for image in instance.images.all():
            ret.append(VehicleBeforeDrivingDocumentOnlySerializer(
                image, context={'request': self.context.get('request')}).data)

        return ret


class VehicleDrivingItemCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleDrivingItemCheck
        exclude = ('vehicle_check_history', )


class VehicleDrivingDocumentOnlySerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleDrivingDocument
        fields = (
            'document',
        )


class VehicleDrivingDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleDrivingDocument
        fields = '__all__'


class VehicleDrivingCheckHistorySerializer(serializers.ModelSerializer):

    check_items = VehicleDrivingItemCheckSerializer(
        source='vehicledrivingitemcheck_set', many=True, read_only=True
    )
    images = serializers.SerializerMethodField()

    class Meta:
        model = m.VehicleDrivingCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleDrivingCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        images = self.context.get('images')

        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'), is_driving_item=True)
            m.VehicleDrivingItemCheck.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        for image in images:
            image['vehicle_check_history'] = check_history.id
            serializer = VehicleBeforeDrivingDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return check_history

    def get_images(self, instance):
        ret = []
        for image in instance.images.all():
            ret.append(VehicleBeforeDrivingDocumentOnlySerializer(
                image, context={'request': self.context.get('request')}).data)

        return ret


class VehicleAfterDrivingItemCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleAfterDrivingItemCheck
        exclude = ('vehicle_check_history', )


class VehicleAfterDrivingDocumentOnlySerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleAfterDrivingDocument
        fields = (
            'document',
        )


class VehicleAfterDrivingDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.VehicleAfterDrivingDocument
        fields = '__all__'


class VehicleAfterDrivingCheckHistorySerializer(serializers.ModelSerializer):

    check_items = VehicleAfterDrivingItemCheckSerializer(
        source='vehicleafterdrivingitemcheck_set', many=True, read_only=True
    )
    images = serializers.SerializerMethodField()

    class Meta:
        model = m.VehicleAfterDrivingCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleAfterDrivingCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        images = self.context.get('images')

        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'), is_after_driving_item=True)
            m.VehicleAfterDrivingItemCheck.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        for image in images:
            image['vehicle_check_history'] = check_history.id
            serializer = VehicleBeforeDrivingDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return check_history

    def get_images(self, instance):
        ret = []
        for image in instance.images.all():
            ret.append(VehicleBeforeDrivingDocumentOnlySerializer(
                image,
                context={'request': self.context.get('request')}
            ).data)

        return ret


class VehicleDriverDailyBindSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleDriverDailyBind
        fields = '__all__'
