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
            return render(request, 'login.html', {"error" : "invalid password"})
        
    return render(request, 'login.html')    


#dashboard for farmers
def DashboardView(request):
    user = request.user
    if user.is_authenticated:
        farmer = FarmerUserModel.objects.get(pk=user.id)
        farmer_sensor = farmer.modules.exclude(module_type='AM')
        farmer_acc = AccutatorModules.objects.filter(module__user=farmer)
        print([x.module_type for x in farmer_sensor],'-----')
        moduleType = [x.module_type for x in farmer_sensor]
        print(moduleType)
        moduleValues = {}
        for i in range(0,len(farmer_sensor)):
            if(moduleType[i]=="LM"):
                lm = (LightLevelModules.objects.get(module = farmer_sensor[i]))
                moduleValues[f'{lm.module.name} light intensity'] = lm.light_intensity
            elif(moduleType[i]=="BM"):
                bm = BasicModules.objects.get(module = farmer_sensor[i])
                print(bm.module.name)
                moduleValues[f'{bm.module.name} temperature'] = bm.temperature
                moduleValues[f'{bm.module.name} humidity'] = bm.humidity
                moduleValues[f'{bm.module.name} soilmoisture'] = bm.soil_moisture
                moduleValues[f'{bm.module.name} ph Value'] = bm.pH_value
                    
                # bmValues = [bm.temperature, bm.]
            elif(moduleType[i]=="WM"):
                wm = WaterTankLevelModules.objects.get(module = farmer_sensor[i])
                moduleValues[f'{wm.module.name} watermodule'] = wm.water_level
            

        print(moduleValues,'************')        #needs MOdifcation



        return render(request, 'dashboard.html', {'user' : user,'farmer':farmer , "sensor":farmer_sensor,'accutator':farmer_acc,'values': moduleValues})
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


@login_required
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
                module.user = request.user
                module.save()
            return redirect('assignModule', farmer_id)
    else:
        form = FarmerModuleAssignForm()
    return render(request, 'addModule.html', {'form': form, "farmer": farmer})
#remove the module from farmer

