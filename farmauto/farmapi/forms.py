from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import FarmerUserModel, Modules

class RegisterationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = FarmerUserModel
        fields = ['username', 'email' , 'phone_number' , 'password1' , 'password2']

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