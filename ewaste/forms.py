from django import forms
from django.contrib.auth.models import User
from .models import EWasteItem, Feedback, PickupRequest


class UserSignUpForm(forms.ModelForm):
    """Public signup - only customers by default. Company accounts must be granted by an admin."""

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def clean_first_name(self):
        first_name = (self.cleaned_data.get('first_name') or '').strip()
        if first_name and not first_name.isalpha():
            raise forms.ValidationError("First name must contain only alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = (self.cleaned_data.get('last_name') or '').strip()
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only alphabetic characters.")
        return last_name


class EWasteItemForm(forms.ModelForm):
    class Meta:
        model = EWasteItem
        fields = ['category', 'item_name', 'description', 'condition', 'quantity', 
                  'pickup_location', 'preferred_date', 'contact_phone']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Old Laptop'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'pickup_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Address'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit phone number'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your feedback...'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }


class PickupRequestForm(forms.ModelForm):
    class Meta:
        model = PickupRequest
        fields = ['status', 'scheduled_date', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_first_name(self):
        first_name = (self.cleaned_data.get('first_name') or '').strip()
        if first_name and not first_name.isalpha():
            raise forms.ValidationError("First name must contain only alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = (self.cleaned_data.get('last_name') or '').strip()
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only alphabetic characters.")
        return last_name
