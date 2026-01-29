from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    ordering = ("email",)

    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações pessoais", {
            "fields": ("first_name", "last_name", "telefone", "nim")
        }),
        ("Permissões", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Datas importantes", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "telefone",
                "nim",
                "password1",
                "password2",
            ),
        }),
    )

    # 🔥 ISTO É O PULO DO GATO
    add_form_template = None



# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser


# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser

#     ordering = ("email",)

#     list_display = ("email", "first_name", "last_name", "is_staff")
#     search_fields = ("email", "first_name", "last_name")

#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Informações pessoais", {"fields": ("first_name", "last_name", "telefone")}),
#         ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
#         ("Datas importantes", {"fields": ("last_login", "date_joined")}),
#     )

#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "first_name", "last_name", "telefone", "password1", "password2"),
#         }),
#     )
