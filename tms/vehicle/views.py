from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c

# models
from . import models as m
from ..order.models import VehicleUserBind, Job

# serializer
from . import serializers as s
from ..core.serializers import ChoiceSerializer

# views
from ..core.views import TMSViewSet, ApproveViewSet
from ..g7.interfaces import G7Interface


class VehicleViewSet(TMSViewSet):
    """
    Viewset for Vehicle
    """
    queryset = m.Vehicle.objects.all()
    serializer_class = s.VehicleSerializer
    short_serializer_class = s.ShortVehicleSerializer

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

    @action(detail=False, url_path='vehicles')
    def list_short_vehicles(self, request):
        page = self.paginate_queryset(self.queryset)
        serializer = s.ShortVehicleSerializer(page, many=True)
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

    @action(detail=True, methods=['get'], url_path='playback')
    def vehicle_history_track_query(self, request, pk=None):
        """
        Retrive the vehicle history track from G7 and return the response
        Not used for now
        """
        vehicle = self.get_object()
        from_datetime = self.request.query_params.get('from', None)
        to_datetime = self.request.query_params.get('to', None)

        if from_datetime is None or to_datetime is None:
            results = []
        else:
            queries = {
                'plate_num': vehicle.plate_num,
                'from': from_datetime,
                'to': to_datetime,
                'timeInterval': 10
            }

            data = G7Interface.call_g7_http_interface(
                'VEHICLE_HISTORY_TRACK_QUERY',
                queries=queries
            )

            if data is None:
                results = []
            else:
                paths = []

                index = 0
                for x in data:
                    paths.append([x.pop('lng'), x.pop('lat')])
                    x['no'] = index
                    x['time'] = datetime.utcfromtimestamp(
                        int(x['time'])/1000
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    index = index + 1

                results = {
                    'paths': paths,
                    'meta': data
                }

        return Response(
            results,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='status')
    def get_all_vehicles_status(self, request):
        ret = []

        for vehicle in m.Vehicle.objects.all():
            if vehicle.status == c.VEHICLE_STATUS_AVAILABLE:
                status = 'No Job'
                try:
                    bind = VehicleUserBind.objects.get(vehicle=vehicle)
                    driver = bind.driver.name
                except VehicleUserBind.DoesNotExist:
                    driver = 'No driver'
            elif vehicle.status == c.VEHICLE_STATUS_INWORK:
                driver = vehicle.bind.driver.name
                job = Job.objects.filter(vehicle=vehicle, progress__gt=1)

                if job.progress == 2:
                    status = '赶往装货地'
                elif job.progress == 3:
                    status = '等待装货'
                elif job.progress == 4:
                    status = '装货中'
                elif job.progress == 5:
                    status = '装货完成'
                elif job.progress == 6:
                    status = '赶往质检'
                elif job.progress == 7:
                    status = '等待质检'
                elif job.progress == 8:
                    status = '质检中'
                elif job.progress == 9:
                    status = '质检完成'
                elif (job.progress - 10) % 4 == 0:
                    status = '赶往卸货'
                elif (job.progress - 10) % 4 == 1:
                    status = '等待卸货'
                elif (job.progress - 10) % 4 == 2:
                    status = '卸货中'
                elif (job.progress - 10) % 4 == 3:
                    status = '卸货完成'

            elif vehicle.status == c.VEHICLE_STATUS_REPAIR:
                driver = 'No driver'
                status = 'Repairing'

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
        try:
            bind = VehicleUserBind.objects.get(vehicle=vehicle)
            driver = bind.driver.name
            escort = bind.escort.name
        except VehicleUserBind.DoesNotExist:
            driver = '未知'
            escort = '未知'

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
            'gpsno': data.get('gpsno', ''),
            'location': data['loc']['address'].split(' ')[0],
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
        vehicle_check, created = m.VehicleCheckHistory.objects.get_or_create(
            vehicle=vehicle, driver=request.user, before_driving_checked_time__gt=bind.get_on
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
        data = request.data
        data['vehicle'] = pk
        data['driver'] = request.user.id
        serializer = s.VehicleDriverDailyBindSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='daily-unbind')
    def vehicle_driver_daily_unbind(self, request, pk=None):
        vehicle = self.get_object()
        bind = m.VehicleDriverDailyBind.objects.filter(vehicle=vehicle, driver=request.user).first()
        if bind.get_off is not None:
            return Response({
                'msg': 'You alread get off this vehicle'
            })
        vehicle_check = m.VehicleCheckHistory.objects.filter(
            vehicle=vehicle, driver=request.user, before_driving_checked_time__gt=bind.get_on
        ).first()

        if vehicle_check is None or vehicle_check.before_driving_checked_time is None or\
           vehicle_check.driving_checked_time is None or vehicle_check.after_driving_checked_time is None:
            return Response(
                {'msg': '你没有完成车辆三检查'}, status=status.HTTP_400_BAD_REQUEST
            )
        bind.get_off = timezone.now()
        bind.save()

        return Response(s.VehicleDriverDailyBindSerializer(bind).data, status=status.HTTP_200_OK)


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


class VehicleMaintenanceRequestViewSet(ApproveViewSet):

    queryset = m.VehicleMaintenanceRequest.objects.all()
    serializer_class = s.VehicleMaintenanceRequestSerializer

    def create(self, request):
        data = request.data
        data['requester'] = request.user.profile.id
        serializer = self.serializer_class(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, url_path="categories")
    def get_vehicle_models(self, request):
        serializer = ChoiceSerializer(
            [{'value': x, 'text': y} for (x, y) in c.VEHICLE_MAINTENANCE],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FuelConsumptionViewSet(TMSViewSet):

    queryset = m.FuelConsumption.objects.all()
    serializer_class = s.FuelConsumptionSerializer


class TireViewSet(TMSViewSet):

    queryset = m.Tire.objects.all()
    serializer_class = s.TireSerializer


class VehicleCheckHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

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

        serializer = s.VehicleCheckHistorySerializer(
            page, many=True,
            context=context
        )

        return self.get_paginated_response(serializer.data)
