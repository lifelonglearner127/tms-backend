from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m
from ..hr.models import Department
from ..vehicle.models import Vehicle

# serializers
from ..account.serializers import ShortUserSerializer
from ..core.serializers import Base64ImageField, TMSChoiceField
from ..hr.serializers import ShortDepartmentSerializer
from ..vehicle.serializers import ShortVehicleSerializer


class OrderPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OrderPayment
        fields = '__all__'


class ShortETCCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = (
            'id', 'number'
        )


class DriverAppETCCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = (
            'id', 'number', 'balance'
        )


class ETCCardSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    department = ShortDepartmentSerializer()

    class Meta:
        model = m.ETCCard
        fields = '__all__'

    def to_internal_value(self, data):
        ret = data
        if 'vehicle' in data:
            ret['vehicle'] = get_object_or_404(Vehicle, id=data['vehicle']['id'])

        if 'department' in data:
            ret['department'] = get_object_or_404(Department, id=data['department']['id'])

        return ret


class ETCCardChargeHistorySerializer(serializers.ModelSerializer):

    card = ETCCardSerializer()

    class Meta:
        model = m.ETCCardChargeHistory
        fields = '__all__'

    def create(self, validated_data):
        card = self.validated_data['card']
        current_balance = card.balance

        if 'charged_on' not in validated_data:
            validated_data['charged_on'] = timezone.localdate()

        charge_history = m.ETCCardChargeHistory.objects.create(
            previous_amount=current_balance,
            after_amount=current_balance + float(validated_data['charged_amount']),
            **validated_data
        )
        card.balance += float(validated_data['charged_amount'])
        card.save()

        return charge_history

    def to_internal_value(self, data):
        ret = data
        if 'card' in data:
            ret['card'] = get_object_or_404(m.ETCCard, id=data['card']['id'])

        return ret


class ETCCardDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.ETCCardUsageDocument
        fields = '__all__'


class ETCCardUsageHistorySerializer(serializers.ModelSerializer):

    card = ETCCardSerializer()

    class Meta:
        model = m.ETCCardUsageHistory
        fields = '__all__'

    def create(self, validated_data):
        etc_usage = m.ETCCardUsageHistory.objects.create(
            driver=self.context.get('user'),
            paid_on=timezone.now(),
            **validated_data
        )
        etc_usage.card.balance -= validated_data['amount']
        etc_usage.card.save()

        images = self.context.get('images')
        for image in images:
            image['etc_usage'] = etc_usage.id
            serializer = ETCCardDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return etc_usage

    def to_internal_value(self, data):
        ret = data
        if 'card' in data:
            ret['card'] = get_object_or_404(m.ETCCard, id=data['card']['id'])

        return ret


class ShortFuelCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = (
            'id', 'number'
        )


class FuelCardSerializer(serializers.ModelSerializer):

    master = ShortFuelCardSerializer(read_only=True)
    vehicle = ShortVehicleSerializer(read_only=True)
    department = ShortDepartmentSerializer(read_only=True)

    class Meta:
        model = m.FuelCard
        fields = '__all__'

    def create(self, validated_data):
        master_data = self.context.get('master', None)
        department_data = self.context.get('department', None)
        vehicle_data = self.context.get('vehicle', None)

        if department_data is None:
            raise serializers.ValidationError({
                'department': 'department data is missing'
            })
        department = Department.objects.get(id=department_data.get('id'))
        master = None
        vehicle = None

        if validated_data['is_child']:
            if master_data is None:
                raise serializers.ValidationError({
                    'master': 'master data is missing'
                })
            else:
                master = m.FuelCard.masters.get(id=master_data.get('id'))

            if vehicle_data is None:
                raise serializers.ValidationError({
                    'vehicle': 'vehicle data is missing'
                })
            else:
                vehicle = Vehicle.objects.get(id=vehicle_data.get('id', None))

        return m.FuelCard.objects.create(
            master=master, vehicle=vehicle, department=department, **validated_data
        )

    def update(self, instance, validated_data):
        master_data = self.context.get('master', None)
        department_data = self.context.get('department', None)
        vehicle_data = self.context.get('vehicle', None)

        if department_data is None:
            raise serializers.ValidationError({
                'department': 'department data is missing'
            })
        department = Department.objects.get(id=department_data.get('id'))
        master = None
        vehicle = None

        if validated_data['is_child']:
            if master_data is None:
                raise serializers.ValidationError({
                    'master': 'master data is missing'
                })
            else:
                master = m.FuelCard.masters.get(id=master_data.get('id'))

            if vehicle_data is None:
                raise serializers.ValidationError({
                    'vehicle': 'vehicle data is missing'
                })
            else:
                vehicle = Vehicle.objects.get(id=vehicle_data.get('id', None))

        instance.master = master
        instance.department = department
        instance.vehicle = vehicle
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class FuelCardDataViewSerializer(serializers.ModelSerializer):

    department = ShortDepartmentSerializer()
    vehicle = ShortVehicleSerializer()
    master = ShortFuelCardSerializer()

    class Meta:
        model = m.FuelCard
        fields = '__all__'


