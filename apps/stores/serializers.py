from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Store
        fields = ('id', 'name', 'slug', 'description', 'logo', 'banner', 'city', 'country', 'is_active', 'owner_email')
        read_only_fields = ('id', 'slug', 'is_active', 'owner_email')

    def validate(self, attrs):
        request = self.context['request']
        if self.instance is None and Store.objects.filter(owner=request.user).exists():
            raise serializers.ValidationError('Vous possédez déjà une boutique.')
        return attrs
