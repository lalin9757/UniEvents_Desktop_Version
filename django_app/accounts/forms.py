from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class StudentRegistrationForm(UserCreationForm):
    """Clean registration form for students only — no user_type field exposed."""
    first_name = forms.CharField(max_length=50, required=False, label='First Name')
    last_name  = forms.CharField(max_length=50, required=False, label='Last Name')
    email      = forms.EmailField(required=False, label='Email')
    student_id = forms.CharField(max_length=20, required=False, label='Student ID')
    intake     = forms.CharField(max_length=20, required=False, label='Intake')
    department = forms.CharField(max_length=100, required=False, label='Department')
    phone      = forms.CharField(max_length=15, required=False, label='Phone')

    class Meta:
        model  = CustomUser
        fields = (
            'first_name', 'last_name', 'username', 'email',
            'student_id', 'intake', 'department', 'phone',
            'password1', 'password2',
        )


# Keep old name as alias so nothing else breaks
CustomUserCreationForm = StudentRegistrationForm


class UserProfileForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone',
                  'profile_picture', 'bio', 'department', 'year')
