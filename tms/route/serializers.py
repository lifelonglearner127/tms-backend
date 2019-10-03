from django.shortcuts import get_object_or_404
from rest_framework import serializers

# models
from . import models as m
from ..info.models import Station

# serializers
from ..info.serializers import ShortStationSerializer
from ..vehicle.serializers import ShortVehiclePlateNumSerializer


class ShortRouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Route
        fields = (
            'id', 'name'
        )


class RouteSerializer(serializers.ModelSerializer):

    start_point = ShortStationSerializer(read_only=True)
    end_point = ShortStationSerializer(read_only=True)
    vehicle = ShortVehiclePlateNumSerializer(read_only=True)
    start_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    finish_time = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Route
        fields = '__all__'

    def create(self, validated_data):
        start_point_data = self.context.get('start_point', None)
        if start_point_data is None:
            raise serializers.ValidationError({
                'start_point': 'Mising data'
            })
        start_point = get_object_or_404(m.Station, id=start_point_data.get('id', None))

        end_point_data = self.context.get('end_point', None)
        if end_point_data is None:
            raise serializers.ValidationError({
                'start_point': 'Mising data'
            })
        end_point = get_object_or_404(m.Station, id=end_point_data.get('id', None))

        if m.Route.objects.filter(start_point=start_point, end_point=end_point).exists():
            raise serializers.ValidationError({
                'route': '这条路书已经在'
            })

        if validated_data['is_g7_route']:
            vehicle_data = self.context.get('vehicle', None)
            if vehicle_data is None:
                raise serializers.ValidationError({
                    'vehicle': 'Missing data'
                })
            vehicle = get_object_or_404(m.Vehicle, id=vehicle_data.get('id', None))
        else:
            vehicle = None

        return m.Route.objects.create(
            start_point=start_point,
            end_point=end_point,
            vehicle=vehicle,
            **validated_data
        )

    def update(self, instance, validated_data):
        start_point_data = self.context.get('start_point', None)
        if start_point_data is None:
            raise serializers.ValidationError({
                'start_point': 'Mising data'
            })
        start_point = get_object_or_404(m.Station, id=start_point_data.get('id', None))

        end_point_data = self.context.get('end_point', None)
        if end_point_data is None:
            raise serializers.ValidationError({
                'start_point': 'Mising data'
            })
        end_point = get_object_or_404(m.Station, id=end_point_data.get('id', None))

        if m.Route.objects.exclude(id=instance.id).filter(start_point=start_point, end_point=end_point).exists():
            raise serializers.ValidationError({
                'route': '这条路书已经在'
            })

        instance.start_point = start_point
        instance.end_point = end_point
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if validated_data['is_g7_route']:
            vehicle_data = self.context.get('vehicle', None)
            if vehicle_data is None:
                raise serializers.ValidationError({
                    'vehicle': 'Missing data'
                })
            instance.vehicle = get_object_or_404(m.Vehicle, id=vehicle_data.get('id', None))

        else:
            instance.vehicle = None
            instance.start_time = None
            instance.finish_time = None

        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not instance.is_g7_route:
            path = Station.objects.filter(id__in=instance.map_path)
            path = dict([(point.id, point) for point in path])

            ret['map_path'] = ShortStationSerializer(
                [path[id] for id in instance.map_path],
                many=True
            ).data

        return ret
