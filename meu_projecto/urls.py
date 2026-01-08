from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf.urls.static import static

def home(request):
    return render(request, "index.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # ← adiciona esta linha
    path('usuarios/', include('usuarios.urls')),
    path('recenseamento/', include('recenseamento.urls')),
    path('documento/', include('documento.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)