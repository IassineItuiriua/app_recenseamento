from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import authenticate


User = get_user_model()


from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email"
        })
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Senha"
        })
    )

    def clean(self):
        # 1️⃣ Executa validações base do Django
        cleaned_data = super().clean()

        email = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(
                self.request,
                username=email,   # 🔥 email tratado como username
                password=password
            )

            if user is None:
                raise forms.ValidationError(
                    "Credenciais inválidas — tente novamente."
                )

            # 2️⃣ Obrigatório para o AuthenticationForm
            self.confirm_login_allowed(user)

            # 3️⃣ Cache interno do Django
            self.user_cache = user

        return cleaned_data



# 🧾 REGISTO DE USUÁRIO
class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas não coincidem.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        if commit:
            user.save()
        return user


# 👤 COMPLETAR PERFIL
class CompletarPerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class EmailPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        return User.objects.filter(email__iexact=email, is_active=True)
