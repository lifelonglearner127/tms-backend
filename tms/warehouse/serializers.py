from rest_framework import serializers

# constants
from ..core import constants as c
# models
from . import models as m

# serializers
from ..account.serializers import ShortUserSerializer
from ..core.serializers import TMSChoiceField


class WarehouseProductNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.WarehouseProduct
        fields = (
            'id', 'name'
        )


class InTransactionSerializer(serializers.ModelSerializer):

    product = WarehouseProductNameSerializer(read_only=True)

    class Meta:
        model = m.InTransaction

    def create(self, validated_data):
        product = self.context.get('product')

        amount = validated_data.get('amount')
        product.amount += amount
        product.save()

        return m.InTransaction.objects.create(
            product=product,
            **validated_data
        )

    def update(self, instance, validated_data):
        product = self.context.get('product')

        amount = validated_data.get('amount')
        product.amount -= instance.amount
        product.amount += amount
        product.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class OutTransactionSerializer(serializers.ModelSerializer):

    product = WarehouseProductNameSerializer(read_only=True)

    class Meta:
        model = m.OutTransaction

    def create(self, validated_data):
        product = self.context.get('product')

        amount = validated_data.get('amount')
        product.amount -= amount
        product.save()

        return m.InTransaction.objects.create(
            product=product,
            **validated_data
        )

    def update(self, instance, validated_data):
        product = self.context.get('product')

        amount = validated_data.get('amount')
        product.amount += instance.amount
        product.amount -= amount
        product.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class InTransactionHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.InTransaction
        exclude = (
            'product',
        )


class OutTransactionHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OutTransaction
        exclude = (
            'product',
        )


class WarehouseProductSerializer(serializers.ModelSerializer):

    assignee = ShortUserSerializer(read_only=True)
    in_transactions = InTransactionHistorySerializer(
        many=True, read_only=True
    )
    out_transactions = OutTransactionHistorySerializer(
        many=True, read_only=True
    )
    amount_unit = TMSChoiceField(choices=c.WEIGHT_UNIT)

    class Meta:
        model = m.WarehouseProduct
        fields = '__all__'

    def create(self, validated_data):
        assignee_data = self.context.get('assignee')
        if assignee_data is None:
            raise serializers.ValidationError({
                'asignee': 'Assignee data is missing'
            })

        try:
            assignee = m.User.objects.get(id=assignee_data.get('id'))
        except m.User.DoesNotExists:
            raise serializers.ValidationError({
                'asignee': 'Assignee data is missing'
            })

        product = m.WarehouseProduct.objects.create(
            assignee=assignee,
            **validated_data
        )

        return product

    def update(self, instance, validated_data):
        assignee_data = self.context.get('assignee')
        if assignee_data is None:
            raise serializers.ValidationError({
                'asignee': 'Assignee data is missing'
            })

        try:
            assignee = m.User.objects.get(id=assignee_data.get('id'))
        except m.User.DoesNotExists:
            raise serializers.ValidationError({
                'asignee': 'Assignee data is missing'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.assignee = assignee
        instance.save()

        return instance
