from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm as DjangoPasswordChangeForm

from users.models import UserProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации с дополнительными полями"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'})
    )

    referral_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        initial=''
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизуем поля
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Обработка реферального кода
        referral_code = self.cleaned_data.get('referral_code')
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                user.referred_by = referrer
            except User.DoesNotExist:
                pass

        if commit:
            user.save()
            # Создаем профиль
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', '')
            )
        return user


class LoginForm(forms.Form):
    """Форма входа"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя или Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


User = get_user_model()


class UserUpdateForm(UserChangeForm):
    """Форма обновления данных пользователя"""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем поле пароля
        self.fields.pop('password', None)
        # Стилизуем поля
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления профиля"""

    class Meta:
        model = UserProfile
        fields = ['phone', 'birth_date', 'address', 'city', 'postal_code',
                  'avatar', 'level', 'email_notifications', 'sms_notifications']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (___) ___-__-__'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Почтовый индекс'
            }),
            'level': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизуем остальные поля
        for field_name in ['email_notifications', 'sms_notifications']:
            self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Форма смены пароля с кастомизацией"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизуем поля
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')

        return password2