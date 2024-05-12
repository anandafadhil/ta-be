from django.shortcuts import render
from django.http import response, HttpResponse, JsonResponse
from .models import *
import json, os, joblib
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.db.models import Sum
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from django.conf import settings


def get_univ_distinct(request):
    univ_name_distinct = DaftarProdiPrediksi.objects.values_list('nama_univ', flat=True).distinct()
    return JsonResponse({'distinct_universities': list(univ_name_distinct)})

def get_univ_name(request):
    distinct_universities = DaftarProdiPrediksi.objects.order_by("nama_univ").values_list('id_univ','nama_univ').distinct()
    return JsonResponse({'distinct_universities': list(distinct_universities)})

def get_prodi(request, id_univ):
    prodi = DaftarProdiPrediksi.objects.filter(id_univ = id_univ).order_by("nama_prodi").values_list("id_prodi", "nama_prodi")
    return JsonResponse({'prodi':list(prodi)})

@csrf_exempt
def save_uni_prodi(request):
    deserialize = json.loads(request.body)
    temp_save = SavedUniProdi(id_univ=deserialize['univInputID'], nama_univ=deserialize['univInput'], id_prodi=deserialize['prodiInputID'], nama_prodi=deserialize['prodiInput'])
    temp_save.save()
    return JsonResponse({'message': 'Complain created successfully'})

def get_save_uni_prodi(request):
    data = SavedUniProdi.objects.all().values_list('id_univ','nama_univ', 'id_prodi', 'nama_prodi').distinct()
    # serialized_data = serializers.serialize('json', data)
    return JsonResponse({'data': list(data)})

def get_statistik_prodi(request=None, id_prodi=None):
    # id_prodi = '9F235AF5-D21C-4901-988C-74201EE4A2DB'
    statistik_prodi = StatistikProdiPrediksi.objects.filter(id_sms=id_prodi).values_list('avg_ipk_sem1', 'avg_ipk_sem2', 'avg_ipk_sem3', 'avg_ipk_sem4', 'avg_sks_sem1', 
                                                                                         'avg_sks_sem2', 'avg_sks_sem3', 'avg_sks_sem4', 'avg_skst_sem1', 'avg_skst_sem2', 
                                                                                         'avg_skst_sem3', 'avg_skst_sem4', 'avg_kenaikan_skst', 'avg_persentase_lulus_tepat_waktu')
    return JsonResponse({'data': list(statistik_prodi)})

def get_prediction(y_pred_stacking_loaded):
    # Process the prediction result here
    # For example, you can return a specific message based on the prediction
    if y_pred_stacking_loaded == 1:
        print('yes')
        return JsonResponse({"prediction": True})
    else:
        print('ga')
        return JsonResponse({"prediction": False})
    
