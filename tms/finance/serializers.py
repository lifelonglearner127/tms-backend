from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..core import constants as c

# models
from . import models as m
from ..hr.models import Department
from ..vehicle.models import Vehicle

# serializers
from ..account.serializers import MainUserSerializer
from ..core.serializers import Base64ImageField, TMSChoiceField
from ..hr.serializers import ShortDepartmentSerializer
from ..vehicle.serializers import ShortVehicleSerializer
from ..info.serializers import StationNameSerializer


class ETCCardNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = (
            'id', 'number'
        )


class ETCCardBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ETCCard
        fields = (
            'id', 'number', 'balance'
        )


class ETCCardSerializer(serializers.ModelSerializer):

    master = ETCCardNumberSerializer(read_only=True)
    vehicle = ShortVehicleSerializer(read_only=True)
    department = ShortDepartmentSerializer(read_only=True)

    class Meta:
        model = m.ETCCard
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
                master = m.ETCCard.masters.get(id=master_data.get('id'))

            if vehicle_data is None:
                raise serializers.ValidationError({
                    'vehicle': 'vehicle data is missing'
                })
            else:
                vehicle = Vehicle.objects.get(id=vehicle_data.get('id', None))

        return m.ETCCard.objects.create(
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
                master = m.ETCCard.masters.get(id=master_data.get('id'))

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


class ETCCardChargeHistorySerializer(serializers.ModelSerializer):

    card = ETCCardSerializer()
    charged_on = serializers.DateTimeField(format='%Y-%m-%d', required=False)

    class Meta:
        model = m.ETCCardChargeHistory
        fields = '__all__'


class ShortETCBillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.ETCBillDocument
        exclude = (
            'etc_bill',
        )


class ETCBillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.ETCBillDocument
        fields = '__all__'


class ETCBillHistorySerializer(serializers.ModelSerializer):

    card = ETCCardNumberSerializer()
    paid_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    images = serializers.SerializerMethodField()

    class Meta:
        model = m.ETCBillHistory
        fields = '__all__'

    def create(self, validated_data):
        etc_bill = m.ETCBillHistory.objects.create(
            driver=self.context.get('user'),
            paid_on=timezone.now(),
            **validated_data
        )
        if validated_data.get('is_card', False):
            etc_bill.card.balance -= validated_data['amount']
            etc_bill.card.save()

        images = self.context.get('images')
        for image in images:
            image['etc_bill'] = etc_bill.id
            serializer = ETCBillDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return etc_bill

    def to_internal_value(self, data):
        if data.get('is_card', False):
            data['card'] = get_object_or_404(m.ETCCard, id=data['card']['id'])
        else:
            data.pop('card', None)

        return data

    def get_images(self, instance):
        return ShortETCBillDocumentSerializer(
            instance.images.all(), context={'request': self.context.get('request')}, many=True
        ).data


class FuelCardNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = (
            'id', 'number'
        )


class FuelCardBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelCard
        fields = (
            'id', 'number', 'balance'
        )


class FuelCardSerializer(serializers.ModelSerializer):

    master = FuelCardNumberSerializer(read_only=True)
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


class FuelCardChargeHistorySerializer(serializers.ModelSerializer):

    card = FuelCardSerializer()
    charged_on = serializers.DateTimeField(format='%Y-%m-%d', required=False)

    class Meta:
        model = m.FuelCardChargeHistory
        fields = '__all__'

    def create(self, validated_data):
        card = self.validated_data['card']
        current_balance = card.balance

        if 'charged_on' not in validated_data:
            validated_data['charged_on'] = timezone.now()

        charge_history = m.FuelCardChargeHistory.objects.create(
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
            ret['card'] = get_object_or_404(m.FuelCard, id=data['card']['id'])

        return ret


class ShortFuelBillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.FuelBillDocument
        exclude = (
            'fuel_bill',
        )


class FuelBillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.FuelBillDocument
        fields = '__all__'


class FuelBillHistorySerializer(serializers.ModelSerializer):

    card = FuelCardNumberSerializer()
    oil_station = StationNameSerializer()
    driver = MainUserSerializer(read_only=True)
    paid_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    created_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    images = serializers.SerializerMethodField()

    class Meta:
        model = m.FuelBillHistory
        fields = '__all__'

    def create(self, validated_data):
        fuel_bill = m.FuelBillHistory.objects.create(
            driver=self.context.get('user'),
            paid_on=timezone.now(),
            **validated_data
        )
        if validated_data.get('is_card', False):
            fuel_bill.card.balance -= validated_data['total_price']
            fuel_bill.card.save()

        images = self.context.get('images')
        for image in images:
            image['fuel_bill'] = fuel_bill.id
            serializer = FuelBillDocumentSerializer(
                data=image,
                context={'request': self.context.get('request')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return fuel_bill

    def to_internal_value(self, data):
        if data.get('is_card', False):
            data['card'] = get_object_or_404(m.FuelCard, id=data['card']['id'], is_child=True)
        else:
            data.pop('card', None)

        if 'oil_station' in data:
            data['oil_station'] = get_object_or_404(
                m.Station, id=data['oil_station']['id'],
                station_type=c.STATION_TYPE_OIL_STATION
            )

        return data

    def get_images(self, instance):
        return ShortFuelBillDocumentSerializer(
            instance.images.all(), context={'request': self.context.get('request')}, many=True
        ).data


class BillDocumentSerializer(serializers.ModelSerializer):

    document = Base64ImageField()

    class Meta:
        model = m.BillDocument
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):

    user = MainUserSerializer(read_only=True)
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
        return BillDocumentSerializer(
            instance.images.all(), context={'request': self.context.get('request')}, many=True
        ).data
