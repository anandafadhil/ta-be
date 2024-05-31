from .models import DaftarProdiPrediksi, StatistikProdiPrediksi, StatistikProdiVisualisasi, DaftarUnivProdiVisualisasi, WilayahUniv
from django.db.models import Sum, Avg, F, FloatField
from django.db.models.functions import Cast
from django.http import response, HttpResponse, JsonResponse
import json, os, joblib
from django.conf import settings

def get_statistik_prodi(id_prodi):
    statistik_prodi=StatistikProdiPrediksi.objects.filter(id_sms=id_prodi).values_list(
        'avg_ipk_sem1', 'avg_ipk_sem2', 'avg_ipk_sem3', 'avg_ipk_sem4', 
        'avg_sks_sem1', 'avg_sks_sem2', 'avg_sks_sem3', 'avg_sks_sem4',
        'avg_skst_sem1', 'avg_skst_sem2', 'avg_skst_sem3', 'avg_skst_sem4', 
        'avg_kenaikan_skst', 'avg_persentase_lulus_tepat_waktu'
    )
    return JsonResponse({'data': list(statistik_prodi)})


def calculate_scores(data, stat_prod):
    IPK_sem_1 = float(data['IPK_sem_1'])
    IPK_sem_2 = float(data['IPK_sem_2'])
    IPK_sem_3 = float(data['IPK_sem_3'])
    IPK_sem_4 = float(data['IPK_sem_4'])
    avg_ipk_sem1, avg_ipk_sem2, avg_ipk_sem3, avg_ipk_sem4 = stat_prod[:4]
    skor_ipk_sem1 = IPK_sem_1 / avg_ipk_sem1
    skor_ipk_sem2 = IPK_sem_2 / avg_ipk_sem2
    skor_ipk_sem3 = IPK_sem_3 / avg_ipk_sem3
    skor_ipk_sem4 = IPK_sem_4 / avg_ipk_sem4

    SKS_sem_1 = float(data['SKS_sem_1'])
    SKS_sem_2 = float(data['SKS_sem_2'])
    SKS_sem_3 = float(data['SKS_sem_3'])
    SKS_sem_4 = float(data['SKS_sem_4'])
    avg_sks_sem1, avg_sks_sem2, avg_sks_sem3, avg_sks_sem4 = stat_prod[4:8]
    skor_sks_sem1 = SKS_sem_1 / avg_sks_sem1
    skor_sks_sem2 = SKS_sem_2 / avg_sks_sem2
    skor_sks_sem3 = SKS_sem_3 / avg_sks_sem3
    skor_sks_sem4 = SKS_sem_4 / avg_sks_sem4

    avg_skst_sem1, avg_skst_sem2, avg_skst_sem3, avg_skst_sem4, avg_kenaikan_skst = stat_prod[8:13]

    skst_sem1 = float(data['SKSL_sem_1'])
    skst_sem2 = skst_sem1 + float(data['SKSL_sem_2'])
    skst_sem3 = skst_sem2 + float(data['SKSL_sem_3'])
    skst_sem4 = skst_sem3 + float(data['SKSL_sem_4'])

    skor_skst_sem1 = skst_sem1 / avg_skst_sem1
    skor_skst_sem2 = skst_sem2 / avg_skst_sem2
    skor_skst_sem3 = skst_sem3 / avg_skst_sem3
    skor_skst_sem4 = skst_sem4 / avg_skst_sem4

    kenaikan_skst = (skst_sem1 + skst_sem2 + skst_sem3 + skst_sem4) / 4.0
    skor_kenaikan_skst = kenaikan_skst / avg_kenaikan_skst

    avg_persentase_lulus_tepat_waktu = stat_prod[13]
    rata_rata_prodi = avg_persentase_lulus_tepat_waktu

    return {
        "skor_ipk_sem1": skor_ipk_sem1,
        "skor_ipk_sem2": skor_ipk_sem2,
        "skor_ipk_sem3": skor_ipk_sem3,
        "skor_ipk_sem4": skor_ipk_sem4,
        "skor_sks_sem1": skor_sks_sem1,
        "skor_sks_sem2": skor_sks_sem2,
        "skor_sks_sem3": skor_sks_sem3,
        "skor_sks_sem4": skor_sks_sem4,
        "skor_skst_sem1": skor_skst_sem1,
        "skor_skst_sem2": skor_skst_sem2,
        "skor_skst_sem3": skor_skst_sem3,
        "skor_skst_sem4": skor_skst_sem4,
        "skor_kenaikan_skst": skor_kenaikan_skst,
        "rata_rata_prodi": rata_rata_prodi
    }

def get_prediction(data):
    model_file_path = os.path.join(settings.BASE_DIR, 'predict_PDDikti_be', 'static', 'predict_PDDikti_be', 'model_files', 'stacking_clf_pipeline_compressed.pkl')
    stacking_clf_loaded = joblib.load(model_file_path)
    y_pred = stacking_clf_loaded.predict(data)
    return y_pred
