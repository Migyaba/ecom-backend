from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Address


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone', 'avatar')
        read_only_fields = ('id', 'email')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'label', 'full_name', 'line1', 'line2', 'city', 'state', 'country', 'is_default')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if validated_data.get('is_default'):
            Address.objects.filter(user=validated_data['user']).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default'):
            Address.objects.filter(user=instance.user).exclude(pk=instance.pk).update(is_default=False)
        return super().update(instance, validated_data)
