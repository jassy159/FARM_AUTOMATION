# farmapi/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser


class Modules(models.Model):
    name = models.CharField(max_length=250)
    password = models.CharField(max_length=30)
    has_user = models.BooleanField(default=False)
    option = [
        ('BM', 'Basic Module'),
        ('TM' , "Temperature Module"),
        ('WM', "Water Tank Level Module"),
        ('AM', "Accutator Module")
    ]
    module_type = models.CharField(max_length=2, choices=option,null=False)

    def __str__(self):
        return self.name

class BasicModules(models.Model):
    pass

class TemperatureModules(models.Model):
    pass

class SensorModules(models.Model):
    pass

class AccutatorModules(models.Model):
    pass

class FarmerUserModel(AbstractUser):
    img = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
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