from django import forms
from .models import Comment
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Submit

class EmailPostForm(forms.Form):
    name=forms.CharField(max_length=50)
    email=forms.EmailField()
    to=forms.EmailField()
    comments=forms.CharField(required=False,widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model =Comment
        fields =('name','email','body')

class SearchForm(forms.Form):
    query=forms.CharField()

class ReferenceForm(forms.Form):
    title=forms.CharField(max_length=250)
    description=forms.CharField(required=False,widget=forms.Textarea)
    link=forms.URLField()