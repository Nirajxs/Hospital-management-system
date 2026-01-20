from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Appointment, GalleryImage

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))

    class Meta:
        model = User
        fields = ('username','email','role','password1','password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        user.role = role
        # Patients can login immediately; doctors/staff need admin approval (is_active False)
        if role == User.PATIENT:
            user.is_active = True
        else:
            user.is_active = False
        if commit:
            user.save()
        return user

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor','date','time','symptoms','image')
        widgets = {
            'doctor': forms.Select(attrs={'class':'form-select'}),
            'date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'time': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'symptoms': forms.Textarea(attrs={'class':'form-control','rows':3, 'placeholder': 'Symptoms (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active doctors
        self.fields['doctor'].queryset = User.objects.filter(role=User.DOCTOR, is_active=True)

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ('image','caption')
        widgets = {
            'caption': forms.TextInput(attrs={'class':'form-control','placeholder':'Caption (optional)'})
        }




