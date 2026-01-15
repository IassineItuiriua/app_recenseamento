from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


# 🔐 FORMULÁRIO DE LOGIN POR EMAIL
class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Senha"})
    )


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
