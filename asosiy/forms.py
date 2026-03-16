from django import forms
from .models import Profil
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profil



class ProfilOzgertirishForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Username')
    email = forms.EmailField(label='Email')
    country = forms.CharField(max_length=100, label='Country', required=False) # CharFieldga o'zgartirildi

    class Meta:
        model = Profil
        fields = ['username', 'email', 'country', 'img']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['country'].initial = self.instance.country

    def save(self, commit=True):
        profil = super().save(commit=False)
        if commit:
            if profil.user:
                profil.user.username = self.cleaned_data['username']
                profil.user.email = self.cleaned_data['email']
                profil.user.save()
            profil.country = self.cleaned_data['country']
            profil.save()
        return profil



class FoydalanuvchiRoYXatgaOlishForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profil = Profil(user=user, country=self.cleaned_data.get('davlat'), img=self.cleaned_data.get('rasm'))
            profil.save()
        return user