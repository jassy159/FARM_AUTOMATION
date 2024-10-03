from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Modules, BasicModules, LightLevelModules, WaterTankLevelModules, AccutatorModules

@receiver(post_save, sender=Modules)
def create_appropriate_module(sender, instance, created, **kwargs):
    if created:
        if instance.module_type == 'BM':  # Basic Module
            BasicModules.objects.create(module=instance)
        elif instance.module_type == 'LM':  # Temperature Module (if different from basic)
            LightLevelModules.objects.create(module=instance, light_intensity=0.0)
        elif instance.module_type == 'WM':  # Water Tank Level Module
            WaterTankLevelModules.objects.create(module=instance, water_level=0.0)
        elif instance.module_type == 'AM':  # Accutator Module
            AccutatorModules.objects.create(module=instance, status=False)
