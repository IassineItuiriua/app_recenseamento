# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
# =====================================================
#   REGISTO / CADASTRO DE USUÁRIO /LOGIN POR EMAIL
# =====================================================

# usuarios/forms.py

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True, "class": "form-control"})
    )

    def clean(self):
        email = self.cleaned_data.get('username')  # username é email
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Por favor introduza o email e password corretos.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data



# =====================================================
#   COMPLETAR PERFIL BÁSICO DO USUÁRIO
# =====================================================
class CompletarPerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "telefone",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "telefone",
            "password1",
            "password2",
        )

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe uma conta com este email.")
        return email