def remove_module_from_farmer(request, farmer_id, module_id):
    farmer = get_object_or_404(FarmerUserModel, id=farmer_id)
    print(farmer)
    print(module_id)
    module = Modules.objects.get(id=module_id)
    print(module)
    print(module.has_user , module.user)
    module.has_user = False
    module.user = None
    print(module.has_user , module.user)
    # Remove the module from the farmer's modules
    module.save()
    farmer.modules.remove(module)
    print(farmer.modules.all())
    return redirect('dashboard')


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
        'triggerValue' : accutator_module.triggerValue,
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
    triggerValue , valuePattern, sensorType = accutator_module.triggerValue,accutator_module.value_pattern,accutator_module.sensor_type
    inverse = accutator_module.inverse
    user = FarmerUserModel.objects.get(modules = Modules.objects.filter(name=module_name)[0])
    print(user , inverse)
    if(valuePattern == 'Average'):
        pass
    #     ar = 0
    #     n=0
    #     if(sensorType in ['temperature', 'humidity','soilmoisture','phvalue']):
    #         pass
    #     elif(sensorType == "lightsensor"):
    #         print(10)
    #         user_modules = user.modules.filter(module_type='LM')  # Only Light Intensity Modules
    #         light_object = LightLevelModules.objects.filter(module__in = user_modules)
            
    #         for i in light_object:
    #             print(10)
    #             n = n+1
    #             ar = ar + float(getattr(i,"light_intensity"))

            
            
    #     return JsonResponse({"avg":ar/n})        
            
    else:
            print(accutator_module.sensor_module.module_type,999999999999)
            if(accutator_module.sensor_module.module_type == "BM"):
                sensorModule = BasicModules.objects.get(module = accutator_module.sensor_module)
                
                if sensorType == "temperature":
                    
                    temp = getattr(sensorModule, 'temperature')
                    if(inverse == False):
                        if(sensorModule.temperature > triggerValue):
                            state = True
                        else:
                            state = False
                    else:
                        if(sensorModule.temperature > triggerValue):
                            state = False
                        else:
                            state = True   
                    accutator_module.status = state
                    accutator_module.save()                                   
                    return JsonResponse({"state":state})
                if sensorType == "humidity":
                    
                    temp = getattr(sensorModule, 'temperature')
                    print(temp)
                    if(inverse == False):
                        if(sensorModule.humidity > triggerValue):
                            state = True
                        else:
                            state = False
                    else:
                        if(sensorModule.humidity > triggerValue):
                            state = False
                        else:
                            state = True   
                    accutator_module.status = state
                    accutator_module.save()  
                    return JsonResponse({"state":state})
                
                if sensorType == "soilmoisture":
                    
                    
                    if(inverse == False):
                        if(sensorModule.soil_moisture > triggerValue):
                            state = True
                        else:
                            state = False
                    else:
                        if(sensorModule.soil_moisture > triggerValue):
                            state = False
                        else:
                            state = True   
                    accutator_module.status = state
                    accutator_module.save()  
                    return JsonResponse({"state":state})
                if sensorType == "phvalue":
                    
                    
                    if(inverse == False):
                        if(sensorModule.pH_value > triggerValue):
                            state = True
                        else:
                            state = False
                    else:
                        if(sensorModule.pH_value > triggerValue):
                            state = False
                        else:
                            state = True   
                    accutator_module.status = state
                    accutator_module.save()  
                    return JsonResponse({"state":state})
            elif(accutator_module.sensor_module.module_type == "LM"):
                
                
                sensorModule = LightLevelModules.objects.get(module = accutator_module.sensor_module)
                
                if(inverse == False):
                        if(sensorModule.light_intensity > triggerValue):
                            state = True
                        else:
                            state = False
                else:
                        if(sensorModule.light_intensity > triggerValue):
                            state = False
                        else:
                            state = True   
                
                
                accutator_module.status = state
                accutator_module.save()             
                return JsonResponse({"state":state})  
            
            elif(accutator_module.sensor_module.module_type == "WM"):
                sensorModule = WaterTankLevelModules.objects.get(module = accutator_module.sensor_module)
                if(inverse == False):
                        if(sensorModule.water_level > triggerValue):
                            state = True
                        else:
                            state = False
                else:
                        if(sensorModule.water_level > triggerValue):
                            state = False
                        else:
                            state = True   
                
                
                accutator_module.status = state
                accutator_module.save()    
                return JsonResponse({"state":state})  




from django.shortcuts import render
from .models import BasicModules, LightLevelModules, WaterTankLevelModules, AccutatorModules

def module_history_chart(request):
    # Fetch data for Basic Modules
    basic_modules = BasicModules.objects.all()
    temperature_values = [module.temperature for module in basic_modules]
    humidity_values = [module.humidity for module in basic_modules]
    soil_moisture_values = [module.soil_moisture for module in basic_modules]
    basic_timestamps = [module.timestamp.strftime("%Y-%m-%d %H:%M:%S") for module in basic_modules]

    # Fetch data for Light Level Modules
    light_modules = LightLevelModules.objects.all()
    light_level_values = [module.light_intensity for module in light_modules]
    light_timestamps = [module.timestamp.strftime("%Y-%m-%d %H:%M:%S") for module in light_modules]

    # Fetch data for Water Tank Level Modules
    water_modules = WaterTankLevelModules.objects.all()
    water_level_values = [module.water_level for module in water_modules]
    water_timestamps = [module.timestamp.strftime("%Y-%m-%d %H:%M:%S") for module in water_modules]

    # Fetch data for Actuator Modules
    actuator_modules = AccutatorModules.objects.all()
    actuator_status_values = [module.status for module in actuator_modules]
    actuator_timestamps = [module.timestamp.strftime("%Y-%m-%d %H:%M:%S") for module in actuator_modules]

    context = {
        'basic_timestamps': basic_timestamps,
        'temperature_values': temperature_values,
        'humidity_values': humidity_values,
        'soil_moisture_values': soil_moisture_values,
        
        'light_timestamps': light_timestamps,
        'light_level_values': light_level_values,
        
        'water_timestamps': water_timestamps,
        'water_level_values': water_level_values,
        
        'actuator_timestamps': actuator_timestamps,
        'actuator_status_values': actuator_status_values,
    }

    return render(request, 'module_history_chart.html', context)
