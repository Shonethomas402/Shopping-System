from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile 

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password.")
        return cleaned_data


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    location = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        if len(username) > 15:
            raise forms.ValidationError("Username must be 15 characters or fewer.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
    
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']
      
# forms.py
from django import forms
from .models import DeliveryAddress

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['name', 'house_no', 'address', 'place', 'pin']
# class ProfileUpdateForm(forms.ModelForm):
#   class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email', 'phone no', 'location']
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)

    class Meta:
        model = Profile
        fields = ['location', 'phone_no', 'username']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        
        if self.user:
            # Set initial values for username and email from the User model
            self.fields['email'].initial = self.user.email
            self.fields['username'].initial = self.user.username

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')
        if len(phone_no) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_no

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if len(location) > 15:
            raise forms.ValidationError("Location must not exceed 15 characters.")
        return location

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update the associated User model's fields (username and email)
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()  # Save the User model changes
        if commit:
            profile.save()  # Save the Profile model changes
        return profile
