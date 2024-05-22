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
    path('get-prediction', get_prediction, name='get_prediction'),
    path('get-avg-grad-time-univ-all', get_avg_grad_time_univ_all, name='get_avg_grad_time_univ_all'),
    path('get-ketepatan-grad-time-univ-all', get_ketepatan_grad_time_univ_all, name='get_ketepatan_grad_time_univ_all'),
    path('get-prog-grad-time-univ-all', get_prog_grad_time_univ_all, name='get_prog_grad_time_univ_all'),
    path('get-dist-grad-univ-all/<str:selected_year_fe>', get_dist_grad_univ_all, name='get_dist_grad_univ_all'),
    path('get-geochart/<str:selected_year_fe>', get_geochart, name='get_geochart'),

    # Univ Stat
    path('get-univ-info/<str:id_univ>', get_univ_info, name='get_univ_info'),
    path('get-avg-grad-time-univ-filter/<str:id_univ>', get_avg_grad_time_univ_filter, name='get_avg_grad_time_univ_filter'),
    path('get-prodi-ranking/<str:selected_id_univ>', get_prodi_ranking, name='get_prodi_ranking'),
    path('get-dist-grad-univ-filter/<str:selected_id_univ>/<str:selected_year_fe>', get_dist_grad_univ_filter, name='get_dist_grad_univ_filter'),
    path('get-ketepatan-grad-time-univ-filter/<str:selected_id_univ>', get_ketepatan_grad_time_univ_filter, name='get_ketepatan_grad_time_univ_filter'),
    path('get-prog-grad-time-univ-filter/<str:selected_id_univ>', get_prog_grad_time_univ_filter, name='get_prog_grad_time_univ_filter'),

    # Prodi stat
    path('get-prodi-info/<str:id_prodi>', get_prodi_info, name='get_prodi_info'),
    path('get-avg-ipk/<str:id_prodi>', get_avg_ipk, name='get_avg_ipk'),
    path('get-avg-sks/<str:id_prodi>', get_avg_sks, name='get_avg_sks'),
    path('get-avg-grad-time-prodi-filter/<str:id_prodi>', get_avg_grad_time_prodi_filter, name='get_avg_grad_time_prodi_filter'),
    path('get-ketepatan-grad-time-filter-prodi/<str:id_prodi>', get_ketepatan_grad_time_prodi_filter, name='get_ketepatan_grad_time_prodi_filter'),
    path('get-prog-grad-time-prodi-filter/<str:id_prodi>', get_prog_grad_time_prodi_filter, name='get_prog_grad_time_prodi_filter'),
    path('get-dist-grad-prodi-filter/<str:id_prodi>/<str:selected_year>', get_dist_grad_prodi_filter, name='get_dist_grad_prodi_filter'),

    # path('test', test, name='test'),
]