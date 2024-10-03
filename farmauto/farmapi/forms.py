from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import FarmerUserModel, Modules ,AccutatorModules

class RegisterationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = FarmerUserModel
        fields = ['username', 'email' , 'phone_number' ,'img', 'password1' , 'password2']

class ModuleCreateForm(forms.ModelForm):
    class Meta:
        model = Modules
        fields = ['name' , 'password' , 'module_type']

class FarmerModuleAssignForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = FarmerUserModel
        fields = ['modules']  # Only show modules for selection

    def __init__(self, *args, **kwargs):
        super(FarmerModuleAssignForm, self).__init__(*args, **kwargs)
        self.fields['modules'].queryset = Modules.objects.filter(has_user=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        selected_module = cleaned_data.get("modules").first()

        # Validate password for the selected module
        if selected_module:
            if selected_module.password != password:
                raise forms.ValidationError(f"Password for module '{selected_module.name}' does not match.")

        return cleaned_data




class AccutatorModuleForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    VALUE_PATTERN_CHOICES = [
        ('Individual', 'Individual Value'),
        ('Average', 'Average Value'),
    ]

    value_pattern = forms.ChoiceField(
        choices=VALUE_PATTERN_CHOICES,
        widget=forms.RadioSelect
    )
    sensor_module = forms.ModelChoiceField(
        queryset=Modules.objects.all(),
        required=False  # Initially not required
    )

    SENSOR_TYPE_CHOICES = [
        ('lightsensor', 'Light Sensor'),
        ('waterlevel', 'Water Level'),
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('soilmoisture', 'Soil Moisture'),
        ('phvalue', 'pH Value'),
    ]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        farmers = FarmerUserModel.objects.get(pk = request.user.id)
        self.fields['sensor_module'].initial = None
        if self.data.get('value_pattern') == 'Average':
            self.fields['sensor_module'] = forms.ModelChoiceField(
            queryset=farmers.modules.exclude(module_type="AM"),
            empty_label="Select a module",
            required=False  # Set required to False when value pattern is Average
            
        )
            print("false")
        else:
            self.fields['sensor_module'] = forms.ModelChoiceField(
            queryset=farmers.modules.exclude(module_type="AM"),
            empty_label="Select a module",
            required=False # Set required to True when value pattern is Individual
        )
            print("true")
        self.fields['sensor_module'] = forms.ModelChoiceField(
            queryset=farmers.modules.exclude(module_type="AM"),
            empty_label="Select a module",
            required=False
        )
        print(farmers.modules.exclude(module_type="AM"))
        
        self.fields['sensor_type'] = forms.ChoiceField(
        choices=self.SENSOR_TYPE_CHOICES,
        required=True,
    )
    def remove_field(form, field_name):
         print("done")
  

    def clean(self):
        cleaned_data = super().clean()
        value_pattern = cleaned_data.get('value_pattern')
        sensor_module = cleaned_data.get('sensor_module')
        password = cleaned_data.get("password")
        sensor_type = cleaned_data.get('sensor_type')
        print("half")


        if value_pattern == "Average":
            # If a sensor module is selected, set value_pattern to Average and sensor_module to None
            cleaned_data['value_pattern'] = 'Average'
            cleaned_data['sensor_module'] = None
        else:
            
            # If no sensor module is selected, proceed with the original logic
            if value_pattern == 'Individual':
                if not sensor_module:
                    self.add_error('sensor_module', 'This field is required when value pattern is Individual')
                if not password:
                    self.add_error('password', 'Password is required for Individual value pattern')

                # Validate password on related Modules instance
                module = Modules.objects.get(pk=self.request.user.id)
                selected_module = cleaned_data.get("sensor_module")
                if selected_module:
                    if selected_module.password != password:
                        raise forms.ValidationError(f"Password for module '{selected_module.name}' does not match.")

                # Validate sensor_type based on sensor_module
                if sensor_module:
                    if sensor_module.module_type == 'LM':
                        if sensor_type != 'lightsensor':
                            self.add_error('sensor_type', 'Only Light Sensor is allowed for Light Module')
                    elif sensor_module.module_type == 'WM':
                        if sensor_type != 'waterlevel':
                            self.add_error('sensor_type', 'Only Water Level is allowed for Water Module')
                    elif sensor_module.module_type == 'BM':
                        if sensor_type not in ['temperature', 'humidity', 'soilmoisture', 'phvalue']:
                            self.add_error('sensor_type', 'Only Temperature, Humidity, Soil Moisture, and pH Value are allowed for Basic Module')
            elif value_pattern == 'Average':
                # Set sensor_type to 'all' for Average value pattern
                cleaned_data['sensor_type'] = 'all'

        return cleaned_data
    # def get_sensor_type_choices(self):
    #     value_pattern = self.data.get('value_pattern')
    #     sensor_module = self.data.get('sensor_module')
    #     print(value_pattern)
    #     if value_pattern == 'Individual':
    #         if sensor_module == 'BM':
    #             return [
    #                 ('temperature', 'Temperature'),
    #                 ('humidity', 'Humidity'),
    #                 ('phvalue', 'pH Value'),
    #                 ('soilmoisture', 'Soil Moisture'),
    #             ]
    #         elif sensor_module == 'LM':
    #             return [
    #                 ('lightsensor', 'Light Sensor'),
    #             ]
    #         else:
    #             return [
    #                 ('waterlevel', 'Water Level'),
    #             ]
    #     else:
    #         print("done")
            
    #         del self.fields['sensor_module']
    #         return self.SENSOR_TYPE_CHOICES

    class Meta:
        model = AccutatorModules
        fields = ['value_pattern', "sensor_module", 'min_value', "max_value", 'sensor_type']  # include sensor_type in the form