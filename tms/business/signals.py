import json
from django.dispatch import receiver
from django.db.models.signals import post_save
from fieldsignals import pre_save_changed
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# constants
from ..core import constants as c

# models
from . import models as m
from ..account.models import User

# serializers


channel_layer = get_channel_layer()


@receiver(post_save, sender=m.VehicleRepairRequest)
def notify_vehicle_request(sender, instance, created, **kwargs):
    if created:
        message_type = c.NOTIFICATION_VEHICLE_REPAIR_REQUEST
        message = '{} request a {} repair rest'.format(
            instance.request.requester.name,
            instance.vehicle.plate_num,
        )

        for approver in instance.request.approvers.all():
            if approver.channel_name:
                async_to_sync(channel_layer.send)(
                    approver.channel_name,
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': message_type,
                            'message': message
                        })
                    }
                )


@receiver(post_save, sender=m.RestRequest)
def notify_rest_request(sender, instance, created, **kwargs):
    if created:
        print(created)
        message_type = c.NOTIFICATION_REST_REQUEST
        message = '{} request a rest from {} to {}'.format(
            instance.request.requester.name,
            instance.from_date.strftime('%Y-%m-%d'),
            instance.to_date.strftime('%Y-%m-%d'),
        )
        print(message)

        for approver in instance.request.approvers.all():
            if approver.channel_name:
                print(approver.channel_name)
                async_to_sync(channel_layer.send)(
                    approver.channel_name,
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': message_type,
                            'message': message
                        })
                    }
                )


# @receiver(post_save, sender=m.ParkingRequest)
# def notify_parking_request(sender, instance, created, **kwargs):
#     """
#     Parking request can be made from driver app, and web manager
#     When parking request is created, staff member will be notified
#     """
#     if created:
#         message = "{} created {} parking request."\
#             "Please approve it".format(instance.driver, instance.vehicle)

#         admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
#         if admin.channel_name:
#             async_to_sync(channel_layer.send)(
#                 admin.channel_name,
#                 {
#                     'type': 'notify',
#                     'data': json.dumps({
#                         'msg_type': c.NOTIFICATION_PARKING_REQUEST,
#                         'message': message
#                     })
#                 }
#             )


# @receiver(
#     pre_save_changed, sender=m.ParkingRequest,
#     fields=['approved']
# )
# def notify_parking_request_result(sender, instance,
#                                   changed_fields=None, **kwargs):
#     """
#     Driver(requester) will be notified
#     when parking request is approved or declined
#     """
#     for field, (old, new) in changed_fields.items():
#         if field.name == 'approved' and instance.driver.channel_name:
#             if new:
#                 msg_type = c.NOTIFICATION_PARKING_REQUEST_APPROVED
#                 message = "Your parking request at {} was "\
#                     "approved".format(instance.from_date, instance.to_date)

#             else:
#                 msg_type = c.NOTIFICATION_PARKING_REQUEST_DECLINED
#                 message = "Your rest request from {} to {} was "\
#                     "declined".format(instance.from_date, instance.to_date)

#             async_to_sync(channel_layer.send)(
#                 instance.user.channel_name,
#                 {
#                     'type': 'notify',
#                     'data': json.dumps({
#                         'msg_type': msg_type,
#                         'message': message
#                     })
#                 }
#             )


# @receiver(post_save, sender=m.DriverChangeRequest)
# def notify_driver_change_request(sender, instance, created, **kwargs):
#     """
#     Parking request can be made from driver app
#     When driver request is created, staff member will be notified
#     """
#     if created:
#         admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
#         if admin.channel_name:
#             message = "{} make an driver change request."\
#                 "Please check and approve.".format(instance.old_driver.name)

#             async_to_sync(channel_layer.send)(
#                 admin.channel_name,
#                 {
#                     'type': 'notify',
#                     'data': json.dumps({
#                         'msg_type': c.NOTIFICATION_DRIVER_CHANGE_REQUEST,
#                         'message': message
#                     })
#                 }
#             )


# @receiver(
#     pre_save_changed, sender=m.DriverChangeRequest,
#     fields=['approved']
# )
# def notify_driver_change_request_result(sender, instance,
#                                         changed_fields=None, **kwargs):
#     """
#     When the staff member approve, old driver(requester)
#         and new driver will be notified
#     When the staff member declines, old driver(requester)
#         will be notified of the result
#     """
#     for field, (old, new) in changed_fields.items():
#         if field.name == 'approved':
#             if instance.old_driver.channel_name:
#                 # old driver will be notified
#                 if new:
#                     msg_type = c.NOTIFICATION_DRIVER_CHANGE_REQUEST_APPROVED
#                     message = "Your rest request from {} to {} was "\
#                         "approved".format(instance.from_date, instance.to_date)