@csrf_exempt
def handle_data_sks(request):
    data = json.loads(request.body)
    
    SKS_sem_1 = data['sem1sksSemester']
    SKSL_sem_1 = data['sem1sksDPO']
    IPK_sem_1 = data['sem1ipsKumulatif']

    SKS_sem_2 = data['sem2sksSemester']
    SKSL_sem_2 = data['sem2sksDPO']
    IPK_sem_2 = data['sem2ipsKumulatif']

    SKS_sem_3 = data['sem3sksSemester']
    SKSL_sem_3 = data['sem3sksDPO']
    IPK_sem_3 = data['sem3ipsKumulatif']

    SKS_sem_4 = data['sem4sksSemester']
    SKSL_sem_4 = data['sem4sksDPO']
    IPK_sem_4 = data['sem4ipsKumulatif']

    id_prodi = data['id']

    stat_prod = get_statistik_prodi(id_prodi=id_prodi)
    stat_prod_data = stat_prod.content.decode()
    # Assuming 'stat_prod_data' contains a 'data' key that has the stats dictionary
    stats_dict = json.loads(stat_prod_data)
    stats = stats_dict['data']
    first_stat = stats[0]
    # Get and decode average data from get_statistik_prodi
    IPK_sem_1 = float(IPK_sem_1)
    IPK_sem_2 = float(IPK_sem_2)
    IPK_sem_3 = float(IPK_sem_3)
    IPK_sem_4 = float(IPK_sem_4)
    avg_ipk_sem1, avg_ipk_sem2, avg_ipk_sem3, avg_ipk_sem4 = first_stat[:4]
    skor_ipk_sem1 = IPK_sem_1 / avg_ipk_sem1
    skor_ipk_sem2 = IPK_sem_2 / avg_ipk_sem2
    skor_ipk_sem3 = IPK_sem_3 / avg_ipk_sem3
    skor_ipk_sem4 = IPK_sem_4 / avg_ipk_sem4
    
    SKS_sem_1 = float(SKS_sem_1)
    SKS_sem_2 = float(SKS_sem_2)
    SKS_sem_3 = float(SKS_sem_3)
    SKS_sem_4 = float(SKS_sem_4)
    avg_sks_sem1, avg_sks_sem2, avg_sks_sem3, avg_sks_sem4 = first_stat[4:8]
    skor_sks_sem1 = SKS_sem_1 / avg_sks_sem1
    skor_sks_sem2 = SKS_sem_2 / avg_sks_sem2
    skor_sks_sem3 = SKS_sem_3 / avg_sks_sem3
    skor_sks_sem4 = SKS_sem_4 / avg_sks_sem4

    # Declaring avg_skst pos
    avg_skst_sem1, avg_skst_sem2, avg_skst_sem3, avg_skst_sem4, avg_kenaikan_skst = first_stat[8:13]

    # Penjumlahan sks total
    skst_sem1 = SKSL_sem_1
    skst_sem2 = SKSL_sem_1 + SKSL_sem_2
    skst_sem3 = SKSL_sem_1 + SKSL_sem_2 + SKSL_sem_3
    skst_sem4 = SKSL_sem_1 + SKSL_sem_2 + SKSL_sem_3 + SKSL_sem_4

    skst_sem1 = float(skst_sem1)
    skst_sem2 = float(skst_sem2)
    skst_sem3 = float(skst_sem3)
    skst_sem4 = float(skst_sem4)
    skor_skst_sem1 = skst_sem1 / avg_skst_sem1
    skor_skst_sem2 = skst_sem2 / avg_skst_sem2
    skor_skst_sem3 = skst_sem3 / avg_skst_sem3
    skor_skst_sem4 = skst_sem4 / avg_skst_sem4

    kenaikan_skst = (skst_sem1 + skst_sem2 + skst_sem3 + skst_sem4) / 4.0
    skor_kenaikan_skst = float(kenaikan_skst) / avg_kenaikan_skst

    avg_persentase_lulus_tepat_waktu = first_stat[13]
    rata_rata_prodi = avg_persentase_lulus_tepat_waktu

    skor_data_array = [
        {
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
            "rata_rata_prodi": rata_rata_prodi,
        }
    ]


    df = pd.DataFrame(skor_data_array)
    model_file_path = os.path.join(settings.BASE_DIR, 'predict_PDDikti_be', 'static', 'predict_PDDikti_be', 'model_files', 'stacking_classifier_model_fix.h5')
    stacking_clf_loaded = joblib.load(model_file_path)
    y_pred_stacking_loaded = stacking_clf_loaded.predict(df)

    print("RES", y_pred_stacking_loaded)
    if y_pred_stacking_loaded == 1:
        print('yes')
        return JsonResponse({"prediction": True})
    else:
        print('ga')
        return JsonResponse({"prediction": False})
    # return prediction_result
    # return JsonResponse({"message": prediction_result})

