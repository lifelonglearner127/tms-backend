from django.shortcuts import get_object_or_404
from rest_framework import serializers

# constants
from ..core import constants as c

# model
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField
from ..account.serializers import ShortUserSerializer
from ..vehicle.serializers import ShortVehicleSerializer
from ..order.serializers import ShortJobSerializer


# class ParkingRequestSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = m.ParkingRequest
#         fields = '__all__'


# class ParkingRequestDataViewSerializer(serializers.ModelSerializer):

#     vehicle = ShortVehicleSerializer()
#     driver = ShortUserSerializer()
#     escort = ShortUserSerializer()

#     class Meta:
#         model = m.ParkingRequest
#         fields = '__all__'


# class DriverChangeRequestSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = m.DriverChangeRequest
#         fields = '__all__'
#         read_only_fields = ('new_driver', )


# class DriverChangeRequestDataViewSerializer(serializers.ModelSerializer):

#     job = ShortJobSerializer()
#     old_driver = ShortUserSerializer()
#     new_driver = ShortUserSerializer()

#     class Meta:
#         model = m.DriverChangeRequest
#         fields = '__all__'


# class EscortChangeRequestSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = m.EscortChangeRequest
#         fields = '__all__'


# class EscortChangeRequestDataViewSerializer(serializers.ModelSerializer):

#     job = ShortJobSerializer()
#     new_escort = ShortUserSerializer()

#     class Meta:
#         model = m.EscortChangeRequest
#         fields = '__all__'


class RequestApproverSerializer(serializers.ModelSerializer):

    approver = ShortUserSerializer(read_only=True)
    approver_type = TMSChoiceField(choices=c.APPROVER_TYPE)

    class Meta:
        model = m.RequestApprover
        exclude = (
            'request',
        )


class RequestCCSerializer(serializers.ModelSerializer):

    cc = ShortUserSerializer(read_only=True)
    cc_type = TMSChoiceField(choices=c.CC_TYPE)

    class Meta:
        model = m.RequestCC
        exclude = (
            'request',
        )


class BasicRequestSerializer(serializers.ModelSerializer):

    requester = ShortUserSerializer(read_only=True)
    request_type = TMSChoiceField(choices=c.REQUEST_TYPE)
    request_time = serializers.DateTimeField(
        format='%Y-%m-%d', required=False
    )
    approvers = RequestApproverSerializer(
        source='requestapprover_set', many=True, read_only=True
    )
    ccs = RequestCCSerializer(
        source='requestcc_set', many=True, read_only=True
    )

    class Meta:
        model = m.BasicRequest
        fields = '__all__'


class RestRequestSerializer(serializers.ModelSerializer):

    request = BasicRequestSerializer(read_only=True)
    category = TMSChoiceField(choices=c.REST_REQUEST_CATEGORY)
    days = serializers.SerializerMethodField()

    class Meta:
        model = m.RestRequest
        fields = '__all__'

    def create(self, validated_data):
        requester = self.context.pop('requester')
        description = self.context.pop('description', '')
        approvers_data = self.context.pop('approvers', [])
        ccs_data = self.context.pop('ccs', [])

        basic_request = m.BasicRequest.objects.create(
            request_type=c.REQUEST_TYPE_REST,
            requester=requester,
            description=description
        )

        step = 0
        for approver_data in approvers_data:
            approver_type = approver_data.get('approver_type', None)
            approver = approver_data.get('approver', None)
            approver = m.User.objects.get(id=approver.get('id', None))

            m.RequestApprover.objects.create(
                request=basic_request,
                approver_type=approver_type['value'],
                approver=approver,
                step=step
            )
            step += 1

        for cc_data in ccs_data:
            cc_type = cc_data.get('cc_type', None)
            cc = cc_data.get('cc', None)
            cc = m.User.objects.get(id=cc.get('id', None))

            m.RequestCC.objects.create(
                request=basic_request,
                cc_type=cc_type['value'],
                cc=cc
            )

        return m.RestRequest.objects.create(request=basic_request, **validated_data)

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)

        if from_date > to_date:
            raise serializers.ValidationError({
                'to_date': 'Error'
            })

        return data

    def get_days(self, instance):
        return (instance.to_date - instance.from_date).days


class VehicleRepairRequestSerializer(serializers.ModelSerializer):

    request = BasicRequestSerializer(read_only=True)
    vehicle = ShortVehicleSerializer(read_only=True)
    category = TMSChoiceField(choices=c.VEHICLE_REPAIR_REQUEST_CATEGORY)

    class Meta:
        model = m.VehicleRepairRequest
        fields = '__all__'

    def create(self, validated_data):
        requester = self.context.pop('requester')
        description = self.context.pop('description', '')
        approvers_data = self.context.pop('approvers', [])
        ccs_data = self.context.pop('ccs', [])
        vehicle = self.context.pop('vehicle')

        basic_request = m.BasicRequest.objects.create(
            request_type=c.REQUEST_TYPE_VEHICLE_REPAIR,
            requester=requester,
            description=description
        )

        step = 0
        for approver_data in approvers_data:
            approver_type = approver_data.get('approver_type', None)
            approver = approver_data.get('approver', None)
            approver = m.User.objects.get(id=approver.get('id', None))

            m.RequestApprover.objects.create(
                request=basic_request,
                approver_type=approver_type['value'],
                approver=approver,
                step=step
            )
            step += 1

        for cc_data in ccs_data:
            cc_type = cc_data.get('cc_type', None)
            cc = cc_data.get('cc', None)
            cc = m.User.objects.get(id=cc.get('id', None))

            m.RequestCC.objects.create(
                request=basic_request,
                cc_type=cc_type['value'],
                cc=cc
            )

        return m.VehicleRepairRequest.objects.create(
            request=basic_request, vehicle=vehicle, **validated_data
        )

    def update(self, instance, validated_data):
        # TODO: update the approvers
        pass


class RestRequestDataSerializer(serializers.ModelSerializer):

    request = BasicRequestSerializer(read_only=True)
    category = TMSChoiceField(choices=c.REST_REQUEST_CATEGORY)
    days = serializers.SerializerMethodField()

    class Meta:
        model = m.RestRequest
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    requester = ShortUserSerializer(read_only=True)
    request_type = TMSChoiceField(choices=c.REQUEST_TYPE)
    request_time = serializers.DateTimeField(
        format='%Y-%m-%d', required=False
    )
    approvers = RequestApproverSerializer(
        source='requestapprover_set', many=True, read_only=True
    )
    ccs = RequestCCSerializer(
        source='requestcc_set', many=True, read_only=True
    )
    detail = serializers.SerializerMethodField()

    class Meta:
        model = m.BasicRequest
        fields = (
            'requester', 'request_type', 'request_time', 'approved', 'approved_time',
            'description', 'approvers', 'ccs', 'detail'
        )

    def get_detail(self, instance):
        if instance.request_type == c.REQUEST_TYPE_REST:
            pass