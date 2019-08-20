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


class ParkingRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ParkingRequest
        fields = '__all__'


class ParkingRequestDataViewSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = ShortUserSerializer()
    escort = ShortUserSerializer()

    class Meta:
        model = m.ParkingRequest
        fields = '__all__'


class DriverChangeRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.DriverChangeRequest
        fields = '__all__'
        read_only_fields = ('new_driver', )


class DriverChangeRequestDataViewSerializer(serializers.ModelSerializer):

    job = ShortJobSerializer()
    old_driver = ShortUserSerializer()
    new_driver = ShortUserSerializer()

    class Meta:
        model = m.DriverChangeRequest
        fields = '__all__'


class EscortChangeRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.EscortChangeRequest
        fields = '__all__'


class EscortChangeRequestDataViewSerializer(serializers.ModelSerializer):

    job = ShortJobSerializer()
    new_escort = ShortUserSerializer()

    class Meta:
        model = m.EscortChangeRequest
        fields = '__all__'


class RestRequestApproverSerializer(serializers.ModelSerializer):

    approver = ShortUserSerializer(read_only=True)
    approver_type = TMSChoiceField(choices=c.APPROVER_TYPE)

    class Meta:
        model = m.RestRequestApprover
        exclude = (
            'rest_request',
        )


class RestRequestCCSerializer(serializers.ModelSerializer):

    cc = ShortUserSerializer(read_only=True)
    cc_type = TMSChoiceField(choices=c.CC_TYPE)

    class Meta:
        model = m.RestRequestCC
        exclude = (
            'rest_request',
        )


class RestRequestSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)
    category = TMSChoiceField(choices=c.REST_REQUEST_CATEGORY)
    approvers = RestRequestApproverSerializer(
        source='restrequestapprover_set', many=True, read_only=True
    )
    ccs = RestRequestCCSerializer(
        source='restrequestcc_set', many=True, read_only=True
    )
    request_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    days = serializers.SerializerMethodField()
    is_approvable = serializers.SerializerMethodField()

    class Meta:
        model = m.RestRequest
        fields = '__all__'

    def create(self, validated_data):
        user = self.context.pop('user')
        approvers_data = self.context.pop('approvers', [])
        ccs_data = self.context.pop('ccs', [])

        rest_request = m.RestRequest.objects.create(
            user=user,
            **validated_data
        )

        step = 0
        for approver_data in approvers_data:
            approver_type = approver_data.get('approver_type', None)
            approver = approver_data.get('approver', None)
            approver = m.User.objects.get(id=approver.get('id', None))

            m.RestRequestApprover.objects.create(
                rest_request=rest_request,
                approver_type=approver_type['value'],
                approver=approver,
                step=step
            )
            step += 1

        for cc_data in ccs_data:
            cc_type = cc_data.get('cc_type', None)
            cc = cc_data.get('cc', None)
            cc = m.User.objects.get(id=cc.get('id', None))

            m.RestRequestCC.objects.create(
                rest_request=rest_request,
                cc_type=cc_type['value'],
                cc=cc
            )

        return rest_request

    def update(self, instance, validated_data):
        user = self.context.pop('user')
        # TODO: update the approvers

        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.user = user
        instance.save()
        return instance

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

    def get_is_approvable(self, instance):
        requester = self.context.get('requester')
        return requester in instance.approvers.all()
