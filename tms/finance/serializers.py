from rest_framework import serializers

from . import models as m
from ..core import constants as c
from ..core.serializers import Base64ImageField, TMSChoiceField
from ..hr.serializers import ShortDepartmentSerializer
from ..vehicle.serializers import ShortVehicleSerializer


class OrderPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OrderPayment
        fields = '__all__'


class OrderPaymentDataViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OrderPayment
        fields = '__all__'


class ShortETCCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = (
            'id', 'number'
        )


class ETCCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = '__all__'


class ETCCardDataViewSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer()
    vehicle = ShortVehicleSerializer()

    class Meta:
        model = m.ETCCard
        fields = '__all__'


class ShortFuelCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = (
            'id', 'number'
        )


class FuelCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = '__all__'

    def validate(self, data):
        master = data.get('master', None)
        vehicle = data.get('vehicle', None)
        if master is not None and vehicle is None:
            raise serializers.ValidationError({
                'vehicle': 'Vehicle is required'
            })

        return data


class FuelCardDataViewSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer()
    vehicle = ShortVehicleSerializer()
    master = ShortFuelCardSerializer()

    class Meta:
        model = m.FuelCard
        fields = '__all__'


class BillSubCategoyChoiceField(serializers.Field):

    def to_representation(self, instance):

        if instance.category == c.BILL_FROM_LOADING_STATION:
            sub_categories = c.LOADING_STATION_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_QUALITY_STATION:
            sub_categories = c.QUALITY_STATION_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_UNLOADING_STATION:
            sub_categories = c.UNLOADING_STATION_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_OIL_STATION:
            sub_categories = c.OIL_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_TRAFFIC:
            sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
        elif instance.category == c.BILL_FROM_OTHER:
            sub_categories = c.OTHER_BILL_SUB_CATEGORY

        choices = dict((x, y) for x, y in sub_categories)
        ret = {
            'value': instance.sub_category,
            'text': choices[instance.sub_category]
        }
        return ret

    def to_internal_value(self, data):
        return {
            'sub_category': data['value']
        }


class BillDetailCategoyChoiceField(serializers.Field):

    def to_representation(self, instance):
        if (
            instance.category != c.BILL_FROM_OTHER or
            instance.sub_category != c.TRAFFIC_VIOLATION_BILL
        ):
            return None

        choices = dict(
            (x, y) for x, y in c.TRAFFIC_VIOLATION_DETAIL_CATEGORY
        )
        ret = {
            'value': instance.detail_category,
            'text': choices[instance.detail_category]
        }
        return ret

    def to_internal_value(self, data):
        return {
            'detail_category': data['value']
        }


class ShortBillDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.BillDocument
        fields = (
            'amount', 'unit_price', 'cost',
        )


class BillDocumentSerializer(serializers.ModelSerializer):

    bill = Base64ImageField()
    category = TMSChoiceField(choices=c.BILL_CATEGORY)
    sub_category = BillSubCategoyChoiceField(source='*', required=False)
    detail_category = BillDetailCategoyChoiceField(source='*', required=False)

    class Meta:
        model = m.BillDocument
        fields = '__all__'
        read_only_fields = ('user', )

    def create(self, validated_data):
        user = self.context.get('user')
        print(validated_data)
        return m.BillDocument.objects.create(
            user=user,
            **validated_data
        )

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.user = self.context('user')
        instance.save()
        return instance
