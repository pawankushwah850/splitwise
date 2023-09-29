from rest_framework import serializers

from split.models import SplitAmountToUser, User


class SplitAmountSerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=1)
    split_type = serializers.ChoiceField(
        choices=[("EQUAL", "EQUAL"), ("PERCENT", "PERCENT"), ("EXACT", "EXACT")]
    )
    split_owner = serializers.EmailField()
    split_to = serializers.ListField(child=serializers.DictField())

    def validate_split_owner(self, value):
        """ "
        Note: Split owner we can handle from request.user, but for task
                I am doing manually
        """
        if not User.objects.filter(email=value).exists():
            serializers.ValidationError("split owner not exist")
        return value

    def validate(self, attrs):
        # validating emails
        for user in attrs.get("split_to"):
            if not User.objects.filter(email=user["email"]).exists():
                raise serializers.ValidationError(f"Email {user['email']} not exists.")

        if attrs.get("split_type") == "EQUAL":
            pass

        elif attrs.get("split_type") == "PERCENT":
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
    class Meta:
        model = SplitAmountToUser
        fields = "__all__"
