from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.documents_list,              name='documents_list'),
    path('generar/',                    views.generate_document,           name='generate_document'),
    path('<int:pk>/descargar/',         views.download_document,           name='download_document'),
    path('<int:pk>/previsualizar/',     views.preview_document,            name='preview_document'),
    path('<int:pk>/eliminar/',          views.delete_document,             name='delete_document'),
    path('ia/generar-texto/',           views.ai_generate_document_text,   name='ai_generate_document_text'),
]
