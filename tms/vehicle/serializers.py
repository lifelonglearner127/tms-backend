from django.shortcuts import get_object_or_404
from rest_framework import serializers
from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField


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


class VehicleBeforeDrivingCheckHistorySerializer(serializers.ModelSerializer):

    check_items = VehicleBeforeDrivingItemCheckSerializer(
        source='vehiclebeforedrivingitemcheck_set', many=True, read_only=True
    )

    class Meta:
        model = m.VehicleBeforeDrivingCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleBeforeDrivingCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'))
            m.VehicleBeforeDrivingItemCheck.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        return check_history


class VehicleDrivingItemCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleDrivingItemCheck
        exclude = ('vehicle_check_history', )


class VehicleDrivingCheckHistorySerializer(serializers.ModelSerializer):

    check_items = VehicleDrivingItemCheckSerializer(
        source='vehicledrivingitemcheck_set', many=True, read_only=True
    )

    class Meta:
        model = m.VehicleDrivingCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleDrivingCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'))
            m.VehicleDrivingItemCheck.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        return check_history


class VehicleAfterDrivingItemCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.VehicleAfterDrivingItemCheck
        exclude = ('vehicle_check_history', )


class VehicleAfterDrivingCheckHistorySerializer(serializers.ModelSerializer):

    check_items = VehicleAfterDrivingItemCheckSerializer(
        source='vehicleafterdrivingitemcheck_set', many=True, read_only=True
    )

    class Meta:
        model = m.VehicleAfterDrivingCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        check_history = m.VehicleAfterDrivingCheckHistory.objects.create(**validated_data)
        items = self.context.get('items')
        for item in items:
            check_item = get_object_or_404(m.VehicleCheckItem, id=item.get('id'))
            m.VehicleAfterDrivingItemCheck.objects.create(
                vehicle_check_history=check_history,
                item=check_item,
                is_checked=item.get('is_checked', False)
            )

        return check_history
