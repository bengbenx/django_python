from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, View
from .forms import MyUserCreationForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from .models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def dashboard(request):
    return render(request,'account/dashboard.html',
            {'section':'dashboard'})

class UserRegistrationView(CreateView):
    template_name='account/user_form.html'
    form_class=MyUserCreationForm

    def form_valid(self,form):
        self.username=form.instance.username
        return super().form_valid(form)
    
    def get_success_url(self):
        user_model=get_user_model()
        user=user_model.objects.get(username=self.username)
        login(self.request,user)
        return reverse_lazy('account:dashboard')

class ProfileUpdateView(LoginRequiredMixin,View):
    template_name='account/profile_form.html'

    def get(self,request,*args,**kwargs):
        user=self.request.user
        context={}
        context['user_form']=UserUpdateForm(instance=user)

        try:
            context['profile_form']=ProfileUpdateForm(instance=user.profile)
        except:
            context['profile_form']=ProfileUpdateForm()
        
        return render(request,self.template_name,context=context)

    def post(self,request,*args,**kwargs):
        user_form=UserUpdateForm(instance=request.user,
                    data=request.POST)

        try:
            profile_form=ProfileUpdateForm(instance=request.user.profile,
                            data=request.POST,
                            files=request.FILES)
        except:
            profile_form=ProfileUpdateForm(data=request.POST,
                            files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.instance.user=request.user
            profile_form.save()

        return redirect(reverse_lazy('account:profile_update'))