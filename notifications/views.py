from django.http import JsonResponse
from rest_framework import status, generics, permissions
from rest_framework.request import Request

from notifications import api
import json


class NotificationView(
    generics.CreateAPIView, generics.RetrieveAPIView, generics.UpdateAPIView
):
    http_method_names = ["get", "patch", "post"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):
        """
        Get Notification list via requesting user
        No argument need
        """
        receiver = request.user
        if receiver is None:
            return JsonResponse(
                data={"msg": "no recevier"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return JsonResponse(
                json.dumps(api.get_notification_list(receiver)), safe=False
            )

    def patch(self, request: Request, *args, **kwargs):
        """
        Read Notification list via sources,
        if it's DM, {dm = "id_of_sender"}
        if it's channel msg, {channel = "id_of_channel"}
        only one sources are allowed
        """
        receiver = request.user
        channel = request.data.get("channel", None)
        dm = request.data.get("dm", None)

        if channel == None and dm == None:
            return JsonResponse(
                data={"msg": "no sources (channel and DM sender)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if channel != None and dm != None:
            return JsonResponse(
                data={"msg": "duplicated sources"}, status=status.HTTP_400_BAD_REQUEST
            )

        api.read_notification_list(request.user, sender=dm, channel=channel)

        return JsonResponse(json.dumps(api.get_notification_list(receiver)), safe=False)

    def post(self, request: Request, *args, **kwargs):
        """
        Debug use only,
        create notification directly.
        if it's DM, {dm = "id_of_sender"}
        if it's channel msg, {channel = "id_of_channel"}
        only one sources are allowed
        """

        sender = request.user
        channel = request.data.get("channel", None)
        receiver = request.data.get("receiver", None)

        if channel == None and receiver == None:
            return JsonResponse(
                data={"msg": "no sources (channel and DM sender)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if receiver != None and receiver != None:
            return JsonResponse(
                data={"msg": "duplicate sources"}, status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            json.dumps(api.notify(sender, channel=channel, receiver=receiver)),
            safe=False,
        )