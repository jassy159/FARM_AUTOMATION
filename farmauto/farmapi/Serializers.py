# serializers.py
from rest_framework import serializers
from .models import FarmerUserModel, BasicModules, Modules, LightLevelModules, WaterTankLevelModules, AccutatorModules


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

class BasicModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicModules
        fields = ['temperature', 'humidity', 'soil_moisture', 'pH_value', 'timestamp']

class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ['id', 'name', 'password', 'module_type']

class BasicModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicModules
        fields = ['temperature', 'humidity', 'soil_moisture', 'pH_value']

class LightLevelModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightLevelModules
        fields = ['light_intensity']

class WaterTankLevelModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterTankLevelModules
        fields = ['water_level']

class AccutatorModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccutatorModules
        fields = ['status']

class BasicModulesHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.CharField()
    history_date = serializers.DateTimeField()

    class Meta:
        model = BasicModules.history.model
        fields = ['id', 'history_user', 'history_date', 'history_type', 'temperature', 'humidity', 'soil_moisture', 'pH_value']

class LightLevelModulesHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.CharField()
    history_date = serializers.DateTimeField()

    class Meta:
        model = LightLevelModules.history.model
        fields = ['id', 'history_user', 'history_date', 'history_type', 'light_intensity']

class WaterTankLevelModulesHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.CharField()
    history_date = serializers.DateTimeField()

    class Meta:
        model = WaterTankLevelModules.history.model
        fields = ['id', 'history_user', 'history_date', 'history_type', 'water_level']

class AccutatorModulesHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.CharField()
    history_date = serializers.DateTimeField()

    class Meta:
        model = AccutatorModules.history.model
        fields = ['id', 'history_user', 'history_date', 'history_type', 'status']