#                 else:
#                     msg_type = c.NOTIFICATION_DRIVER_CHANGE_REQUEST_DECLINED
#                     message = "Your rest request from {} to {} was "\
#                         "declined".format(instance.from_date, instance.to_date)

#                 async_to_sync(channel_layer.send)(
#                     instance.user.channel_name,
#                     {
#                         'type': 'notify',
#                         'data': json.dumps({
#                             'msg_type': msg_type,
#                             'message': message
#                         })
#                     }
#                 )

#             if instance.new_driver.channel_name:
#                 if new:
#                     msg_type = c.NOTIFICATION_DRIVER_CHANGE_REQUEST_NEW_DRIVER
#                     message = "You are select as a new driver on this {}."\
#                         "Please change at {} on {}".format(
#                             instance.job.id,
#                             instance.change_place,
#                             instance.change_time
#                         )


# @receiver(post_save, sender=m.EscortChangeRequest)
# def notify_escort_change_request(sender, instance, created, **kwargs):
#     """
#     Escort change request can be made from driver app
#     staff member will be notified
#     """
#     if created:
#         admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
#         if admin.channel_name:
#             message = "{} make an driver change request."\
#                 "Please check and approve.".format(instance.old_escort.name)

#             async_to_sync(channel_layer.send)(
#                 admin.channel_name,
#                 {
#                     'type': 'notify',
#                     'data': json.dumps({
#                         'msg_type': c.NOTIFICATION_ESCORT_CHANGE_REQUEST,
#                         'message': message
#                     })
#                 }
#             )


# @receiver(
#     pre_save_changed, sender=m.EscortChangeRequest,
#     fields=['approved']
# )
# def notify_escort_change_request_result(sender, instance,
#                                         changed_fields=None, **kwargs):
#     """
#     When the staff member approve escort change, old escort(requester)
#         and new escort will be notified
#     When the staff member declines, old escort(requester)
#         will be notified of the result
#     """
#     for field, (old, new) in changed_fields.items():
#         if field.name == 'approved':
#             # old escort will be notified
#             if instance.old_escort.channel_name:
#                 if new:
#                     msg_type = c.NOTIFICATION_ESCORT_CHANGE_REQUEST_APPROVED
#                     message = "Your rest request from {} to {} was "\
#                         "approved".format(instance.from_date, instance.to_date)

#                 else:
#                     msg_type = c.NOTIFICATION_ESCORT_CHANGE_REQUEST_DECLINED
#                     message = "Your rest request from {} to {} was "\
#                         "declined".format(instance.from_date, instance.to_date)

#                 async_to_sync(channel_layer.send)(
#                     instance.user.channel_name,
#                     {
#                         'type': 'notify',
#                         'data': json.dumps({
#                             'msg_type': msg_type,
#                             'message': message
#                         })
#                     }
#                 )

#             # new escort will be notified
#             if instance.new_driver.channel_name:
#                 if new:
#                     msg_type = c.NOTIFICATION_ESCORT_CHANGE_REQUEST_NEW_ESCORT
#                     message = "You are select as a new escort on this {}."\
#                         "Please change at {} on {}".format(
#                             instance.job.id,
#                             instance.change_place,
#                             instance.change_time
#                         )


# @receiver(post_save, sender=m.RestRequest)
# def notify_rest_request(sender, instance, created, **kwargs):
#     """
#     rest request can be made from driver app and web
#     staff member will be notified
#     """
#     if created:
#         admin = User.objects.filter(role=c.USER_ROLE_ADMIN)[0]
#         if admin.channel_name:
#             message = "{} make an rest request."\
#                 "Please check and approve.".format(instance.user.name)

#             async_to_sync(channel_layer.send)(
#                 admin.channel_name,
#                 {
#                     'type': 'notify',
#                     'data': json.dumps({
#                         'msg_type': c.NOTIFICATION_REST_REQUEST,
#                         'message': message
#                     })
#                 }
#             )


# @receiver(
#     pre_save_changed, sender=m.RestRequest,
#     fields=['approved']
# )
# def notify_rest_request_result(sender, instance,
#                                changed_fields=None, **kwargs):
#     """
#     when staff member approve or decline, requester will be notified
#     """
#     for field, (old, new) in changed_fields.items():
#         if field.name == 'approved' and instance.user.channel_name:
#             if new:
#                 msg_type = c.NOTIFICATION_REST_REQUEST_APPROVED
#                 message = "Your rest request from {} to {} was "\
#                     "approved".format(instance.from_date, instance.to_date)

#             else:
#                 msg_type = c.NOTIFICATION_REST_REQUEST_DECLINED
#                 message = "Your rest request from {} to {} was "\
#                     "declined".format(instance.from_date, instance.to_date)

#             async_to_sync(channel_layer.send)(
#                 instance.user.channel_name,
#                 {
#                     'type': 'notify',
#                     'data': json.dumps({
#                         'msg_type': msg_type,
#                         'message': message
#                     })
#                 }
#             )
