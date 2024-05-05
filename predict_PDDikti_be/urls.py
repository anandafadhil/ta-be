from django.urls import path
from .views import *

urlpatterns = [
    # path('', homepage, name='homepage'),
    path('distinct-universities', get_univ_distinct, name='get_univ_distinct'),
    path('univ-name', get_univ_name, name='get_univ_name'),
    path('prodi/<str:id_univ>', get_prodi, name='get_prodi'),
    path('uni-prodi', save_uni_prodi, name='save_uni_prodi'),
    path('get-uni-prodi', get_save_uni_prodi, name='get_save_uni_prodi'),
    path('statistik-prodi/<str:id_prodi>', get_statistik_prodi, name='get_statistik_prodi'),
    path('sks-handle', handle_data_sks, name='handle_data_sks'),
    path('bulk-handle', handle_data_bulk, name='handle_data_bulk'),
    path('bulk-processed', processed_data_bulk, name='processed_data_bulk'),
]