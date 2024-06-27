from rest_framework import serializers

from users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    confirm_password = serializers.CharField(
        max_length=128,
    )

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'confirm_password',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                "Пароли не совпадают"
            )
        return attrs


class ChangedPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        max_length=128,
    )
    new_password = serializers.CharField(
        max_length=128,
    )
    confirm_password = serializers.CharField(
        max_length=128,
    )

    class Meta:
        model = CustomUser
        fields = [
            'old_password',
            'new_password',
            'confirm_password',
        ]

    def validate(self, attrs):
        old_password = attrs['old_password']
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError(
                "Старый пароль неверный"
            )
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                "Пароли не совпадают"
            )
        return attrs
