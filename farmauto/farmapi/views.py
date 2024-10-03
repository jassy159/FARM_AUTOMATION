# views.py
import json
from django.db.models import F
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django import forms
from django.contrib.auth import authenticate , login
from .Serializers import( CustomUserSerializer , BasicModulesSerializer , AccutatorModulesSerializer , 
                         LightLevelModulesSerializer, WaterTankLevelModulesSerializer ,
                         BasicModulesHistorySerializer , WaterTankLevelModulesHistorySerializer,
                         LightLevelModulesHistorySerializer ,AccutatorModulesHistorySerializer)
from .forms import RegisterationForm, ModuleCreateForm , FarmerModuleAssignForm , AccutatorModuleForm
from .models import Modules, FarmerUserModel , BasicModules ,LightLevelModules, AccutatorModules , WaterTankLevelModules
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404  

#to register normal user
def registerView(request):
    if request.method == "POST":
        form = RegisterationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = RegisterationForm()
    return render(request, 'register.html',{"form": form})

#to login for everyone
def LoginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request , username = username,password =  password)

        if user is not None:
            print(user)
            login(request, user)
            refresh = RefreshToken.for_user(user)
            request.session['jwt_token'] = str(refresh.access_token)
            if request.user.is_superuser:
                return redirect('admindashboard')
            else:

                return redirect('dashboard')
        else:
            print(user)
            return render(request, 'login.html', {"error" : "invalid"})
        
    return render(request, 'login.html')    


#dashboard for farmers
def DashboardView(request):
    user = request.user
    if user.is_authenticated:
        farmer = FarmerUserModel.objects.get(pk=user.id)
        farmer_sensor = farmer.modules.exclude(module_type='AM')
        farmer_acc = farmer.modules.filter(module_type='AM')
        print(farmer_sensor)

        return render(request, 'dashboard.html', {'user' : user,'farmer':farmer , "sensor":farmer_sensor,'accutator':farmer_acc})
    else:
        return redirect('login')
    

#dashboard for superuser
@user_passes_test(lambda u: u.is_superuser) #checks and allow if user is superuser
def AdminDashboardView(request):
    modules = Modules.objects.all()
    return render(request, 'admindashboard.html',{'modules' : modules})

#home view
def HomeView(request):
    return render(request, 'index.html')




#form for superuser to create modules
@user_passes_test(lambda u: u.is_superuser)
def CreateModule(request):
    if request.method == 'POST':
        form = ModuleCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admindashboard')
    else:
        form = ModuleCreateForm()
    modules = Modules.objects.all()        
    return render(request, 'createModule.html', {'form': form,'modules':modules})

#superuser to delete modules
@user_passes_test(lambda u: u.is_superuser)
def ModuleDelete(request, pk):
    Module = get_object_or_404(Modules, pk=pk)
    
    
    Module.delete()
    return redirect('admindashboard')
    

# View to assign modules to a farmer



def assign_module_to_farmer(request, farmer_id):
    farmer = FarmerUserModel.objects.get(pk=farmer_id)
    if request.method == 'POST':
        form = FarmerModuleAssignForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            selected_modules = form.cleaned_data.get("modules")
            for module in selected_modules:
                if module.password != password:
                    raise forms.ValidationError(f"Password for module '{module.name}' does not match.")
                farmer.modules.add(module)  # Add the module to the farmer's modules
                module.has_user = True  # Set has_user to True
                module.save()
            return redirect('assignModule', farmer_id)
    else:
        form = FarmerModuleAssignForm()
    return render(request, 'addModule.html', {'form': form, "farmer": farmer})
#remove the module from farmer
def remove_module_from_farmer(request, farmer_id, module_id):
    farmer = get_object_or_404(FarmerUserModel, id=farmer_id)
    module = get_object_or_404(Modules, id=module_id)

    # Remove the module from the farmer's modules
    if module in farmer.modules.all():
        farmer.modules.remove(module)

    return redirect('assignModule',farmer_id=farmer.id)


