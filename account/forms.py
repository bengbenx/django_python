from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm, DateInput
from .models import Profile

class MyUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        fields=('username','first_name','last_name','email')

class MyDateInput(DateInput):
    input_type='date'

class UserUpdateForm(ModelForm):
    class Meta:
        model=get_user_model()
        fields=('first_name','last_name','email')

class ProfileUpdateForm(ModelForm):
    class Meta:
        model=Profile
        fields=('date_of_birth','photo')
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['date_of_birth'].widget=MyDateInput()