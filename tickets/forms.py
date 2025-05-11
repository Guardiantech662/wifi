from django import forms
from .models import MikroTikRouter, AccessTicket, Plan

class MikroTikRouterForm(forms.ModelForm):
    class Meta:
        model = MikroTikRouter
        fields = ['name', 'ip_address', 'username', 'password', 'api_port']

class AccessTicketForm(forms.Form):
    plan = forms.ModelChoiceField(queryset=Plan.objects.all(), label="Choose Plan")
    duration_months = forms.IntegerField(min_value=1, label="Duration in months")

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'bandwidth_limit', 'price', 'duration_months']



#this for the user creation
from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': '+224XXXXXXXX',
                'class': 'form-control'
            })
        }


# this for is for the user signup creating user
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    phone_number = forms.CharField(max_length=20, label="Phone Number")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Create or update user profile
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'phone_number': self.cleaned_data['phone_number']}
            )
        return user
