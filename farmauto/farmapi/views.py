# views.py
from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django import forms
from django.contrib.auth import authenticate , login
from .Serializers import CustomUserSerializer
from .forms import RegisterationForm, ModuleCreateForm , FarmerModuleAssignForm
from .models import Modules, FarmerUserModel
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
        return render(request, 'dashboard.html', {'user' : user})
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