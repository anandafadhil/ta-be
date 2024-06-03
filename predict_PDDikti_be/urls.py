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
    path('predict', handle_data_singular, name='handle_data_singular'), #endpoint ganti /predict
    path('predict-bulk', handle_data_bulk, name='handle_data_bulk'), #endpoint ganti /predict-bulk

    # All Stat
    path('select-year', select_year, name='select_year'),
    path('total-univ', get_total_univ, name='get_total_univ'), #endpoint ganti /total-univ
    path('total-prodi', get_total_prodi, name='get_total_prodi'), #endpoint ganti /total-prodi

    path('average-grad-time', get_avg_grad_time_univ_all, name='get_avg_grad_time_univ_all'), #endpoint ganti /average-grad-time
    path('grad-timeliness', get_ketepatan_grad_time_univ_all, name='get_ketepatan_grad_time_univ_all'), #endpoint ganti /grad-timeliness
    path('grad-progression', get_prog_grad_time_univ_all, name='get_prog_grad_time_univ_all'), #endpoint ganti /grad-progression
    path('grad-distribution/<str:year>', get_dist_grad_univ_all, name='get_dist_grad_univ_all'), #endpoint ganti /grad-time-distribution/{year}
    path('geochart/<str:year>', get_geochart, name='get_geochart'), #endpoint ganti /geochart/{year}

    # Univ Stat
    path('univ-information/<str:id_univ>', get_univ_info, name='get_univ_info'), #endpoint ganti /univ-information/{id_univ}
    path('average-grad-time-univ/<str:id_univ>', get_avg_grad_time_univ_filter, name='get_avg_grad_time_univ_filter'), #endpoint ganti /average-grad-time-univ/{id_univ}
    path('prodi-ranking/<str:id_univ>', get_prodi_ranking, name='get_prodi_ranking'), #endpont ganti /prodi-ranking/{id_univ}
    path('grad-time-distribution-univ/<str:id_univ>/<str:year>', get_dist_grad_univ_filter, name='get_dist_grad_univ_filter'), #/grad-time-distribution-univ/{id_univ}/{year}
    path('grad-timeliness-univ/<str:id_univ>', get_ketepatan_grad_time_univ_filter, name='get_ketepatan_grad_time_univ_filter'), #/grad-timeliness-univ/{id_univ}
    path('grad-progression-univ/<str:id_univ>', get_prog_grad_time_univ_filter, name='get_prog_grad_time_univ_filter'), #/grad-progression-univ/{id_univ}

    # Prodi Stat
    path('prodi-information/<str:id_prodi>', get_prodi_info, name='get_prodi_info'), #/prodi-information/{id_prodi}
    path('avg-ipk/<str:id_prodi>', get_avg_ipk, name='get_avg_ipk'), #/avg-ipk/{id_prodi}
    path('avg-sks/<str:id_prodi>', get_avg_sks, name='get_avg_sks'), #/avg-sks/{id_prodi}
    path('average-grad-time-prodi/<str:id_prodi>', get_avg_grad_time_prodi_filter, name='get_avg_grad_time_prodi_filter'), #/average-grad-time-prodi/{id_prodi} 
    path('grad-timeliness-prodi/<str:id_prodi>', get_ketepatan_grad_time_prodi_filter, name='get_ketepatan_grad_time_prodi_filter'), #/grad-timeliness-prodi/{id_prodi} 
    path('grad-progression-prodi/<str:id_prodi>', get_prog_grad_time_prodi_filter, name='get_prog_grad_time_prodi_filter'), #/grad-progression-prodi/{id_prodi}
    path('grad-time-distribution-prodi/<str:id_prodi>/<str:year>', get_dist_grad_prodi_filter, name='get_dist_grad_prodi_filter'), #/grad-time-distribution-prodi/{id_prodi}/{year}

    # Predict Singular
    path('total-ipk', get_ipk_total, name='get_ipk_total'), #/total-ipk
    path('total-sks', get_sks_total, name='get_sks_total'), #/total-sks
    path('sks-needed', get_sks_needed, name='get_sks_needed'), #/sks-needed
    path('get-ketepatan-grad-time/<str:id_prodi>', get_ketepatan_grad_time, name='get_ketepatan_grad_time'),
    
    # Predict Bulk
    path('handle-table-bulk', handle_table_bulk, name='handle_table_bulk'),

]