@csrf_exempt
def handle_data_bulk(request, id_prodi):
    data = json.loads(request.body)
    print(data)
    print(id_prodi)
    students_data = []
    for student in data['data']:
        student_data = {
            'NPM': student['NPM'],
            'IPK_sem_1': student['IPK_sem_1'],
            'IPK_sem_2': student['IPK_sem_2'],
            'IPK_sem_3': student['IPK_sem_3'],
            'IPK_sem_4': student['IPK_sem_4'],
            'SKS_sem_1': student['SKS_sem_1'],
            'SKS_sem_2': student['SKS_sem_2'],
            'SKS_sem_3': student['SKS_sem_3'],
            'SKS_sem_4': student['SKS_sem_4'],
            'SKSL_sem_1': student['SKSL_sem_1'],
            'SKSL_sem_2': student['SKSL_sem_2'],
            'SKSL_sem_3': student['SKSL_sem_3'],
            'SKSL_sem_4': student['SKSL_sem_4'],
        }
        students_data.append(student_data)

        """
        PROCESSING DATA HERE
        MODEL
        """
    print("ceK", list(students_data))
    print("data1", len(students_data))
    processed_data = []
    for splitted_stud in students_data :
        SKS_sem_1 = splitted_stud['SKS_sem_1']
        SKSL_sem_1 = splitted_stud['SKSL_sem_1']
        IPK_sem_1 = splitted_stud['IPK_sem_1']

        SKS_sem_2 = splitted_stud['SKS_sem_2']
        SKSL_sem_2 = splitted_stud['SKSL_sem_2']
        IPK_sem_2 = splitted_stud['IPK_sem_2']

        SKS_sem_3 = splitted_stud['SKS_sem_3']
        SKSL_sem_3 = splitted_stud['SKSL_sem_3']
        IPK_sem_3 = splitted_stud['IPK_sem_3']

        SKS_sem_4 = splitted_stud['SKS_sem_4']
        SKSL_sem_4 = splitted_stud['SKSL_sem_4']
        IPK_sem_4 = splitted_stud['IPK_sem_4']

        NPM = splitted_stud['NPM']


        # handling prodi data
        stat_prod = get_statistik_prodi(id_prodi=id_prodi)
        stat_prod_data = stat_prod.content.decode()
        # Assuming 'stat_prod_data' contains a 'data' key that has the stats dictionary
        stats_dict = json.loads(stat_prod_data)
        stats = stats_dict['data']
        first_stat = stats[0]
        
        
        IPK_sem_1 = float(IPK_sem_1)
        IPK_sem_2 = float(IPK_sem_2)
        IPK_sem_3 = float(IPK_sem_3)
        IPK_sem_4 = float(IPK_sem_4)
        avg_ipk_sem1, avg_ipk_sem2, avg_ipk_sem3, avg_ipk_sem4 = first_stat[:4]
        skor_ipk_sem1 = IPK_sem_1 / avg_ipk_sem1
        skor_ipk_sem2 = IPK_sem_2 / avg_ipk_sem2
        skor_ipk_sem3 = IPK_sem_3 / avg_ipk_sem3
        skor_ipk_sem4 = IPK_sem_4 / avg_ipk_sem4
        
        SKS_sem_1 = float(SKS_sem_1)
        SKS_sem_2 = float(SKS_sem_2)
        SKS_sem_3 = float(SKS_sem_3)
        SKS_sem_4 = float(SKS_sem_4)
        avg_sks_sem1, avg_sks_sem2, avg_sks_sem3, avg_sks_sem4 = first_stat[4:8]
        skor_sks_sem1 = SKS_sem_1 / avg_sks_sem1
        skor_sks_sem2 = SKS_sem_2 / avg_sks_sem2
        skor_sks_sem3 = SKS_sem_3 / avg_sks_sem3
        skor_sks_sem4 = SKS_sem_4 / avg_sks_sem4

        # Declaring avg_skst pos
        avg_skst_sem1, avg_skst_sem2, avg_skst_sem3, avg_skst_sem4, avg_kenaikan_skst = first_stat[8:13]

        # Penjumlahan sks total
        skst_sem1 = SKSL_sem_1
        skst_sem2 = SKSL_sem_1 + SKSL_sem_2
        skst_sem3 = SKSL_sem_1 + SKSL_sem_2 + SKSL_sem_3
        skst_sem4 = SKSL_sem_1 + SKSL_sem_2 + SKSL_sem_3 + SKSL_sem_4

        skst_sem1 = float(skst_sem1)
        skst_sem2 = float(skst_sem2)
        skst_sem3 = float(skst_sem3)
        skst_sem4 = float(skst_sem4)
        skor_skst_sem1 = skst_sem1 / avg_skst_sem1
        skor_skst_sem2 = skst_sem2 / avg_skst_sem2
        skor_skst_sem3 = skst_sem3 / avg_skst_sem3
        skor_skst_sem4 = skst_sem4 / avg_skst_sem4

        kenaikan_skst = (skst_sem1 + skst_sem2 + skst_sem3 + skst_sem4) / 4.0
        skor_kenaikan_skst = float(kenaikan_skst) / avg_kenaikan_skst

        avg_persentase_lulus_tepat_waktu = first_stat[13]
        rata_rata_prodi = avg_persentase_lulus_tepat_waktu

        skor_data_array = [
            {
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
                "rata_rata_prodi": rata_rata_prodi,
            }
        ]


        df = pd.DataFrame(skor_data_array)
        model_file_path = os.path.join(settings.BASE_DIR, 'predict_PDDikti_be', 'static', 'predict_PDDikti_be', 'model_files', 'stacking_classifier_model_fix.h5')
        stacking_clf_loaded = joblib.load(model_file_path)
        y_pred_stacking_loaded = stacking_clf_loaded.predict(df)

        if y_pred_stacking_loaded == 1:
            result = "Tepat Waktu"
            processed_data.append({"NPM": NPM, "RES":result})
        else:
            result = "Tidak Tepat Waktu"
            processed_data.append({"NPM": NPM, "RES":result})
        
        print("RES", processed_data)
    return JsonResponse({"data": processed_data})

