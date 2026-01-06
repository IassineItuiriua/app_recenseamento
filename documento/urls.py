# documento/urls.py
from django.urls import path
from . import views

app_name = "documento"

urlpatterns = [
    path('solicitar/', views.SolicitarDocumentoView.as_view(), name='solicitar_documento'),
    path('visualizar/<int:documento_id>/', views.VisualizarDocumentoView.as_view(), name='visualizar_documento'),
    path('gerar_documento/<int:documento_id>/', views.GerarDocumentoView.as_view(), name='gerar_documento'),
    path('baixar_pdf/<int:documento_id>/', views.BaixarPDFDocumentoView.as_view(), name='baixar_pdf_documento'),
    path('documento/confirmar_exame/<int:pessoa_id>/', views.ConfirmarExameView.as_view(), name="confirmar_exame"),
]
