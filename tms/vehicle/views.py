from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c

# models
from . import models as m
from ..order.models import Job
from ..finance.models import ETCCard, FuelCard

# serializer
from . import serializers as s
from ..core.serializers import ChoiceSerializer
from ..finance.serializers import ETCCardBalanceSerializer, FuelCardBalanceSerializer

# views
from ..core.views import TMSViewSet
from ..g7.interfaces import G7Interface
from ..core import utils


class VehicleViewSet(TMSViewSet):
    """
    Viewset for Vehicle
    """
    queryset = m.Vehicle.objects.all()
    serializer_class = s.VehicleSerializer
    short_serializer_class = s.ShortVehiclePlateNumSerializer

    def create(self, request):
        branches = request.data.get('branches', None)
        if branches is None:
            load = request.data.get('load', 0)
            data = request.data.copy()
            data.setdefault('branches', [load])
            serializer = self.serializer_class(data=data)
        else:
            serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    # version 2
    @action(detail=False, url_path='binds')
    def get_vehicle_bind_details(self, request):
        """
        This api endpoint will be used for getting vehicle and binded drivers and escorts
        When the user click the vehicle input box on arrange edit view on the front end
        """
        vehicle = request.query_params.get('vehicle', '')
        queryset = self.queryset
        if vehicle:
            queryset = queryset.filter(plate_num__contains=vehicle)

        page = self.paginate_queryset(queryset)

        serializer = s.VehicleBindDetailSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='vehicles')
    def list_short_vehicles(self, request):
        page = self.paginate_queryset(m.Vehicle.availables.all())
        serializer = s.ShortVehicleStatusSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='branches')
    def get_vehicle_branches(self, request, pk=None):
        vehicle = self.get_object()

        return Response(
            {
                'branches': vehicle.branches
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='playback')
    def get_vehicle_playback_by_job(self, request, pk=None):
        vehicle = self.get_object()

        start_time = self.request.query_params.get('start_time', None)
        finish_time = self.request.query_params.get('finish_time', None)

        results = {
            'total_distance': 0,
            'paths': [],
            'meta': []
        }
        while True:
            queries = {
                'plate_num': vehicle.plate_num,
                'from': start_time,
                'to': finish_time,
                'timeInterval': '30'
            }
            try:
                data = G7Interface.call_g7_http_interface(
                    'VEHICLE_HISTORY_TRACK_QUERY',
                    queries=queries
                )
                for x in data:
                    results['paths'].append([x.pop('lng'), x.pop('lat')])
                    results['total_distance'] += round(x['distance'] / 100)
                    x['time'] = datetime.fromtimestamp(x['time']/1000).strftime('%Y-%m-%d %H:%M:%S')

                results['meta'].extend(data)

                if len(data) == 1000:
                    start_time = datetime.strptime(
                        data[999]['time'], '%Y-%m-%d %H:%M:%S'
                    )
                    start_time = start_time + timedelta(seconds=1)
                    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

                else:
                    break
            except Exception:
                results = {
                    'result': {
                        'code': '1',
                        'msg': 'g7 error'
                    }
                }
                break

        if 'total_distance' in results:
            results['total_distance'] = round(
                results['total_distance'] / 1000, 2
            )

        return Response(
            results,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='g7-points')
    def get_vehicle_g7_points(self, request, pk=None):
        """
        Retrive the vehicle history track from G7 and return the response
        """
        vehicle = self.get_object()
        start_time = self.request.query_params.get('start_time', None)
        finish_time = self.request.query_params.get('finish_time', None)

        result = {
            'distance': 0,
            'path': []
        }
        while True:
            queries = {
                'plate_num': vehicle.plate_num,
                'from': start_time,
                'to': finish_time,
                'timeInterval': '30'
            }
            try:
                data = G7Interface.call_g7_http_interface(
                    'VEHICLE_HISTORY_TRACK_QUERY',
                    queries=queries
                )
                for x in data:
                    result['path'].append([x.pop('lng'), x.pop('lat')])
                    result['distance'] += round(x['distance'] / 100)

                if len(data) == 1000:
                    start_time = datetime.fromtimestamp(
                        int(data[999]['time'])/1000
                    )
                    start_time = start_time + timedelta(seconds=1)
                    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

                else:
                    break
            except Exception:
                result = {
                    'code': '1',
                    'msg': 'g7 error'
                }
                break

        if 'distance' in result:
            result['distance'] /= 1000

        return Response(
            result,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='status')
    def get_all_vehicles_status(self, request):
        ret = []

        for vehicle in m.Vehicle.objects.order_by('plate_num'):
            bind = m.VehicleDriverDailyBind.objects.filter(
                vehicle=vehicle
            ).first()
            if bind is not None and bind.get_off is None:
                driver = bind.driver.name
            else:
                driver = '无司机'
            if vehicle.status == c.VEHICLE_STATUS_UNDER_WHEEL:
                job = Job.objects.filter(vehicle=vehicle, progress__gt=1).first()
                if job is not None:
                    if job.progress >= 10:
                        if (job.progress - 10) % 4 == 0:
                            progress = 10
                        elif (job.progress - 10) % 4 == 1:
                            progress = 11
                        elif (job.progress - 10) % 4 == 2:
                            progress = 12
                        elif (job.progress - 10) % 4 == 3:
                            progress = 13
                    else:
                        progress = job.progress

                    status = c.JOB_PROGRESS.get(progress)
                else:
                    status = '无任务'

            elif vehicle.status == c.VEHICLE_STATUS_REPAIR:
                status = '修车'
            else:
                status = '无任务'

            ret.append({
                'plate_num': vehicle.plate_num,
                'driver': driver,
                'status': status
            })

        return Response(
            s.VehicleStatusSerializer(ret, many=True).data
        )

    @action(detail=False, url_path='position')
    def get_all_vehicle_positions(self, request):
        """
        Get the current location of all registered vehicles
        This api will be called when dashboard component is mounted
        After dashboard component mounted, vehicle positions will be notified
        vai web sockets, so this api is called only once.
        """
        plate_nums = m.Vehicle.objects.values_list('plate_num', flat=True)
        body = {
            'plate_nums': list(plate_nums),
            'fields': ['loc']
        }
        data = G7Interface.call_g7_http_interface(
            'BULK_VEHICLE_STATUS_INQUIRY',
            body=body
        )
        ret = []
        for key, value in data.items():
            if value['code'] == 0:
                ret.append(value)

        serializer = s.VehiclePositionSerializer(
            ret, many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='current-position')
    def get_vehicle_position(self, request):
        """
        Get the current location of vehicle; for mobile
        This api will be called when the driver want to see the job route
        """
        plate_num = self.request.query_params.get('plate_num', None)
        queries = {
            'plate_num': plate_num,
            'fields': 'loc',
            'addr_required': True,
        }

        data = G7Interface.call_g7_http_interface(
            'VEHICLE_STATUS_INQUIRY',
            queries=queries
        )

        if data is None:
            raise s.serializers.ValidationError({
                'vehicle': 'Error occured while getting position'
            })

        ret = {
            'plate_num': plate_num,
            'lnglat': [float(data['loc']['lng']), float(data['loc']['lat'])],
            'speed': float(data['loc']['speed'])
        }
        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="current-info")
    def current_info(self, request):
        """
        get the vehicle status of selected vehicle
        this api will be called when admin hit on the truck icon on dashbaord
        """
        plate_num = self.request.query_params.get('plate_num', None)
        vehicle = get_object_or_404(m.Vehicle, plate_num=plate_num)

        # Get the current driver and escorts of this vehicle

        bind = m.VehicleDriverDailyBind.objects.filter(vehicle=vehicle).first()
        if bind is not None and bind.get_off is None:
            driver = bind.driver.name
            driver_mobile = bind.driver.mobile
            escort = '未知'
            escort_mobile = '未知'
        else:
            driver = '未知'
            escort = '未知'
            driver_mobile = '未知'
            escort_mobile = '未知'

        queries = {
            'plate_num': plate_num,
            'fields': 'loc',
            'addr_required': True,
        }

        data = G7Interface.call_g7_http_interface(
            'VEHICLE_STATUS_INQUIRY',
            queries=queries
        )
        ret = {
            'plate_num': plate_num,
            'driver': driver,
            'escort': escort,
            'driver_mobile': driver_mobile,
            'escort_mobile': escort_mobile,
            'gpsno': data.get('gpsno', ''),
            'last_gps_time': data.get('time', ''),
            'location': data['loc']['address'],
            'speed': data['loc']['speed']
        }
        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="brands")
    def get_vehicle_brands(self, request):
        """
        Get the vehicle brands
        """
        serializer = ChoiceSerializer(
            [{'value': x, 'text': y} for (x, y) in c.VEHICLE_BRAND],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="models")
    def get_vehicle_models(self, request):
        """
        Get the vehicle models
        """
        serializer = ChoiceSerializer(
            [{'value': x, 'text': y} for (x, y) in c.VEHICLE_MODEL_TYPE],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="in-works")
    def get_in_work_vehicles(self, request):
        """
        get in-work vehicles
        """
        page = self.paginate_queryset(
            m.Vehicle.inworks.all()
        )
        serializer = s.ShortVehicleSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="availables")
    def get_available_vehicles(self, request):
        """
        get availables vehicles
        """
        page = self.paginate_queryset(
            m.Vehicle.availables.all()
        )
        serializer = s.ShortVehicleSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='last-vehicle-check')
    def get_last_vehicle_check(self, request, pk=None):
        vehicle = self.get_object()
        vehicle_check = m.VehicleCheckHistory.objects.filter(
            vehicle=vehicle, driver=request.user
        ).first()

        if vehicle_check is not None:
            ret = s.VehicleCheckHistorySerializer(
                vehicle_check, context={'request': request}
            ).data
        else:
            ret = []

        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='vehicle-check')
    def vehicle_check(self, request, pk=None):
        vehicle = self.get_object()
        bind = m.VehicleDriverDailyBind.objects.filter(vehicle=vehicle, driver=request.user).first()
        if bind is None or bind.get_off is not None:
            return Response(
                {
                    'msg': 'You need to get on this vehicle'
                },
                status=status.HTTP_200_OK
            )

        vehicle_check = m.VehicleCheckHistory.objects.filter(
            Q(before_driving_checked_time__gt=bind.get_on) |
            Q(driving_checked_time__gt=bind.get_on) |
            Q(after_driving_checked_time__gt=bind.get_on),
            vehicle=vehicle,
            driver=request.user,
        ).first()

        if vehicle_check is None:
            vehicle_check = m.VehicleCheckHistory.objects.create(
                vehicle=vehicle,
                driver=request.user
            )

        items = request.data.pop('items')
        images = request.data.pop('images', [])
        check_type = request.data.pop('check_type')
        data = request.data
        data['vehicle'] = pk
        data['driver'] = request.user.id
        if check_type == c.VEHICLE_CHECK_TYPE_BEFORE_DRIVING:
            data['before_driving_checked_time'] = timezone.now()
            data['before_driving_problems'] = data.pop('problems')
            data['before_driving_description'] = data.pop('description')
        elif check_type == c.VEHICLE_CHECK_TYPE_DRIVING:
            data['driving_checked_time'] = timezone.now()
            data['driving_problems'] = data.pop('problems')
            data['driving_description'] = data.pop('description')
        elif check_type == c.VEHICLE_CHECK_TYPE_AFTER_DRIVING:
            data['after_driving_checked_time'] = timezone.now()
            data['after_driving_problems'] = data.pop('problems')
            data['after_driving_description'] = data.pop('description')

        serializer = s.VehicleCheckHistorySerializer(
            vehicle_check,
            data=data,
            context={
                'items': items, 'images': images, 'request': request, 'check_type': check_type
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='daily-bind')
    def vehicle_driver_daily_bind(self, request, pk=None):
        vehicle = self.get_object()
        driver = request.user

        # check if vehicle is available
        if vehicle.status != c.VEHICLE_STATUS_AVAILABLE:
            return Response(
                {
                    'msg': 'Cannot get on this vehicle because this vehicle is unavailable'
                }
            )

        # check if somebody is get on this vehicle
        bind = m.VehicleDriverDailyBind.objects.filter(vehicle=vehicle).first()
        if bind is not None and bind.get_off is None:
            return Response({
                'msg': 'Somebody already get on this vehicle'
            })

        # check if driver is available
        if driver.profile.status != c.WORK_STATUS_AVAILABLE:
            return Response({
                'msg': 'Cannot get on this vehicle because you are not available'
            })

        bind = m.VehicleDriverDailyBind.objects.create(
            vehicle=vehicle,
            driver=request.user
        )

        vehicle.status = c.VEHICLE_STATUS_UNDER_WHEEL
        vehicle.save()

        driver.profile.status = c.WORK_STATUS_DRIVING
        driver.profile.save()

        return Response(
            s.VehicleDriverDailyBindSerializer(bind).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='daily-unbind')
    def vehicle_driver_daily_unbind(self, request, pk=None):
        """
        this api is called in driver app when driver get off the vehicle
        """
        vehicle = self.get_object()
        driver = request.user
        station_data = request.data.pop('station', None)
        if station_data is None:
            return Response(
                {
                    'msg': 'missing station data'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        bind = m.VehicleDriverDailyBind.objects.filter(vehicle=vehicle, driver=driver).first()
        if bind is None:
            return Response({
                'msg': "You didn't get on this vehicle before"
            })

        if bind.get_off is not None:
            return Response({
                'msg': 'You already get off this vehicle'
            })

        # check if the vehicle check is all done
        vehicle_check = m.VehicleCheckHistory.objects.filter(
            vehicle=vehicle, driver=driver, before_driving_checked_time__gt=bind.get_on
        ).first()

        if vehicle_check is None:
            return Response(
                {
                    'msg': '你没有完成车辆三检查'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if driver complete before driving check
        before_driving_check_item_count = m.VehicleCheckItem.published_before_driving_check_items.count()
        checked_item_count = vehicle_check.vehiclebeforedrivingitemcheck_set.filter(is_checked=True).count()
        if vehicle_check.before_driving_checked_time is None or\
           checked_item_count != before_driving_check_item_count:
            return Response(
                {
                    'msg': "you didn't complete before driving check "
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if driver complete driving check
        driving_check_item_count = m.VehicleCheckItem.published_driving_check_items.count()
        checked_item_count = vehicle_check.vehicledrivingitemcheck_set.filter(is_checked=True).count()
        if vehicle_check.driving_checked_time is None or\
           checked_item_count != driving_check_item_count:
            return Response(
                {
                    'msg': "you didn't complete driving check "
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if driver complete after driving check
        after_driving_check_item_count = m.VehicleCheckItem.published_after_driving_check_items.count()
        checked_item_count = vehicle_check.vehicleafterdrivingitemcheck_set.filter(is_checked=True).count()
        if vehicle_check.after_driving_checked_time is None or\
           checked_item_count != after_driving_check_item_count:
            return Response(
                {
                    'msg': "you didn't complete after driving check "
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        station_id = station_data.get('id', None)
        if station_id is not None:
            station = get_object_or_404(m.Station, id=station_id)
        else:
            station = m.Station.objects.create(
                name=station_data.get('name', ''),
                station_type=c.STATION_TYPE_GET_OFF_STATION
            )

        bind.get_off_station = station
        bind.get_off = timezone.now()
        bind.save()
        vehicle.status = c.VEHICLE_STATUS_AVAILABLE
        vehicle.save()
        driver.profile.status = c.WORK_STATUS_AVAILABLE
        driver.profile.save()

        return Response(s.VehicleDriverDailyBindSerializer(bind).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path="etccard")
    def get_equipped_etccard(self, request, pk=None):
        vehicle = self.get_object()
        try:
            card = ETCCard.objects.get(vehicle=vehicle)
            return Response(
                ETCCardBalanceSerializer(card).data,
                status=status.HTTP_200_OK
            )
        except ETCCard.DoesNotExist:
            return Response(
                {'msg': 'This vehicle does not have etc card'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['get'], url_path="fuelcard")
    def get_equipped_fuelcard(self, request, pk=None):
        vehicle = self.get_object()
        try:
            card = FuelCard.objects.get(vehicle=vehicle)
            return Response(
                FuelCardBalanceSerializer(card).data,
                status=status.HTTP_200_OK
            )
        except FuelCard.DoesNotExist:
            return Response(
                {'msg': 'This vehicle does not have fuel card'},
                status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['get'], url_path="unbinded-vehicles")
    def get_unbinded_vehicles(self, request):
        vehicle_ids = m.VehicleDriverEscortBind.objects.values_list('vehicle')
        vehicles = m.Vehicle.objects.exclude(id__in=vehicle_ids)
        return Response(
            s.ShortVehiclePlateNumSerializer(vehicles, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path="unbinded-driversandescorts")
    def get_unbinded_drivers_and_escorts(self, request):
        user_ids = []
        user_escort_ids = m.VehicleDriverEscortBind.objects.values_list('driver', 'escort')
        for user_id, escort_id in user_escort_ids:
            user_ids.extend([user_id, escort_id])

        users = m.User.wheels.exclude(id__in=user_ids)
        return Response(
            s.MainUserSerializer(users, many=True).data,
            status=status.HTTP_200_OK
        )


class VehicleCheckItemViewSet(TMSViewSet):

    queryset = m.VehicleCheckItem.objects.all()
    serializer_class = s.VehicleCheckItemSerializer

    @action(detail=False, url_path='get-before-items')
    def get_before_driving_items(self, request):
        serializer = s.VehicleCheckItemNameSerializer(
            m.VehicleCheckItem.objects.filter(is_before_driving_item=True, is_published=True),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='get-driving-items')
    def get_driving_items(self, request):
        serializer = s.VehicleCheckItemNameSerializer(
            m.VehicleCheckItem.objects.filter(is_driving_item=True, is_published=True),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='get-after-items')
    def get_after_driving_items(self, request):
        serializer = s.VehicleCheckItemNameSerializer(
            m.VehicleCheckItem.objects.filter(is_after_driving_item=True, is_published=True),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FuelConsumptionViewSet(TMSViewSet):

    queryset = m.FuelConsumption.objects.all()
    serializer_class = s.FuelConsumptionSerializer


class VehicleCheckHistoryViewSet(viewsets.ModelViewSet):

    queryset = m.VehicleCheckHistory.objects.all()
    serializer_class = s.VehicleCheckHistorySerializer

    def list(self, request):
        page = self.paginate_queryset(self.queryset)
        return self.get_paginated_response(
            s.ShortVehicleCheckHistorySerializer(
                page,
                many=True
            ).data
        )

    @action(detail=False, url_path="me")
    def get_my_check_history(self, request):
        page = self.paginate_queryset(
            request.user.my_vehicle_checks.all()
        )
        context = {}
        bind = m.VehicleDriverDailyBind.objects.filter(driver=request.user).first()
        if bind is not None and bind.get_off is None:
            context = {
                'bind': True,
                'get_on_time': bind.get_on
            }
        elif bind is not None and bind.get_off is not None:
            context = {
                'bind': False
            }

        context['request'] = request
        serializer = s.VehicleCheckHistorySerializer(
            page, many=True,
            context=context
        )

        return self.get_paginated_response(serializer.data)


class VehicleMaintenanceHistoryViewSet(TMSViewSet):

    queryset = m.VehicleMaintenanceHistory.objects.all()
    serializer_class = s.VehicleMaintenanceHistorySerializer

    def create(self, request):
        context = {
            'vehicle': request.data.pop('vehicle'),
            'assignee': request.data.pop('assignee'),
            'station': request.data.pop('station'),
        }
        serializer = s.VehicleMaintenanceHistorySerializer(
            data=request.data,
            context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'vehicle': request.data.pop('vehicle'),
            'assignee': request.data.pop('assignee'),
            'station': request.data.pop('station'),
        }
        serializer = s.VehicleMaintenanceHistorySerializer(
            instance,
            data=request.data,
            context=context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class VehicleTireViewSet(viewsets.ModelViewSet):

    serializer_class = s.VehicleTireSerializer
    queryset = m.VehicleTire.objects.all()

    def create(self, request):
        vehicle_data = request.data.pop('vehicle', None)
        vehicle = get_object_or_404(m.Vehicle, id=vehicle_data.get('id', None))
        position = request.data.pop('position', 0)
        if m.VehicleTire.objects.filter(vehicle=vehicle, position=position).exists():
            raise s.serializers.ValidationError({
                'vehicle': 'Already exists'
            })

        vehicle_tire = m.VehicleTire.objects.create(
            vehicle=vehicle,
            position=position
        )
        data = request.data.pop('current_tire')
        data['vehicle_tire'] = vehicle_tire.id
        serializer = s.TireManagementHistorySerializer(
            data=data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            self.serializer_class(vehicle_tire).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        vehicle_data = request.data.pop('vehicle', None)
        vehicle = get_object_or_404(m.Vehicle, id=vehicle_data.get('id', None))
        position = request.data.pop('position', 0)
        if m.VehicleTire.objects.exclude(id=pk).filter(vehicle=vehicle, position=position).exists():
            raise s.serializers.ValidationError({
                'vehicle': 'Already exists'
            })

        instance.position = position
        instance.vehicle = vehicle
        instance.save()

        data = request.data.pop('current_tire')
        data['vehicle_tire'] = instance.id
        current_tire = instance.history.first()
        if current_tire is not None:
            serializer = s.TireManagementHistorySerializer(
                current_tire,
                data=data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='change')
    def change_tire(self, request, pk=None):
        vehicle_tire = self.get_object()
        data = request.data
        data['vehicle_tire'] = pk

        if vehicle_tire.current_tire is not None and vehicle_tire.current_tire.installed_on is not None:
            vehicle_tire.current_tire.mileage = utils.get_mileage(
                vehicle_tire.vehicle.plate_num,
                vehicle_tire.current_tire.installed_on,
                timezone.now()
            )
            vehicle_tire.current_tire.save()

        serializer = s.TireManagementHistorySerializer(
            data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='tread-depth')
    def get_current_tread_check(self, request, pk=None):
        """
        this api is called in web admin to check the current tread depth
        """
        vehicle_tire = self.get_object()
        if vehicle_tire.current_tire is None:
            return Response(
                {
                    'msg': 'no tire installed yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if vehicle_tire.current_tire.current_tread_depth is None:
            tread_depth = vehicle_tire.current_tire.tread_depth
        else:
            tread_depth = vehicle_tire.current_tire.current_tread_depth.tread_depth

        return Response(
            {
                'tread_depth': tread_depth
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='tread-check')
    def tread_check(self, request, pk=None):
        """
        this api is called in web manager when user check the tread
        """
        vehice_tire = self.get_object()
        if vehice_tire.current_tire is None:
            return Response(
                {
                    'msg': 'not tire yet'
                },
                status=status.HTTP_200_OK
            )

        m.TireTreadDepthCheckHistory.objects.create(
            tire=vehice_tire.current_tire,
            tread_depth=request.data.pop('tread_depth', 0)
        )

        return Response(
            {
                'msg': 'success'
            },
            status=status.HTTP_200_OK
        )


class TireManagementHistoryViewSet(viewsets.ModelViewSet):

    queryset = m.TireManagementHistory.objects.all()
    serializer_class = s.TireManagementHistoryDataViewSerializer


class TireTreadDepthCheckHistoryViewSet(viewsets.ModelViewSet):

    queryset = m.TireTreadDepthCheckHistory.objects.all()
    serializer_class = s.TireTreadDepthCheckHistorySerializer


class VehicleDriverEscortBindViewSet(TMSViewSet):

    serializer_class = s.VehicleDriverEscortBindSerializer

    def get_queryset(self):
        return m.VehicleDriverEscortBind.objects.all()


class VehicleViolationViewSet(TMSViewSet):

    queryset = m.VehicleViolation.objects.all()
    serializer_class = s.VehicleViolationSerializer


class VehicleViolationUploadView(APIView):

    parser_classes = [MultiPartParser, ]

    def post(self, request):
        for _, data_file in request.data.items():
            if not data_file.name.endswith('.csv'):
                return Response({
                    'msg': 'File is not csv type'
                })
            data = data_file.read().decode('utf-8')
            lines = data.split('\n')

            for line in lines:
                fields = line.split(',')
                if len(fields) != 8:
                    continue

                data_dict = {}
                data_dict['violates_on'] = fields[0]
                data_dict['vehicle'] = fields[1]
                data_dict['driver'] = fields[2]
                data_dict['address'] = fields[3]
                data_dict['fine'] = fields[4]
                data_dict['deduction_score'] = fields[5]
                data_dict['description'] = fields[6]
                data_dict['status'] = fields[7]
                m.VehicleViolation.objects.create(**data_dict)

        return Response({
            'msg': 'Successfully uploaded'
        }, status=status.HTTP_200_OK)
