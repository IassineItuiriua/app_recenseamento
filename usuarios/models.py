from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email deve ser fornecido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # removemos username
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    nim = models.CharField(max_length=20, unique=True, blank=True, null=True)

    USERNAME_FIELD = "email"   # login agora é pelo email
    REQUIRED_FIELDS = []        # sem campos obrigatórios extras

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.nim}"




# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     username = None  # 🔥 remove completamente
#     email = models.EmailField(unique=True)
#     telefone = models.CharField(max_length=20, blank=True, null=True)
#     nim = models.CharField(max_length=20, unique=True, blank=True, null=True)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = []
