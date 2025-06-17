from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Answer, Profile, Question 
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Profile
        fields = ['image']
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    def save(self):
        user = super().save()
        user.set_password(self.cleaned_data.get('password'))
        user.save()
class AskForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text="Enter tags separated by commas")

    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        return [tag.strip() for tag in tags.split(',') if tag.strip()]
    
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'avatar': self.cleaned_data['avatar']} if self.cleaned_data['avatar'] else {}
            )
            if not created and self.cleaned_data['avatar']:
                profile.avatar = self.cleaned_data['avatar']
                profile.save()
        return user
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
    
    nickname = forms.CharField(required=False)
    avatar = forms.ImageField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'profile'):
            self.fields['nickname'].initial = self.instance.profile.nickname
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.nickname = self.cleaned_data['nickname']
        if self.cleaned_data['avatar']:
            profile.avatar = self.cleaned_data['avatar']
        profile.save()
        return user
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Enter your answer here'}),
        }
