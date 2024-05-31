from django.urls import path
from .views import *

urlpatterns = [
    # Get univ + prodi predict
    path('univ-predict', get_univ_pred, name='get_univ_pred'),
    path('prodi-predict/<str:id_univ>', get_prodi, name='get_prodi'),
    
    # Get univ + prodi visual
    path('univ-vis', get_univ_vis, name='get_univ_vis'),
    path('prodi-vis/<str:id_univ>', get_prodi_vis, name='get_prodi_vis'),

    # Predict 
    path('sks-handle', handle_data_singular, name='handle_data_singular'), #endpoint ganti /predict
    path('bulk-handle', handle_data_bulk, name='handle_data_bulk'), #endpoint ganti /predict-bulk

    # All Stat
    path('select-year', select_year, name='select_year'),
    path('get-total-univ', get_total_univ, name='get_total_univ'), #endpoint ganti /total-univ
    path('get-total-prodi', get_total_prodi, name='get_total_prodi'), #endpoint ganti /total-prodi

    path('get-avg-grad-time-univ-all', get_avg_grad_time_univ_all, name='get_avg_grad_time_univ_all'), #endpoint ganti /average-grad-time
    path('get-ketepatan-grad-time-univ-all', get_ketepatan_grad_time_univ_all, name='get_ketepatan_grad_time_univ_all'), #endpoint ganti /grad-timeliness
    path('get-prog-grad-time-univ-all', get_prog_grad_time_univ_all, name='get_prog_grad_time_univ_all'), #endpoint ganti /grad-progression
    path('get-dist-grad-univ-all/<str:selected_year_fe>', get_dist_grad_univ_all, name='get_dist_grad_univ_all'), #endpoint ganti /grad-time-distribution/{year}
    path('get-geochart/<str:selected_year_fe>', get_geochart, name='get_geochart'), #endpoint ganti /geochart/{year}

    # Univ Stat
    path('get-univ-info/<str:id_univ>', get_univ_info, name='get_univ_info'), #endpoint ganti /univ-information/{id_univ}
    path('get-avg-grad-time-univ-filter/<str:id_univ>', get_avg_grad_time_univ_filter, name='get_avg_grad_time_univ_filter'), #endpoint ganti /average-grad-time-univ/{id_univ}
    path('get-prodi-ranking/<str:selected_id_univ>', get_prodi_ranking, name='get_prodi_ranking'), #endpont ganti /prodi-ranking/{id_univ}
    path('get-dist-grad-univ-filter/<str:selected_id_univ>/<str:selected_year_fe>', get_dist_grad_univ_filter, name='get_dist_grad_univ_filter'), #/grad-time-distribution-univ/{id_univ}/{year}
    path('get-ketepatan-grad-time-univ-filter/<str:selected_id_univ>', get_ketepatan_grad_time_univ_filter, name='get_ketepatan_grad_time_univ_filter'), #/grad-timeliness-univ/{id_univ}
    path('get-prog-grad-time-univ-filter/<str:selected_id_univ>', get_prog_grad_time_univ_filter, name='get_prog_grad_time_univ_filter'), #/grad-progression-univ/{id_univ}

    # Prodi Stat
    path('get-prodi-info/<str:id_prodi>', get_prodi_info, name='get_prodi_info'), #/prodi-information/{id_prodi}
    path('get-avg-ipk/<str:id_prodi>', get_avg_ipk, name='get_avg_ipk'), #/avg-ipk/{id_prodi}
    path('get-avg-sks/<str:id_prodi>', get_avg_sks, name='get_avg_sks'), #/avg-sks/{id_prodi}
    path('get-avg-grad-time-prodi-filter/<str:id_prodi>', get_avg_grad_time_prodi_filter, name='get_avg_grad_time_prodi_filter'), #/average-grad-time-prodi/{id_prodi} 
    path('get-ketepatan-grad-time-filter-prodi/<str:id_prodi>', get_ketepatan_grad_time_prodi_filter, name='get_ketepatan_grad_time_prodi_filter'), #/grad-timeliness-prodi/{id_prodi} 
    path('get-prog-grad-time-prodi-filter/<str:id_prodi>', get_prog_grad_time_prodi_filter, name='get_prog_grad_time_prodi_filter'), #/grad-progression-prodi/{id_prodi}
    path('get-dist-grad-prodi-filter/<str:id_prodi>/<str:selected_year>', get_dist_grad_prodi_filter, name='get_dist_grad_prodi_filter'), #/grad-time-distribution-prodi/{id_prodi}/{year}

    # Predict Singular
    path('get-ipk-total', get_ipk_total, name='get_ipk_total'), #/total-ipk
    path('get-sks-total', get_sks_total, name='get_sks_total'), #/total-sks
    path('get-sks-needed', get_sks_needed, name='get_sks_needed'), #/sks-needed
    path('get-ketepatan-grad-time/<str:id_prodi>', get_ketepatan_grad_time, name='get_ketepatan_grad_time'),
    
    # Predict Bulk
    path('handle-table-bulk', handle_table_bulk, name='handle_table_bulk'),

]