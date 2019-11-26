from rest_framework import serializers

# constants

# models
from . import models as m

# serializers
from ..account.serializers import (
    MainUserSerializer, UserNameTypeSerializer
)


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
        fields = '__all__'

    def create(self, validated_data):
        product = self.context.get('product')

        amount = validated_data.get('amount')
        validated_data['price'] = amount * validated_data.get('unit_price')
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
    recipient = UserNameTypeSerializer(read_only=True)

    class Meta:
        model = m.OutTransaction
        fields = '__all__'

    def create(self, validated_data):
        product = self.context.get('product')
        recipient_data = self.context.get('recipient')
        if recipient_data is None:
            raise serializers.ValidationError({
                'recipient': 'Recipient data is missing'
            })

        try:
            recipient = m.User.objects.get(pk=recipient_data.get('id'))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'recipient': 'Recipient data is missing'
            })

        amount = validated_data.get('amount')
        product.amount -= amount
        product.save()

        return m.OutTransaction.objects.create(
            product=product,
            recipient=recipient,
            **validated_data
        )

    def update(self, instance, validated_data):
        product = self.context.get('product')
        recipient_data = self.context.get('recipient')
        if recipient_data is None:
            raise serializers.ValidationError({
                'recipient': 'Recipient data is missing'
            })

        try:
            recipient = m.User.objects.get(pk=recipient_data.get('id'))
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'recipient': 'Recipient data is missing'
            })

        amount = validated_data.get('amount')
        product.amount += instance.amount
        product.amount -= amount
        product.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.recipient = recipient
        instance.save()
        return instance


class InTransactionHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.InTransaction
        exclude = (
            'product',
        )


class InTransactionHistoryExportSerializer(serializers.ModelSerializer):

    product = serializers.CharField(source='product.name')
    transaction_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = m.InTransaction
        fields = (
            'product', 'ticket_type', 'unit_price', 'amount', 'amount_unit', 'supplier',
            'supplier_contact', 'supplier_mobile', 'transaction_on',
        )


class OutTransactionHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.OutTransaction
        exclude = (
            'product',
        )


class OutTransactionHistoryExportSerializer(serializers.ModelSerializer):

    product = serializers.CharField(source='product.name')
    recipient = serializers.CharField(source='recipient.name')
    transaction_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = m.OutTransaction
        fields = (
            'product', 'recipient', 'unit_price', 'amount', 'amount_unit',
            'transaction_on', 'vehicle', 'ticket_type'
        )


class WarehouseProductSerializer(serializers.ModelSerializer):

    assignee = MainUserSerializer(read_only=True)
    in_transactions = InTransactionHistorySerializer(
        many=True, read_only=True
    )
    out_transactions = OutTransactionHistorySerializer(
        many=True, read_only=True
    )

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
        except m.User.DoesNotExist:
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
        except m.User.DoesNotExist:
            raise serializers.ValidationError({
                'asignee': 'Assignee data is missing'
            })

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.assignee = assignee
        instance.save()

        return instance
