# farmapi/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

class Modules(models.Model):
    name = models.CharField(max_length=250, unique=True)
    password = models.CharField(max_length=30)
    has_user = models.BooleanField(default=False)
    options = [
        ('BM', 'Basic Module'),
        ('LM', "Light Intensity Module"),
        ('WM', "Water Level Module"),
        ('AM', "Accutator Module")
    ]

    module_type = models.CharField(max_length=2, choices=options, null=False)

    def __str__(self):
        return self.name

    history = HistoricalRecords()

class BasicModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='basic_module')
    temperature = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    soil_moisture = models.FloatField(null=True)
    pH_value = models.FloatField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.name} - Basic Module"

    history = HistoricalRecords()

class LightLevelModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='light_module')
    light_intensity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.name} - Light Level Module"

    history = HistoricalRecords()

class WaterTankLevelModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='water_tank_module')
    water_level = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.name} - Water Tank Level Module"

    history = HistoricalRecords()
    
class AccutatorModules(models.Model):
    module = models.OneToOneField(Modules, on_delete=models.CASCADE, related_name='accutator_module')
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    value_pattern = models.CharField(max_length=10, blank=True, null=True)  # either "Individual" or "Average"
    sensor_module = models.ForeignKey(Modules, on_delete=models.CASCADE, blank=True, null=True)
    sensor_type = models.CharField(max_length=50, blank=True, null=True)  # applicable in both "Individual" and "Average" cases
    min_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.module.name} - Accutator Module"

    def __str__(self):
        return f"{self.module.name} - Accutator Module"

    history = HistoricalRecords()

class FarmerUserModel(AbstractUser):
    img = models.ImageField(upload_to='dds/', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def save(self, *args, **kwargs):
        # Ensure that a superuser cannot be a normal user
        if self.is_superuser:
            self.is_normal_user = False
        super().save(*args, **kwargs)

    modules = models.ManyToManyField(Modules, related_name='farmers')

    def __str__(self):
        return self.username

    history = HistoricalRecords()