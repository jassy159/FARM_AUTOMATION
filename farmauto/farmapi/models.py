from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class Modules(models.Model):
    name = models.CharField(max_length=250, unique=True)
    password = models.CharField(max_length=30)
    has_user = models.BooleanField(default=False)
    user = models.ForeignKey('FarmerUserModel', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_modules')

    MODULE_TYPES = (
        ('BM', 'Basic Module'),
        ('LM', "Light Intensity Module"),
        ('WM', "Water Level Module"),
        ('AM', "Actuator Module"),
    )

    module_type = models.CharField(max_length=2, choices=MODULE_TYPES, null=False)

    def __str__(self):
        return self.name

    history = HistoricalRecords()


class BasicModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='basic_module')
    temperature = models.FloatField(null=True , default=0)
    humidity = models.FloatField(null=True, default=0)
    soil_moisture = models.FloatField(null=True, default=0)
    pH_value = models.FloatField(null=True, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.name} - Basic Module"

    history = HistoricalRecords()


class LightLevelModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='light_module')
    light_intensity = models.FloatField( default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.name} - Light Level Module"

    history = HistoricalRecords()


class WaterTankLevelModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='water_tank_module')
    water_level = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.name} - Water Tank Level Module"

    history = HistoricalRecords()


class AccutatorModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='actuator_module')
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    value_pattern = models.CharField(max_length=10, blank=True, null=True)  # either "Individual" or "Average"
    sensor_module = models.ForeignKey(Modules, on_delete=models.CASCADE, blank=True, null=True, related_name='linked_sensor_module')
    sensor_type = models.CharField(max_length=50, blank=True, null=True)  # applicable in both "Individual" and "Average" cases
    triggerValue = models.IntegerField(null=True)
    
    inverse = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.module.name} - Actuator Module"

    history = HistoricalRecords()


class FarmerUserModel(AbstractUser):
    img = models.ImageField(upload_to='dds/', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    modules = models.ManyToManyField(Modules, related_name='farmers')

    def save(self, *args, **kwargs):
        # Ensure that a superuser cannot be a normal user
        if self.is_superuser:
            self.is_normal_user = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    history = HistoricalRecords()
