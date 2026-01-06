from django.urls import path
from . import views
app_name = "recenseamento"
urlpatterns = [
    path('recensear/', views.RecenseamentoView.as_view(), name='recensear'),
]