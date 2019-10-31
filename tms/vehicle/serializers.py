from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from ..core import constants as c

# models
from . import models as m

# serializers
from ..core.serializers import TMSChoiceField, Base64ImageField
from ..account.serializers import MainUserSerializer
from ..info.serializers import StationLocationSerializer, StationNameSerializer

# other
from ..core import utils


class FuelConsumptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.FuelConsumption
        fields = '__all__'


class ShortVehiclePlateNumSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Vehicle
        fields = (
            'id', 'plate_num',
        )


class ShortVehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for short data of vehicle
    """
    # bound_driver = MainUserSerializer(read_only=True)

    class Meta:
        model = m.Vehicle
        fields = (
            'id',
            'plate_num',
            'status',
            'total_load',
            'branches',
        )


class ShortVehicleStatusSerializer(serializers.ModelSerializer):

    status = TMSChoiceField(choices=c.VEHICLE_STATUS)

    class Meta:
        model = m.Vehicle
        fields = (
            'id',
            'plate_num',
            'status'
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


class ShortVehicleCheckHistorySerializer(serializers.ModelSerializer):

    plate_num = serializers.CharField(source='vehicle.plate_num')
    driver = serializers.CharField(source='driver.name')
    checked_on = serializers.DateTimeField(
        source='created',
        format='%Y-%m-%d'
    )

    class Meta:
        model = m.VehicleCheckHistory
        fields = (
            'id',
            'plate_num',
            'driver',
            'checked_on',
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
    driver = MainUserSerializer(read_only=True)
    total_problems = serializers.SerializerMethodField()
    before_driving_images = serializers.SerializerMethodField()
    driving_images = serializers.SerializerMethodField()
    after_driving_images = serializers.SerializerMethodField()
    before_driving_checked_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    driving_checked_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    after_driving_checked_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    is_readonly = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    updated = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

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

    def get_is_readonly(self, instance):
        if not self.context.get('bind', False):
            return True

        get_on_time = self.context.get('get_on_time')
        try:
            # check with existing checked time
            if instance.before_driving_checked_time:
                if instance.before_driving_checked_time < get_on_time:
                    return True
                else:
                    return False
            elif instance.driving_checked_items:
                if instance.driving_checked_items < get_on_time:
                    return True
                else:
                    return False
            elif instance.after_driving_checked_time:
                if instance.after_driving_checked_time < get_on_time:
                    return True
                else:
                    return False
            else:
                return False
        except Exception:
            return False

    def get_total_problems(self, instance):
        return instance.before_driving_problems + instance.driving_problems + instance.after_driving_problems

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['vehicle'] = {
            'id': instance.vehicle.id,
            'plate_num': instance.vehicle.plate_num
        }

        ret['before'] = {
            'items': ret.pop('before_driving_checked_items'),
            'itemsCount': m.VehicleCheckItem.published_before_driving_check_items.count(),
            'problems': ret.pop('before_driving_problems'),
            'description': ret.pop('before_driving_description'),
            'images': ret.pop('before_driving_images')
        }

        ret['driving'] = {
            'items': ret.pop('driving_checked_items'),
            'itemsCount': m.VehicleCheckItem.published_driving_check_items.count(),
            'problems': ret.pop('driving_problems'),
            'description': ret.pop('driving_description'),
            'images': ret.pop('driving_images')
        }

        ret['after'] = {
            'items': ret.pop('after_driving_checked_items'),
            'itemsCount': m.VehicleCheckItem.published_after_driving_check_items.count(),
            'problems': ret.pop('after_driving_problems'),
            'description': ret.pop('after_driving_description'),
            'images': ret.pop('after_driving_images')
        }
        return ret


class VehicleDriverDailyBindSerializer(serializers.ModelSerializer):

    get_off_station = StationNameSerializer(required=False)

    class Meta:
        model = m.VehicleDriverDailyBind
        fields = '__all__'


class VehicleMaintenanceHistorySerializer(serializers.ModelSerializer):

    category = TMSChoiceField(choices=c.VEHICLE_MAINTENANCE_CATEGORY)
    vehicle = ShortVehicleSerializer(read_only=True)
    assignee = MainUserSerializer(read_only=True)
    station = StationLocationSerializer(read_only=True)

    class Meta:
        model = m.VehicleMaintenanceHistory
        fields = '__all__'

    def create(self, validated_data):
        vehicle = get_object_or_404(
            m.Vehicle, id=self.context['vehicle']['id']
        )
        assignee = get_object_or_404(
            m.User, id=self.context['assignee']['id']
        )
        station = get_object_or_404(
            m.Station, id=self.context['station']['id']
        )
        return m.VehicleMaintenanceHistory.objects.create(
            vehicle=vehicle,
            assignee=assignee,
            station=station,
            **validated_data
        )

    def update(self, instance, validated_data):
        vehicle = get_object_or_404(
            m.Vehicle, id=self.context['vehicle']['id']
        )
        assignee = get_object_or_404(
            m.User, id=self.context['assignee']['id']
        )
        station = get_object_or_404(
            m.Station, id=self.context['station']['id']
        )

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.vehicle = vehicle
        instance.assignee = assignee
        instance.station = station
        instance.save()
        return instance


class TireManagementHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = m.TireManagementHistory
        fields = '__all__'


class ShortTireManagementHistorySerializer(serializers.ModelSerializer):

    mileage = serializers.SerializerMethodField()

    class Meta:
        model = m.TireManagementHistory
        exclude = (
            'vehicle_tire',
        )

    def get_mileage(self, instance):
        if instance.mileage is not None:
            return instance.mileage
        else:
            return utils.get_mileage(
                instance.vehicle_tire.vehicle.plate_num,
                instance.installed_on,
                timezone.now()
            )


class ShortVehicleTireSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()

    class Meta:
        model = m.VehicleTire
        fields = '__all__'


class TireManagementHistoryDataViewSerializer(serializers.ModelSerializer):

    vehicle_tire = ShortVehicleTireSerializer()

    class Meta:
        model = m.TireManagementHistory
        fields = '__all__'


class TireTreadDepthCheckHistorySerializer(serializers.Serializer):

    id = serializers.IntegerField()
    vehicle = serializers.CharField(source='tire.vehicle_tire.vehicle.plate_num')
    position = serializers.CharField(source='tire.vehicle_tire.position')
    installed_on = serializers.DateTimeField(source='tire.installed_on')
    checked_on = serializers.DateTimeField()
    tread_depth = serializers.FloatField()
    before_tread_depth = serializers.FloatField()


class VehicleTireSerializer(serializers.ModelSerializer):

    current_tire = serializers.SerializerMethodField()

    class Meta:
        model = m.VehicleTire
        fields = '__all__'

    def get_current_tire(self, instance):
        if instance.history.first() is not None:
            return ShortTireManagementHistorySerializer(instance.history.first()).data
        else:
            return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['vehicle'] = {
            'id': instance.vehicle.id,
            'plate_num': instance.vehicle.plate_num
        }
        return ret


class VehicleDriverEscortBindSerializer(serializers.ModelSerializer):

    vehicle = ShortVehicleSerializer()
    driver = MainUserSerializer()
    escort = MainUserSerializer()

    class Meta:
        model = m.VehicleDriverEscortBind
        fields = '__all__'

    def validate(self, data):
        vehicle = data['vehicle']
        driver = data['driver']
        escort = data['escort']

        if self.instance is None:

            if m.VehicleDriverEscortBind.objects.filter(vehicle=vehicle).exists():
                raise serializers.ValidationError({
                    'vehicle': '车辆已存在'
                })

            if m.VehicleDriverEscortBind.objects.filter(driver=driver).exists():
                raise serializers.ValidationError({
                    'driver': '司机已存在'
                })
            if m.VehicleDriverEscortBind.objects.filter(escort=escort).exists():
                raise serializers.ValidationError({
                    'escort': '押运员已存在'
                })

        else:
            if m.VehicleDriverEscortBind.objects.exclude(id=self.instance.id).filter(vehicle=vehicle).exists():
                raise serializers.ValidationError({
                    'vehicle': '车辆已存在'
                })

            if m.VehicleDriverEscortBind.objects.exclude(id=self.instance.id).filter(driver=driver).exists():
                raise serializers.ValidationError({
                    'driver': '司机已存在'
                })
            if m.VehicleDriverEscortBind.objects.exclude(id=self.instance.id).filter(escort=escort).exists():
                raise serializers.ValidationError({
                    'escort': '押运员已存在'
                })

        return data

    def to_internal_value(self, data):
        ret = {
            'vehicle': get_object_or_404(m.Vehicle, id=data['vehicle']['id']),
            'driver': get_object_or_404(m.User, id=data['driver']['id']),
            'escort': get_object_or_404(m.User, id=data['escort']['id'])
        }
        return ret


# version 2
class VehicleBindDetailSerializer(serializers.ModelSerializer):

    driver = serializers.SerializerMethodField()
    escort = serializers.SerializerMethodField()
    total_branch_size = serializers.SerializerMethodField()
    current_progress = serializers.SerializerMethodField()

    class Meta:
        model = m.Vehicle
        fields = (
            'id',
            'plate_num',
            'total_branch_size',
            'driver',
            'escort',
            'current_progress',
            'license_expires_on',
        )

    def get_driver(self, instance):
        try:
            vehicle_bind = instance.bind
        except m.VehicleDriverEscortBind.DoesNotExist:
            return None

        return {
            'id': vehicle_bind.driver.id,
            'name': vehicle_bind.driver.name,
            'mobile': vehicle_bind.driver.mobile,
            'id_card': vehicle_bind.driver.profile.id_card
        }

    def get_escort(self, instance):
        try:
            vehicle_bind = instance.bind
        except m.VehicleDriverEscortBind.DoesNotExist:
            return None

        return {
            'id': vehicle_bind.escort.id,
            'name': vehicle_bind.escort.name,
            'mobile': vehicle_bind.escort.mobile,
            'id_card': vehicle_bind.escort.profile.id_card,
        }

    def get_total_branch_size(self, instance):
        total_branch_size = 0
        for branch in instance.branches:
            total_branch_size += branch

        return total_branch_size

    def get_current_progress(self, instance):
        current_job = instance.jobs.filter(progress__gt=c.JOB_PROGRESS_NOT_STARTED).first()
        if current_job is None:
            return '无任务'

        if current_job.progress >= 10:
            if (current_job.progress - 10) % 4 == 0:
                progress = 10
            elif (current_job.progress - 10) % 4 == 1:
                progress = 11
            elif (current_job.progress - 10) % 4 == 2:
                progress = 12
            elif (current_job.progress - 10) % 4 == 3:
                progress = 13
        else:
            progress = current_job.progress

        return c.JOB_PROGRESS.get(progress, '无任务')


class VehicleViolationSerializer(serializers.ModelSerializer):

    # vehicle = ShortVehiclePlateNumSerializer(read_only=True)
    # driver = UserNameSerializer(read_only=True)

    class Meta:
        model = m.VehicleViolation
        fields = '__all__'
