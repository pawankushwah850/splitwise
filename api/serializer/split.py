from rest_framework import serializers

from split.models import SplitAmountToUser, User


class UserAndSplitAmountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(required=False, max_digits=8, decimal_places=2)
    percent = serializers.DecimalField(required=False, max_digits=8, decimal_places=2)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(f"Invalid email {value}.")

        return value


class SplitAmountSerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=1)
    split_type = serializers.ChoiceField(choices=[("EQUAL", "EQUAL"), ("PERCENT", "PERCENT"), ("EXACT", "EXACT")])
    split_owner = serializers.EmailField()
    split_to = UserAndSplitAmountSerializer(many=True)

    def validate_split_owner(self, value):
        """ "
        Note: Split owner we can handle from request.user, but for task
                I am doing manually
        """
        if not User.objects.filter(email=value).exists():
            serializers.ValidationError("split owner not exist")
        return value

    def validate(self, attrs):
        if attrs.get("split_type") == "PERCENT":
            # validating share percent
            total_share = sum([i["percent"] for i in attrs.get("split_to")])
            if not total_share == 100:
                raise serializers.ValidationError("Total share percent is wrong.")

        elif attrs.get("split_type") == "EXACT":
            # validating share amount
            total_share = sum([i["amount"] for i in attrs.get("split_to")])

            if not total_share == attrs.get("total_amount"):
                raise serializers.ValidationError("Total share amount is wrong.")

        return attrs


class SplitAmountToSerializer(serializers.ModelSerializer):
    borrow_from_name = serializers.CharField(source="borrow_from.get_full_name")
    borrow_from = serializers.CharField(source="borrow_from.email")

    borrow_by_name = serializers.CharField(source="borrow_by.get_full_name")
    borrow_by = serializers.CharField(source="borrow_by.email")

    class Meta:
        model = SplitAmountToUser
        fields = "__all__"
