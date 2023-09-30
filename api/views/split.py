from django.db import models
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.mixins import MultiSerializerViewSetMixin
from api.serializer import SplitAmountSerializer, SplitAmountToSerializer
from api.split_calculation import split_calculation
from split.models import SplitAmountToUser, User


class SplitWiseViewSets(MultiSerializerViewSetMixin, GenericViewSet):
    serializer_action_classes = {
        "split_amount": SplitAmountSerializer,
        "get_member_passbook": SplitAmountToSerializer,
    }

    @action(methods=("post",), detail=False, permission_classes=(AllowAny,))
    def split_amount(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        split_owner = User.objects.get(email=ser.validated_data["split_owner"])
        total_amount = ser.validated_data["total_amount"]

        if ser.validated_data["split_type"] == "EQUAL":
            amount = total_amount / len(ser.validated_data["split_to"])

            for data in ser.validated_data["split_to"]:
                if data["email"] == split_owner.email:
                    continue

                borrow_by = User.objects.filter(email=data["email"]).first()
                split_calculation(borrow_by=borrow_by, split_owner=split_owner, amount=amount)

        if ser.validated_data["split_type"] == "EXACT":
            for data in ser.validated_data["split_to"]:
                if data["email"] == split_owner.email:
                    continue

                borrow_by = User.objects.filter(email=data["email"]).first()
                split_calculation(borrow_by=borrow_by, split_owner=split_owner, amount=data["amount"])

        if ser.validated_data["split_type"] == "PERCENT":
            for data in ser.validated_data["split_to"]:
                if data["email"] == split_owner.email:
                    continue

                # calculate percent
                amount = float(data["percent"] * total_amount) * (1 / 100)
                borrow_by = User.objects.filter(email=data["email"]).first()
                split_calculation(borrow_by=borrow_by, split_owner=split_owner, amount=amount)

        return Response(ser.data)

    @action(methods=("post",), detail=False, permission_classes=(AllowAny,))
    def get_member_passbook(self, request, *args, **kwargs):
        email = request.data["email"]
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User not exists.")
        instances = SplitAmountToUser.objects.filter(borrow_by__email=email)

        response = {
            "total_balance": instances.aggregate(amount=models.Sum("amount"))["amount"],
            "passbook": self.get_serializer(instance=instances, many=True).data,
        }

        return Response(response)
