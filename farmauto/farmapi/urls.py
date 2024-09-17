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
    path('register/',views.registerView, name = 'register')
     # Include the router URLs
]