class BasicModuleCreateView(APIView):
    
    def post(self, request, module_name):
        try:
            # Get the module using its name
            module = Modules.objects.get(name=module_name)
        except Modules.DoesNotExist:
            return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

        # Try to get existing BasicModules instance or create a new one
        basic_module, created = BasicModules.objects.get_or_create(module=module)

        # Update the existing entry with the new data
        serializer = BasicModulesSerializer(basic_module, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated values
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, module_name):
        try:
            module = Modules.objects.get(name=module_name)
        except Modules.DoesNotExist:
            return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all BasicModules entries linked to this module
        basic_modules = BasicModules.objects.filter(module=module)
        serializer = BasicModulesSerializer(basic_modules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class LightLevelModuleUpdateView(APIView):
    def get(self, request, module_name):
        try:
            module = LightLevelModules.objects.get(module__name=module_name)
        except LightLevelModules.DoesNotExist:
            return Response({'error': 'Light Level Module not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LightLevelModulesSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, module_name):
        try:
            module = LightLevelModules.objects.get(module__name=module_name)
        except LightLevelModules.DoesNotExist:
            return Response({'error': 'Light Level Module not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LightLevelModulesSerializer(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaterTankLevelModuleUpdateView(APIView):
    def get(self, request, module_name):
        try:
            module = WaterTankLevelModules.objects.get(module__name=module_name)
        except WaterTankLevelModules.DoesNotExist:
            return Response({'error': 'Water Tank Level Module not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = WaterTankLevelModulesSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, module_name):
        try:
            module = WaterTankLevelModules.objects.get(module__name=module_name)
        except WaterTankLevelModules.DoesNotExist:
            return Response({'error': 'Water Tank Level Module not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = WaterTankLevelModulesSerializer(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#previous Data
# Historical data views

class BasicModulesHistoryView(APIView):
    def get(self, request, module_name):
        module = Modules.objects.filter(name=module_name)
        pk = module.first().pk
        basic_modules = BasicModules.objects.filter(module_id=pk)
        history = basic_modules.first().history.all()
        serializer = BasicModulesHistorySerializer(history, many=True)
        return Response(serializer.data)

class LightLevelModulesHistoryView(APIView):
    def get(self, request, module_name):
        module = Modules.objects.filter(name=module_name)
        
        pk = module.first().pk
        
        light_level_modules = LightLevelModules.objects.filter(module_id=pk)
        print(light_level_modules)
        history = light_level_modules.first().history.all()
        print(history)
        serializer = LightLevelModulesHistorySerializer(history, many=True)
        return Response(serializer.data)

class WaterTankLevelModulesHistoryView(APIView):
    def get(self, request, module_name):
        module = Modules.objects.filter(name=module_name)
        pk = module.first().pk
        print(pk)
        water_tank_level_modules = WaterTankLevelModules.objects.filter(module_id=pk)
        
        history = water_tank_level_modules.first().history.all()
        serializer = WaterTankLevelModulesHistorySerializer(history, many=True)
        return Response(serializer.data)

class AccutatorModulesHistoryView(APIView):
    def get(self, request, module_name):
        module = Modules.objects.filter(name=module_name)
        pk = module.first().pk
        accutator_modules = AccutatorModules.objects.filter(module_id=pk)
        history = accutator_modules.first().history.all()
        serializer = AccutatorModulesHistorySerializer(history, many=True)
        return Response(serializer.data)
    
# # CORRECT THE HECK UP
def accutator_module_update_view(request, module_name):
    
    accutator_module = AccutatorModules.objects.get(module=Modules.objects.filter(name=module_name)[0])
    initial_data = {
        'value_pattern': accutator_module.value_pattern,
        'sensor_module': accutator_module.sensor_module,
        'min_value': accutator_module.min_value,
        'max_value': accutator_module.max_value,
        'sensor_type': accutator_module.sensor_type,
    }

    if request.method == 'POST':
        form = AccutatorModuleForm(request=request, data=request.POST)
        

        if form.is_valid():
            value_pattern = form.cleaned_data.get('value_pattern')
            
            if value_pattern == 'Average':
                accutator_module.sensor_module = None  # Set sensor_module to None
                
            else:
                accutator_module.sensor_module = form.cleaned_data.get('sensor_module')
            # Update the instance's attributes using the form data
            accutator_module.__dict__.update(form.cleaned_data)
            accutator_module.sensor_type = form.cleaned_data.get('sensor_type')
            # Save the instance
            accutator_module.save()
            # Redirect to the next page
            return redirect('dashboard')
    else:
        form = AccutatorModuleForm(request=request, initial=initial_data)
        
    return render(request, 'EditAccutatorDet.html', {'form': form})


# def accutator_module_update_view(request, module_name):
#     print(request.user.id, "*////////*/*/**/*")
#     accutator_module = AccutatorModules.objects.get(module=Modules.objects.filter(name=module_name)[0])
#     initial_data = {
#         'value_pattern': accutator_module.value_pattern,
#         'sensor_module': accutator_module.sensor_module,
#         'min_value': accutator_module.min_value,
#         'max_value': accutator_module.max_value,
#     }

#     if request.method == 'POST':
#         form = AccutatorModuleForm(request=request, data=request.POST)
#         print(5555555555555)
#         print(form.is_valid(),99999988888888)

#         if form.is_valid():
#             value_pattern = form.cleaned_data.get('value_pattern')
#             print(value_pattern)
#             if value_pattern == 'Average':
#                 accutator_module.sensor_module = None  # Set sensor_module to None
                
#             else:
#                 accutator_module.sensor_module = form.cleaned_data.get('sensor_module')
#             # Update the instance's attributes using the form data
#             accutator_module.__dict__.update(form.cleaned_data)
#             # Save the instance
#             accutator_module.save()
#             # Redirect to the next page
#             return redirect('dashboard')
#     else:
#         form = AccutatorModuleForm(request=request, initial=initial_data)
        
#     return render(request, 'EditAccutatorDet.html', {'form': form})

def get_sensor_types(request):
    module_id = request.GET.get('module_id')
    sensor_types = []

    if module_id:
        try:
            module = Modules.objects.get(pk=module_id)
            if module.module_type == 'BM':
                sensor_types = [
                    {'value': 'temperature', 'label': 'Temperature'},
                    {'value': 'humidity', 'label': 'Humidity'},
                    {'value': 'soilmoisture', 'label': 'Soil Moisture'},
                    {'value': 'phvalue', 'label': 'pH Value'},
                ]
            elif module.module_type == 'LM':
                
                sensor_types = [{'value': 'lightsensor', 'label': 'Light Sensor'}]
            elif module.module_type == 'WM':
                sensor_types = [{'value': 'waterlevel', 'label': 'Water Level'}]
        except Modules.DoesNotExist:
            pass

    return JsonResponse(sensor_types, safe=False)

def update_sensor_module_value(request):
    value_pattern = request.GET.get('value_pattern')
    if value_pattern:    
        if value_pattern == "Average":
            print('Averag')
        else:
            print("indi")
    return JsonResponse("inid", safe=False)                
    #     try:
    #         module = Modules.objects.get(pk=module_id)
    #         if module.module_type == 'BM':
    #             sensor_types = [
    #                 {'value': 'temperature', 'label': 'Temperature'},
    #                 {'value': 'humidity', 'label': 'Humidity'},
    #                 {'value': 'soilmoisture', 'label': 'Soil Moisture'},
    #                 {'value': 'phvalue', 'label': 'pH Value'},
    #             ]
    #         elif module.module_type == 'LM':
                
    #             sensor_types = [{'value': 'lightsensor', 'label': 'Light Sensor'}]
    #         elif module.module_type == 'WM':
    #             sensor_types = [{'value': 'waterlevel', 'label': 'Water Level'}]
    #     except Modules.DoesNotExist:
    #         pass

    # return JsonResponse(sensor_types, safe=False)


@api_view(['GET'])
def get_accutator_modules(request, module_name):
    accutator_module = AccutatorModules.objects.get(module=Modules.objects.filter(name=module_name)[0])
    min,max , valuePattern, sensorType = accutator_module.min_value,accutator_module.max_value,accutator_module.value_pattern,accutator_module.sensor_type
    user = FarmerUserModel.objects.get(modules = Modules.objects.filter(name=module_name)[0])
    print(user)
    if(valuePattern == 'Average'):
        ar = 0
        n=0
        if(sensorType in ['temperature', 'humidity','soilmoisture','phvalue']):
            pass
        elif(sensorType == "lightsensor"):
            print(10)
            user_modules = user.modules.filter(module_type='LM')  # Only Light Intensity Modules
            light_object = LightLevelModules.objects.filter(module__in = user_modules)
            
            for i in light_object:
                print(10)
                n = n+1
                ar = ar + float(getattr(i,"light_intensity"))

            
            
        return JsonResponse({"avg":ar/n})        
            
    else:
            print(accutator_module.sensor_module.module_type,999999999999)
            if(accutator_module.sensor_module.module_type == "BM"):
                sensorModule = BasicModules.objects.get(module = accutator_module.sensor_module)
                
                if sensorType == "temperature":
                    
                    temp = getattr(sensorModule, 'temperature')
                    print(temp)
                    
                    return JsonResponse({"sensorModule":temp,})
                if sensorType == "humidity":
                    
                    temp = getattr(sensorModule, 'temperature')
                    print(temp)
                    return JsonResponse({"sensorModule":temp})
                if sensorType == "soilmoisture":
                    
                    temp = getattr(sensorModule, 'temperature')
                    print(temp)
                    return JsonResponse({"sensorModule":temp})
                if sensorType == "phvalue":
                    
                    temp = getattr(sensorModule, 'temperature')
                    print(temp)
                    return JsonResponse({"sensorValue":temp})
            elif(accutator_module.sensor_module.module_type == "LM"):
                print(55    )
                sensorModule = LightLevelModules.objects.get(module = accutator_module.sensor_module)
                print(sensorModule)
                light = getattr(sensorModule,'light_intensity')
                return JsonResponse({"sensorValue":light})  
            
            elif(accutator_module.sensor_module.module_type == "WM"):
                sensorModule = WaterTankLevelModules.objects.get(module = accutator_module.sensor_module)
                water_level = getattr(sensorModule,'water_level')
                return JsonResponse({"sensorValue":water_level})  