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
    path('bulk-handle/<str:id_prodi>', handle_data_bulk, name='handle_data_bulk'),
    path('bulk-processed', processed_data_bulk, name='processed_data_bulk'),
    path('get-prediction', get_prediction, name='get_prediction'),
    path('get-avg-grad-time-univ-all', get_avg_grad_time_univ_all, name='get_avg_grad_time_univ_all'),
    path('get-ketepatan-grad-time-univ-all', get_ketepatan_grad_time_univ_all, name='get_ketepatan_grad_time_univ_all'),
    path('get-prog-grad-time-univ-all', get_prog_grad_time_univ_all, name='get_prog_grad_time_univ_all'),
    path('get-dist-grad-univ-all/<str:selected_year_fe>', get_dist_grad_univ_all, name='get_dist_grad_univ_all'),

]