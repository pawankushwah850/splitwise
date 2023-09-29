from django.db.models import F
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.mixins import MultiSerializerViewSetMixin
from api.serializer import SplitAmountSerializer, SplitAmountToSerializer
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

        if ser.validated_data["split_type"] == "EQUAL":
            amount = ser.validated_data["total_amount"] / len(
                ser.validated_data["split_to"]
            )

            for data in ser.validated_data["split_to"]:
                if data["email"] == split_owner.email:
                    continue

                borrow_by = User.objects.filter(email=data["email"]).first()

                # condition need to check, if split owner borrow amount from this user before
                instance = SplitAmountToUser.objects.filter(
                    borrow_from=borrow_by, borrow_by=split_owner, amount__gte=1
                )
                if instance.exists():
                    instance = instance.first()

                    # Now check how much split owner borrow amount before
                    if instance.amount > amount:
                        instance.amount = F("amount") - amount
                        instance.save(update_fields=("amount",))
                    else:
                        amount -= instance.amount

                        # update balance or create split amount
                        SplitAmountToUser.objects.update_or_create(
                            defaults=dict(
                                borrow_from=split_owner,
                                borrow_by=borrow_by,
                            ),
                            amount=amount,
                        )

                        # update balance 0 if no borrow amount is pending
                        SplitAmountToUser.objects.filter(
                            borrow_from=borrow_by, borrow_by=split_owner
                        ).update(amount=0)
                else:
                    # now check if split owner again giving money to same user then add amount
                    # Other wise create split amount
                    ins = SplitAmountToUser.objects.filter(
                        borrow_from=split_owner, borrow_by=borrow_by
                    )
                    if ins.exists():
                        ins.update(amount=F("amount") + amount)
                    else:
                        SplitAmountToUser.objects.create(
                            borrow_from=split_owner, borrow_by=borrow_by, amount=amount
                        )

        if ser.validated_data["split_type"] == "EXACT":
            for data in ser.validated_data["split_to"]:
                if data["email"] == split_owner.email:
                    continue

                amount = data["amount"]
                borrow_by = User.objects.filter(email=data["email"]).first()

                # condition need to check, if split owner borrow amount from this user before
                instance = SplitAmountToUser.objects.filter(
                    borrow_from=borrow_by, borrow_by=split_owner, amount__gte=1
                )
                if instance.exists():
                    instance = instance.first()
                    # Now check how much split owner borrow amount before
                    if instance.amount > amount:
                        instance.amount = F("amount") - amount
                        instance.save(update_fields=("amount",))
                    else:
                        amount -= instance.amount

                        # update balance or create split amount
                        SplitAmountToUser.objects.update_or_create(
                            defaults=dict(
                                borrow_from=split_owner,
                                borrow_by=borrow_by,
                            ),
                            amount=amount,
                        )

                        # update balance 0 if not borrow amount is pending
                        SplitAmountToUser.objects.filter(
                            borrow_from=borrow_by, borrow_by=split_owner
                        ).update(amount=0)
                else:
                    # now check if split owner again giving money to same user then add amount
                    # Other wise create split amount

                    ins = SplitAmountToUser.objects.filter(
                        borrow_from=split_owner, borrow_by=borrow_by
                    )
                    if ins.exists():
                        ins.update(amount=F("amount") + amount)
                    else:
                        SplitAmountToUser.objects.create(
                            borrow_from=split_owner, borrow_by=borrow_by, amount=amount
                        )

        if ser.validated_data["split_type"] == "PERCENT":
            for data in ser.validated_data["split_to"]:
                if data["email"] == split_owner.email:
                    continue

                total_amount = ser.validated_data["total_amount"]

                amount = float(data["percent"] * total_amount) * (1 / 100)
                borrow_by = User.objects.filter(email=data["email"]).first()

                # condition need to check, if split owner borrow amount from this user before
                instance = SplitAmountToUser.objects.filter(
                    borrow_from=borrow_by, borrow_by=split_owner, amount__gte=1
                )
                if instance.exists():
                    # Now check how much split owner borrow amount before
                    instance = instance.first()
                    if instance.amount > amount:
                        instance.amount = F("amount") - amount
                        instance.save(update_fields=("amount",))
                    else:
                        amount -= instance.amount

                        # update balance or create split amount
                        SplitAmountToUser.objects.update_or_create(
                            defaults=dict(
                                borrow_from=split_owner,
                                borrow_by=borrow_by,
                            ),
                            amount=amount,
                        )

                        # update balance 0 if not borrow amount is pending
                        SplitAmountToUser.objects.filter(
                            borrow_from=borrow_by, borrow_by=split_owner
                        ).update(amount=0)
                else:
                    # now check if split owner again giving money to same user then add amount
                    # Other wise create split amount

                    ins = SplitAmountToUser.objects.filter(
                        borrow_from=split_owner, borrow_by=borrow_by
                    )
                    if ins.exists():
                        ins.update(amount=F("amount") + amount)
                    else:
                        SplitAmountToUser.objects.create(
                            borrow_from=split_owner, borrow_by=borrow_by, amount=amount
                        )

        return Response(ser.data)

    @action(methods=("post",), detail=False, permission_classes=(AllowAny,))
    def get_member_passbook(self, request, *args, **kwargs):
        email = request.data["email"]
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User not exists.")
        instances = SplitAmountToUser.objects.filter(borrow_by__email=email)
        return Response(self.get_serializer(instance=instances, many=True).data)
