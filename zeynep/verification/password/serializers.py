from django.db import transaction

from rest_framework import serializers

from zeynep.auth.models import User
from zeynep.verification.models import PasswordResetVerification
from zeynep.verification.registration.serializers import BaseCheckSerializer


class PasswordResetVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetVerification
        fields = ("email",)

    def validate_email(self, email):  # noqa
        return User.objects.normalize_email(email)

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data["user"] = User.objects.get(
                email=validated_data["email"]
            )
        except User.DoesNotExist:
            return validated_data

        verification = super().create(validated_data)
        verification.send_email()
        return verification


class PasswordResetVerificationCheckSerializer(BaseCheckSerializer):  # noqa
    model = PasswordResetVerification
