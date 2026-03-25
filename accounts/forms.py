"""Accounts forms — user registration with password confirmation."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    """Extended registration form that captures email."""

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}))
    first_name = forms.CharField(
        max_length=50, required=True, widget=forms.TextInput(attrs={"placeholder": "First name"})
    )
    last_name = forms.CharField(
        max_length=50, required=False, widget=forms.TextInput(attrs={"placeholder": "Last name"})
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
