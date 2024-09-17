# serializers.py
from rest_framework import serializers
from .models import FarmerUserModel

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = FarmerUserModel
        fields = ('username', 'email', 'phone_number', 'img', 'password')

    def create(self, validated_data):
        user = FarmerUserModel(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
