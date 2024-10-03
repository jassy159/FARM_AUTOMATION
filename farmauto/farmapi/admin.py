from django.contrib import admin
from . import models

admin.site.register(models.FarmerUserModel)
admin.site.register(models.Modules)
admin.site.register(models.WaterTankLevelModules)
admin.site.register(models.BasicModules)
admin.site.register(models.LightLevelModules)
admin.site.register(models.AccutatorModules)

