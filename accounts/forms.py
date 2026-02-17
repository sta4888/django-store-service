from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class ReferralRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        }),
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        }),
        label='Фамилия'
    )
    middle_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Отчество (если есть)'
        }),
        label='Отчество'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label='Email'
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Введите корректный номер телефона')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        }),
        label='Телефон'
    )
    passport_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Номер паспорта'
        }),
        label='Номер паспорта'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        }),
        label='Подтверждение пароля'
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Я согласен на обработку персональных данных'
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'middle_name',
            'email', 'phone', 'passport_number'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Пользователь с таким телефоном уже существует')
        return phone

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, referrer=None, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_terms_accepted = self.cleaned_data["terms_accepted"]
        user.referrer = referrer

        if commit:
            user.save()
            # Обновляем статистику реферера
            if referrer:
                referrer.total_referrals += 1
                referrer.active_referrals += 1
                referrer.save()

        return user


class EmailVerificationForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите 6-значный код',
            'maxlength': '6'
        }),
        label='Код подтверждения'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not self.user:
            raise forms.ValidationError('Пользователь не найден')

        if not self.user.email_verification_code:
            raise forms.ValidationError('Код подтверждения не был отправлен')

        if self.user.is_verification_code_expired():
            raise forms.ValidationError('Срок действия кода истек. Запросите новый код.')

        if code != self.user.email_verification_code:
            raise forms.ValidationError('Неверный код подтверждения')

        return code


class LoginForm(AuthenticationForm):  # Наследуем от AuthenticationForm
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID пользователя или Email'
        }),
        label='ID или Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Пробуем найти по user_id
            try:
                user = CustomUser.objects.get(user_id=username)
                cleaned_data['username'] = user.username  # Меняем username на фактический логин
            except CustomUser.DoesNotExist:
                # Пробуем найти по email
                try:
                    user = CustomUser.objects.get(email=username)
                    cleaned_data['username'] = user.username  # Меняем username на фактический логин
                except CustomUser.DoesNotExist:
                    # Оставляем как есть - пробуем авторизоваться напрямую
                    pass

        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    """Форма запроса на восстановление пароля"""
    user_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш ID'
        }),
        label="ID пользователя"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        }),
        label="Email"
    )

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        email = cleaned_data.get('email')

        if user_id and email:
            try:
                user = CustomUser.objects.get(user_id=user_id, email=email)
                # Сохраняем пользователя для использования в представлении
                self.user = user
            except CustomUser.DoesNotExist:
                raise ValidationError("Пользователь с таким ID и email не найден.")
        return cleaned_data


class PasswordResetConfirmForm(forms.Form):
    """Форма подтверждения кода и установки нового пароля"""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите 6-значный код',
            'pattern': '[0-9]{6}',
            'maxlength': '6'
        }),
        label="Код подтверждения"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль'
        }),
        label="Новый пароль"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        }),
        label="Подтверждение пароля"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Пароли не совпадают.")

        # Проверка сложности пароля
        if new_password and len(new_password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов.")

        return cleaned_data



class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите ваш email",
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email не найден")

        return email