def processed_data_bulk(request):
    students_data = request.session.get('processed_data')
    print("AAAA", students_data)
    if students_data is not None:
        print('aaa')
        return JsonResponse({"data": students_data})
    else:
        return JsonResponse({"error": "No data founddd"}, status=404)

def get_statistik_lulus_tahun(request):
    # Define your query
    query_1 = StatistikProdiVisualisasi.objects \
        .values('tahun_angkatan') \
        .annotate(
            jml_mhs_lulus35=Sum('jml_mhs_lulus35'),
            jml_mhs_lulus40=Sum('jml_mhs_lulus40'),
            jml_mhs_lulus45=Sum('jml_mhs_lulus45'),
            jml_mhs_lulus50=Sum('jml_mhs_lulus50'),
            jml_mhs_lulus55=Sum('jml_mhs_lulus55'),
            jml_mhs_lulus60=Sum('jml_mhs_lulus60')
        )

    # Aggregate the total for all years
    all_time_total = StatistikProdiVisualisasi.objects \
        .aggregate(
            jml_mhs_lulus35=Sum('jml_mhs_lulus35'),
            jml_mhs_lulus40=Sum('jml_mhs_lulus40'),
            jml_mhs_lulus45=Sum('jml_mhs_lulus45'),
            jml_mhs_lulus50=Sum('jml_mhs_lulus50'),
            jml_mhs_lulus55=Sum('jml_mhs_lulus55'),
            jml_mhs_lulus60=Sum('jml_mhs_lulus60')
        )

    # Append 'All Time' record to the queryset
    query_1 = list(query_1)
    query_1.append({
        'tahun_angkatan': 'All Time',
        **all_time_total
    })

    # Sort the result by 'tahun_angkatan'
    query_1.sort(key=lambda x: x['tahun_angkatan'])

    # Print the result
    for row in query_1:
        print(row)
    

