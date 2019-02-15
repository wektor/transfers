from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from sharing.models import SharedUrl, SharedLink, SharedFile


# class SharedUrlForm(forms.ModelForm):
#     class Meta:
#         model = SharedUrl
#         fields = '__all__'
#
#     password = forms.CharField(widget=forms.PasswordInput())
#
#     def clean_password(self):
#         # is pass valid
#         passwd = self.cleaned_data['password']
#         validate_password(passwd)
#         return make_password(passwd)

class SharedLinkForm(forms.ModelForm):
    class Meta:
        model = SharedLink
        fields = ['link']


class SharedFileForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = ['file']


class OpenUrlForm(forms.ModelForm):
    class Meta:
        model = SharedUrl
        fields = ['password']

    password = forms.CharField(widget=forms.PasswordInput())
