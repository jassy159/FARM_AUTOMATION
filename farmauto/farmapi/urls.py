from django.urls import path,include
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = routers.DefaultRouter()




urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('',views.HomeView, name = 'home'),
    path('dashboard', views.DashboardView , name='dashboard'),
    path('admindashboard', views.AdminDashboardView , name='admindashboard'),
    path('createModule/',views.CreateModule, name='addModuleAdmin'),
    path('delete/<int:pk>',views.ModuleDelete,name='deleteModule'),
    path('moduleAssign/<int:farmer_id>', views.assign_module_to_farmer, name='assignModule'),
     path('removeModule/<int:farmer_id>/<int:module_id>/', views.remove_module_from_farmer, name='detachModule'),
    path('login/', views.LoginView, name='login'),
    path('register/',views.registerView, name = 'register'),
    path('api/basicmodules/<str:module_name>/', views.BasicModuleCreateView.as_view(), name='basic_module_update'),
        path('api/light-level-module/<str:module_name>/', views.LightLevelModuleUpdateView.as_view(), name='light-level-module-update'),
    path('api/water-tank-module/<str:module_name>/', views.WaterTankLevelModuleUpdateView.as_view(), name='water-tank-module-update'),
    
    # Include the router URLs
    #previous Data 
     path('api/basic-modules/<str:module_name>/all-previous/', views.BasicModulesHistoryView.as_view(), name='basic-module-all-previous-data'),
    path('api/water-tank-modules/<str:module_name>/all-previous/', views.WaterTankLevelModulesHistoryView.as_view(), name='water-tank-module-all-previous-data'),
    path('api/light-level-modules/<str:module_name>/all-previous/', views.LightLevelModulesHistoryView.as_view(), name='light-level-module-all-previous-data'),
    #update accutators
     path('accutator_modules/<str:module_name>', views.accutator_module_update_view, name='accutator_module_update'),


         path('get-sensor-types/', views.get_sensor_types, name='get_sensor_types'),
   

    #accutator state 
    path('accustate/get_accutator_modules/<str:module_name>',views.get_accutator_modules,name='get_accutator_modules')
    ]