# class BillSubCategoyChoiceField(serializers.Field):

#     def to_representation(self, instance):

#         if instance.category == c.BILL_FROM_LOADING_STATION:
#             sub_categories = c.LOADING_STATION_BILL_SUB_CATEGORY
#         elif instance.category == c.BILL_FROM_QUALITY_STATION:
#             sub_categories = c.QUALITY_STATION_BILL_SUB_CATEGORY
#         elif instance.category == c.BILL_FROM_UNLOADING_STATION:
#             sub_categories = c.UNLOADING_STATION_BILL_SUB_CATEGORY
#         elif instance.category == c.BILL_FROM_OIL_STATION:
#             sub_categories = c.OIL_BILL_SUB_CATEGORY
#         elif instance.category == c.BILL_FROM_TRAFFIC:
#             sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
#         elif instance.category == c.BILL_FROM_OTHER:
#             sub_categories = c.OTHER_BILL_SUB_CATEGORY

#         choices = dict((x, y) for x, y in sub_categories)
#         ret = {
#             'value': instance.sub_category,
#             'text': choices[instance.sub_category]
#         }
#         return ret

#     def to_internal_value(self, data):
#         return {
#             'sub_category': data['value']
#         }


# class BillDetailCategoyChoiceField(serializers.Field):

#     def to_representation(self, instance):
#         if (
#             instance.category != c.BILL_FROM_OTHER or
#             instance.sub_category != c.TRAFFIC_VIOLATION_BILL
#         ):
#             return None

#         choices = dict(
#             (x, y) for x, y in c.TRAFFIC_VIOLATION_DETAIL_CATEGORY
#         )
#         ret = {
#             'value': instance.detail_category,
#             'text': choices[instance.detail_category]
#         }
#         return ret

#     def to_internal_value(self, data):
#         return {
#             'detail_category': data['value']
#         }


# class ShortBillDocumentSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = m.BillDocument
#         fields = (
#             'amount', 'unit_price', 'cost',
#         )


# class BillDocumentSerializer(serializers.ModelSerializer):

#     bill = Base64ImageField()
#     category = TMSChoiceField(choices=c.BILL_CATEGORY)
#     sub_category = BillSubCategoyChoiceField(source='*', required=False)
#     detail_category = BillDetailCategoyChoiceField(source='*', required=False)

#     class Meta:
#         model = m.BillDocument
#         fields = '__all__'
#         read_only_fields = ('user', )

#     def create(self, validated_data):
#         user = self.context.get('user')
#         return m.BillDocument.objects.create(
#             user=user,
#             **validated_data
#         )

#     def update(self, instance, validated_data):
#         for (key, value) in validated_data.items():
#             setattr(instance, key, value)
#         instance.user = self.context('user')
#         instance.save()
#         return instance


class BillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.BillDocument
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)
    category = TMSChoiceField(choices=c.BILL_CATEGORY)
    images = serializers.SerializerMethodField()

    class Meta:
        model = m.Bill
        fields = '__all__'

    def create(self, validated_data):
        bill = m.Bill.objects.create(user=self.context.get('user'), **validated_data)
        images = self.context.get('images')
        for image in images:
            image['bill'] = bill.id
            serializer = BillDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return bill

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.images.all().delete()
        instance.save()

        images = self.context.get('images')
        for image in images:
            image['bill'] = instance.id
            serializer = BillDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return instance

    def get_images(self, instance):
        ret = []
        for image in instance.images.all():
            ret.append(BillDocumentSerializer(
                image, context={'request': self.context.get('request')}).data
            )

        return ret
