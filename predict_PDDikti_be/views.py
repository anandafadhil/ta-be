from django.shortcuts import render
from django.http import response, HttpResponse, JsonResponse
from .models import *
import json, os, joblib
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.db import connection
from django.db.models import Sum, Avg, Value, FloatField, F, IntegerField, CharField, TextField, Case, When
from django.db.models.functions import Cast
from collections import defaultdict
from . import services

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


def get_univ_pred(request):
    distinct_universities = DaftarProdiPrediksi.objects.order_by("nama_univ").values_list('id_univ','nama_univ').distinct()
    return JsonResponse({'distinct_universities': list(distinct_universities)})

def get_prodi(request, id_univ):
    prodi = DaftarProdiPrediksi.objects.filter(id_univ = id_univ).order_by("nama_prodi").values_list("id_prodi", "nama_prodi")
    return JsonResponse({'prodi':list(prodi)})

def get_univ_vis(request):
    distinct_universities = DaftarUnivProdiVisualisasi.objects.order_by("nm_univ").values_list('id_univ','nm_univ').distinct()
    return JsonResponse({'distinct_universities': list(distinct_universities)})

def get_prodi_vis(request, id_univ):
    prodi = DaftarUnivProdiVisualisasi.objects.filter(id_univ = id_univ).order_by("nm_prodi").values_list("id_prodi", "nm_prodi")
    return JsonResponse({'prodi':list(prodi)})

@csrf_exempt
def handle_data_singular(request):
    data = json.loads(request.body)
    id_prodi = data['id']

    # Call the get statistik services
    stat_prod = services.get_statistik_prodi(id_prodi)
    stat_prod_data = stat_prod.content.decode()
    stats_dict = json.loads(stat_prod_data)
    stats = stats_dict['data']

    if not stat_prod_data:
        return JsonResponse({"error": "No statistics found for the provided ID"}, status=404)

    first_stat = stats[0]
    scores = services.calculate_scores(data, first_stat)
    df = pd.DataFrame([scores])
    y_pred_stacking_loaded = services.get_prediction(df)

    if y_pred_stacking_loaded == 1:
        return JsonResponse({"prediction": True})
    else:
        return JsonResponse({"prediction": False})
    
@csrf_exempt
def handle_data_bulk(request):
    data = json.loads(request.body)
    id_prodi = data['id']
    student_data_list = data['data']
    
    # Fetch all required statistics in one query
    stat_prod = services.get_statistik_prodi(id_prodi)
    stat_prod_data = stat_prod.content.decode()
    stats_dict = json.loads(stat_prod_data)
    
    if not stats_dict['data']:
        return JsonResponse({"error": "No statistics found for the provided ID"}, status=404)
    
    first_stat = stats_dict['data'][0]

    processed_data = []
    for student_data in student_data_list:
        NPM = student_data['Identifier_Mahasiswa']
        
        # Call the calculation & prediction services
        scores = services.calculate_scores(student_data, first_stat)
        df = pd.DataFrame([scores])
        y_pred_stacking_loaded = services.get_prediction(df)

        result = "Tepat Waktu" if y_pred_stacking_loaded == 1 else "Tidak Tepat Waktu"
        processed_data.append({"NPM": NPM, "RES": result})
        
    return JsonResponse({"data": processed_data})

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

    # Sort by 'tahun_angkatan'
    query_1.sort(key=lambda x: x['tahun_angkatan'])

    # Print the result
    for row in query_1:
        print(row)
    
def get_avg_grad_time_univ_all(request=None):
    all_time = StatistikProdiVisualisasi.objects.aggregate(
        avg_grad_time=Cast(
            (Sum(F('jml_mhs_lulus35') * 3.5) + 
             Sum(F('jml_mhs_lulus40') * 4.0) + 
             Sum(F('jml_mhs_lulus45') * 4.5) + 
             Sum(F('jml_mhs_lulus50') * 5.0) + 
             Sum(F('jml_mhs_lulus55') * 5.5) + 
             Sum(F('jml_mhs_lulus60') * 6.0)) / 
            Sum(F('jml_mhs_lulus35') + F('jml_mhs_lulus40') + F('jml_mhs_lulus45') + 
                F('jml_mhs_lulus50') + F('jml_mhs_lulus55') + F('jml_mhs_lulus60')),
            output_field=FloatField()
        )
    )

    # Merge results
    results = [{'tahun_angkatan': 'All Time', **all_time}]
    list_selected = []
    for avg_lulus in list(results) :
        year = str(avg_lulus['tahun_angkatan'])
        avg_grad = avg_lulus['avg_grad_time']
        rounded_avg_grad = round(avg_grad, 1)
        if year == "All Time" : 
            list_selected.append({"selected_year": year, "avg_grad":rounded_avg_grad})
            break
        else :
            continue
    print(list_selected)
    return JsonResponse(list_selected, safe=False)

def get_ketepatan_grad_time_univ_all(request=None):
    all_time = StatistikProdiVisualisasi.objects.aggregate(
        avg_grad_time=Cast(
            (Sum(F('jml_mhs_lulus35')) + 
             Sum(F('jml_mhs_lulus40'))) * 1.0 / 
            Sum(F('jml_mhs_lulus35') + F('jml_mhs_lulus40') + F('jml_mhs_lulus45') + 
                F('jml_mhs_lulus50') + F('jml_mhs_lulus55') + F('jml_mhs_lulus60')),
            output_field=FloatField()
        )
    )

    # Merge results
    results = [{'tahun_angkatan': 'All Time', **all_time}]
    list_selected = []
    for avg_lulus in list(results) :
        year = str(avg_lulus['tahun_angkatan'])
        avg_grad = avg_lulus['avg_grad_time']
        rounded_tepat_grad = round(avg_grad, 4)*100
        rounded_tidak_tepat_grad = 100 - rounded_tepat_grad
        if year == "All Time" : 
            list_selected.append({"selected_year": year, "tepat_grad":rounded_tepat_grad, "tidak_tepat_grad": rounded_tidak_tepat_grad})
            break
        else :
            continue
    return JsonResponse(list_selected, safe=False)

def get_prog_grad_time_univ_all(request=None):
    by_year = StatistikProdiVisualisasi.objects.values('tahun_angkatan').annotate(
    avg_grad_time=Cast(
        (Sum(F('jml_mhs_lulus35')) + Sum(F('jml_mhs_lulus40'))) *1.0 / 
        Sum(F('jml_mhs_lulus35') + F('jml_mhs_lulus40') + F('jml_mhs_lulus45') + 
            F('jml_mhs_lulus50') + F('jml_mhs_lulus55') + F('jml_mhs_lulus60')),
        output_field=FloatField()
        )
    ).order_by('tahun_angkatan')


    # Merge results
    results = list(by_year)
    list_selected = []
    for avg_lulus in list(results) :
        year = str(avg_lulus['tahun_angkatan'])
        avg_grad = avg_lulus['avg_grad_time']
        rounded_tepat_grad = round(avg_grad, 4)*100
        rounded_tidak_tepat_grad = round((100 - rounded_tepat_grad), 4)

        if year != "All Time" : 
            list_selected.append({"selected_year": year, "tepat_grad":rounded_tepat_grad, "tidak_tepat_grad": rounded_tidak_tepat_grad})
            
        else :
            continue
    print(list_selected)
    return JsonResponse(list_selected, safe=False)

def get_dist_grad_univ_all(request, year) :
    selected_year = year
    annual_stats = StatistikProdiVisualisasi.objects.values('tahun_angkatan').annotate(
    tahun=Cast('tahun_angkatan', output_field=CharField()),
    jml_mhs_lulus35=Cast(Sum('jml_mhs_lulus35'), output_field=IntegerField()),
    jml_mhs_lulus40=Cast(Sum('jml_mhs_lulus40'), output_field=IntegerField()),
    jml_mhs_lulus45=Cast(Sum('jml_mhs_lulus45'), output_field=IntegerField()),
    jml_mhs_lulus50=Cast(Sum('jml_mhs_lulus50'), output_field=IntegerField()),
    jml_mhs_lulus55=Cast(Sum('jml_mhs_lulus55'), output_field=IntegerField()),
    jml_mhs_lulus60=Cast(Sum('jml_mhs_lulus60'), output_field=IntegerField())
    ).order_by('tahun_angkatan')

    # Convert QuerySet to a list of dicts for further processing
    annual_stats_list = list(annual_stats)

    # Aggregate total for all time
    total_stats = StatistikProdiVisualisasi.objects.aggregate(
        jml_mhs_lulus35=Sum('jml_mhs_lulus35'),
        jml_mhs_lulus40=Sum('jml_mhs_lulus40'),
        jml_mhs_lulus45=Sum('jml_mhs_lulus45'),
        jml_mhs_lulus50=Sum('jml_mhs_lulus50'),
        jml_mhs_lulus55=Sum('jml_mhs_lulus55'),
        jml_mhs_lulus60=Sum('jml_mhs_lulus60')
    )

    # Convert sums to int and add 'All Time' label
    all_time_stats = {
        'tahun': 'All Time',
        **{key: int(value) for key, value in total_stats.items() if value is not None}
    }

    # Combine both lists
    combined_results = annual_stats_list + [all_time_stats]

    list_selected = []
    for res in list(combined_results) :
        tahun = res['tahun']
        jml_mhs_lulus35 = res['jml_mhs_lulus35']
        jml_mhs_lulus40 = res['jml_mhs_lulus40']
        jml_mhs_lulus45 = res['jml_mhs_lulus45']
        jml_mhs_lulus50 = res['jml_mhs_lulus50']
        jml_mhs_lulus55 = res['jml_mhs_lulus55']
        jml_mhs_lulus60 = res['jml_mhs_lulus60']

        if tahun == selected_year : 
            list_selected.append({"selected_year": tahun, "jml_mhs_lulus35":jml_mhs_lulus35, "jml_mhs_lulus40":jml_mhs_lulus40, "jml_mhs_lulus45":jml_mhs_lulus45, "jml_mhs_lulus50":jml_mhs_lulus50, "jml_mhs_lulus55":jml_mhs_lulus55, "jml_mhs_lulus60":jml_mhs_lulus60})
            break
        elif tahun == "All Time" :
            list_selected.append({"selected_year": "All Time", "jml_mhs_lulus35":jml_mhs_lulus35, "jml_mhs_lulus40":jml_mhs_lulus40, "jml_mhs_lulus45":jml_mhs_lulus45, "jml_mhs_lulus50":jml_mhs_lulus50, "jml_mhs_lulus55":jml_mhs_lulus55, "jml_mhs_lulus60":jml_mhs_lulus60})
            break
        else :
            continue

    return JsonResponse(list_selected, safe=False)

def get_geochart(request, year):
    selected_year = year

    # Fetching data with related objects
    statistik_data = StatistikProdiVisualisasi.objects.select_related('id_sms').values(
        'uuid', 'id_sms', 'tahun_angkatan', 'jml_mhs_lulus35', 'jml_mhs_lulus40', 'jml_mhs_lulus45', 'jml_mhs_lulus50', 'jml_mhs_lulus55', 'jml_mhs_lulus60'
    )
    univ_prodi_data = DaftarUnivProdiVisualisasi.objects.values('id_prodi', 'id_univ', 'nm_univ')
    wilayah_data = WilayahUniv.objects.values('id_sp', 'provinsi', 'provinsi_label')

    # Create dictionaries for fast lookups
    univ_prodi_dict = {up['id_prodi']: up for up in univ_prodi_data}
    wilayah_dict = {wu['id_sp']: wu for wu in wilayah_data}

    res = []
    for spv in statistik_data:
        nm_univ = None
        provinsi = None
        provinsi_label = None
        total_lulus35_40 = spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40']
        total_lulus = total_lulus35_40 + spv['jml_mhs_lulus45'] + spv['jml_mhs_lulus50'] + spv['jml_mhs_lulus55'] + spv['jml_mhs_lulus60']
        persentase = float(total_lulus35_40 / total_lulus) if total_lulus > 0 else 0

        # left join dupv
        dupv = univ_prodi_dict.get(spv['id_sms'])
        if dupv:
            nm_univ = dupv['nm_univ']

            # left join wu
            wu = wilayah_dict.get(dupv['id_univ'])
            if wu and wu['provinsi'] is not None:
                provinsi = wu['provinsi']
                provinsi_label = wu['provinsi_label']

                res.append({
                    'uuid': spv['uuid'],
                    'per': persentase,
                    'thn': spv['tahun_angkatan'],
                    'id_sms': spv['id_sms'],
                    'nm_univ': nm_univ,
                    'provinsi': provinsi,
                    'provinsi_label': provinsi_label,
                    'jml_mhs_lulus35': spv['jml_mhs_lulus35'],
                    'jml_mhs_lulus40': spv['jml_mhs_lulus40'],
                    'jml_mhs_lulus45': spv['jml_mhs_lulus45'],
                    'jml_mhs_lulus50': spv['jml_mhs_lulus50'],
                    'jml_mhs_lulus55': spv['jml_mhs_lulus55'],
                    'jml_mhs_lulus60': spv['jml_mhs_lulus60']
                })

    grouped_data = defaultdict(lambda: {
        'jml_mhs_lulus35': 0,
        'jml_mhs_lulus40': 0,
        'jml_mhs_lulus45': 0,
        'jml_mhs_lulus50': 0,
        'jml_mhs_lulus55': 0,
        'jml_mhs_lulus60': 0
    })

    result_all = []
    if selected_year == "All":
        for entry in res:
            key = (entry['provinsi'], entry['provinsi_label'])
            grouped_data[key]['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
            grouped_data[key]['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
            grouped_data[key]['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
            grouped_data[key]['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
            grouped_data[key]['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
            grouped_data[key]['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']

        # Calculate percentage for each group
        for key, counts in grouped_data.items():
            provinsi, provinsi_label = key
            total_lulus35_40 = counts['jml_mhs_lulus35'] + counts['jml_mhs_lulus40']
            total_lulus = total_lulus35_40 + counts['jml_mhs_lulus45'] + counts['jml_mhs_lulus50'] + counts['jml_mhs_lulus55'] + counts['jml_mhs_lulus60']
            persentase = float(total_lulus35_40 / total_lulus) if total_lulus > 0 else 0
            result_all.append({
                'provinsi': provinsi,
                'provinsi_label': provinsi_label,
                'tahun_angkatan': "All Time",
                'persentase': persentase
            })
    else:
        for entry in res:
            key = (entry['provinsi'], entry['provinsi_label'], entry['thn'])
            grouped_data[key]['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
            grouped_data[key]['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
            grouped_data[key]['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
            grouped_data[key]['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
            grouped_data[key]['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
            grouped_data[key]['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']

        for key, counts in grouped_data.items():
            provinsi, provinsi_label, tahun_angkatan = key
            total_lulus35_40 = counts['jml_mhs_lulus35'] + counts['jml_mhs_lulus40']
            total_lulus = total_lulus35_40 + counts['jml_mhs_lulus45'] + counts['jml_mhs_lulus50'] + counts['jml_mhs_lulus55'] + counts['jml_mhs_lulus60']
            persentase = float(total_lulus35_40 / total_lulus) if total_lulus > 0 else 0

            if tahun_angkatan == int(selected_year):
                result_all.append({
                    'provinsi': provinsi,
                    'provinsi_label': provinsi_label,
                    'tahun_angkatan': tahun_angkatan,
                    'persentase': persentase
                })

    return JsonResponse(result_all, safe=False)

def get_univ_info(request, id_univ):
    univ_info = DaftarUnivProdiVisualisasi.objects.filter(id_univ = id_univ).values('id_univ', 'nm_univ', 'tahun_berdiri_univ', 'rank_univ').first()
    wilayah_data = WilayahUniv.objects.values('id_sp', 'provinsi', 'provinsi_label')
    wilayah_dict = {wu['id_sp']: wu for wu in wilayah_data}
    res = []
    wu = wilayah_dict.get(univ_info['id_univ'])
    if wu and wu['provinsi'] is not None:
        provinsi = wu['provinsi']
        provinsi_label = wu['provinsi_label']
    
    else :
        provinsi = "Indonesia"
        provinsi_label = "Indonesia"

    res.append({
        'id_univ': univ_info['id_univ'],
        'nm_univ': univ_info['nm_univ'],
        'thn': univ_info['tahun_berdiri_univ'],
        'rank_univ': univ_info['rank_univ'],
        'provinsi': provinsi,
        'provinsi_label': provinsi_label,
    })
    return JsonResponse(res, safe=False)

def get_avg_grad_time_univ_filter(request, id_univ):
    statistik_data = StatistikProdiVisualisasi.objects.select_related('id_sms').values(
        'uuid', 'id_sms', 'tahun_angkatan', 'jml_mhs_lulus35', 'jml_mhs_lulus40', 'jml_mhs_lulus45', 'jml_mhs_lulus50', 'jml_mhs_lulus55', 'jml_mhs_lulus60'
    )
    univ_prodi_data = DaftarUnivProdiVisualisasi.objects.filter(id_univ=id_univ).values('id_prodi', 'id_univ', 'nm_univ')

    # Create dictionaries for fast lookups
    univ_prodi_dict = {up['id_prodi']: up for up in univ_prodi_data}
    
    res = []
    for spv in statistik_data:
        nm_univ = None
        total_lulus_atas = spv['jml_mhs_lulus35']*3.5 + spv['jml_mhs_lulus40'] *4.0 + spv['jml_mhs_lulus45']*4.5 + spv['jml_mhs_lulus50'] *5.0 + spv['jml_mhs_lulus55']*5.5 + spv['jml_mhs_lulus60'] *6.0
        total_lulus = spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40'] + spv['jml_mhs_lulus45'] + spv['jml_mhs_lulus50'] + spv['jml_mhs_lulus55'] + spv['jml_mhs_lulus60']

        # left join dupv
        dupv = univ_prodi_dict.get(spv['id_sms'])
        if dupv:
            nm_univ = dupv['nm_univ']
            id_univ = dupv['id_univ']
            if id_univ == id_univ :
                res.append({
                    'uuid': spv['uuid'],
                    'thn': spv['tahun_angkatan'],
                    'id_sms': spv['id_sms'],
                    'id_univ': id_univ,
                    'nm_univ': nm_univ,
                    'total_lulus' : total_lulus,
                    'total_lulus_atas': total_lulus_atas,
                    'jml_mhs_lulus35': spv['jml_mhs_lulus35'],
                    'jml_mhs_lulus40': spv['jml_mhs_lulus40'],
                    'jml_mhs_lulus45': spv['jml_mhs_lulus45'],
                    'jml_mhs_lulus50': spv['jml_mhs_lulus50'],
                    'jml_mhs_lulus55': spv['jml_mhs_lulus55'],
                    'jml_mhs_lulus60': spv['jml_mhs_lulus60']
                })
            else :
                continue

        total_aggregate = {
        'jml_mhs_lulus35': 0,
        'jml_mhs_lulus40': 0,
        'jml_mhs_lulus45': 0,
        'jml_mhs_lulus50': 0,
        'jml_mhs_lulus55': 0,
        'jml_mhs_lulus60': 0,
        'total_lulus_atas': 0,
        'total_lulus': 0
        }

    result_all = []
    for entry in res:
        total_aggregate['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
        total_aggregate['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
        total_aggregate['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
        total_aggregate['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
        total_aggregate['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
        total_aggregate['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']
        total_aggregate['total_lulus_atas'] += entry['total_lulus_atas']
        total_aggregate['total_lulus'] += entry['total_lulus']
    
    total_aggregate['persentase'] = float(total_aggregate['total_lulus_atas'] / total_aggregate['total_lulus']) if total_aggregate['total_lulus'] > 0 else 0

    result_all.append({
        'tahun_angkatan': "All Time",
        'persentase': total_aggregate['persentase'],
    })

    return JsonResponse(result_all, safe=False)

def get_prodi_ranking(request, id_univ):
    selected_id = id_univ

    # Fetch statistik data with related prodi data in one query
    statistik_data = StatistikProdiVisualisasi.objects.filter(
        id_sms__in=DaftarUnivProdiVisualisasi.objects.filter(id_univ=selected_id).values('id_prodi')
    ).values(
        'uuid', 'id_sms', 'tahun_angkatan', 'jml_mhs_lulus35', 'jml_mhs_lulus40', 'jml_mhs_lulus45', 'jml_mhs_lulus50', 'jml_mhs_lulus55', 'jml_mhs_lulus60'
    )

    # Fetch related univ prodi data
    univ_prodi_data = DaftarUnivProdiVisualisasi.objects.filter(id_univ=selected_id).values('id_prodi', 'id_univ', 'nm_univ', 'nm_prodi')

    # Create dictionaries for fast lookups
    univ_prodi_dict = {up['id_prodi']: up for up in univ_prodi_data}

    res = []
    for spv in statistik_data:
        total_lulus35_40 = spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40']
        total_lulus = total_lulus35_40 + spv['jml_mhs_lulus45'] + spv['jml_mhs_lulus50'] + spv['jml_mhs_lulus55'] + spv['jml_mhs_lulus60']
        persentase = float(total_lulus35_40 / total_lulus) if total_lulus > 0 else 0

        dupv = univ_prodi_dict.get(spv['id_sms'])
        if dupv:
            res.append({
                'uuid': spv['uuid'],
                'per': persentase,
                'thn': spv['tahun_angkatan'],
                'id_sms': spv['id_sms'],
                'nm_univ': dupv['nm_univ'],
                'id_prodi': dupv['id_prodi'],
                'nm_prodi': dupv['nm_prodi'],
                'jml_mhs_lulus35': spv['jml_mhs_lulus35'],
                'jml_mhs_lulus40': spv['jml_mhs_lulus40'],
                'jml_mhs_lulus45': spv['jml_mhs_lulus45'],
                'jml_mhs_lulus50': spv['jml_mhs_lulus50'],
                'jml_mhs_lulus55': spv['jml_mhs_lulus55'],
                'jml_mhs_lulus60': spv['jml_mhs_lulus60']
            })

    grouped_data = defaultdict(lambda: {
        'jml_mhs_lulus35': 0,
        'jml_mhs_lulus40': 0,
        'jml_mhs_lulus45': 0,
        'jml_mhs_lulus50': 0,
        'jml_mhs_lulus55': 0,
        'jml_mhs_lulus60': 0
    })

    for entry in res:
        key = (entry['id_prodi'], entry['nm_prodi'])
        grouped_data[key]['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
        grouped_data[key]['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
        grouped_data[key]['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
        grouped_data[key]['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
        grouped_data[key]['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
        grouped_data[key]['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']

    result_all = []
    for key, counts in grouped_data.items():
        id_prodi, nm_prodi = key
        total_lulus35_40 = counts['jml_mhs_lulus35'] + counts['jml_mhs_lulus40']
        total_lulus = total_lulus35_40 + counts['jml_mhs_lulus45'] + counts['jml_mhs_lulus50'] + counts['jml_mhs_lulus55'] + counts['jml_mhs_lulus60']
        persentase = float(total_lulus35_40 / total_lulus) if total_lulus > 0 else 0

        result_all.append({
            'id_prodi': id_prodi,
            'nm_prodi': nm_prodi,
            'persentase': persentase
        })

    result_all_sorted = sorted(result_all, key=lambda x: x['persentase'], reverse=True)

    for index, pos in enumerate(result_all_sorted):
        pos['position'] = index + 1

    return JsonResponse(result_all_sorted, safe=False)

def get_dist_grad_univ_filter(request, id_univ, year) :
    selected_id = id_univ
    selected_year = year
    annual_stats = StatistikProdiVisualisasi.objects.values('tahun_angkatan').annotate(
    tahun=Cast('tahun_angkatan', output_field=CharField()),
    id_sms=Cast('id_sms', output_field=TextField()),
    jml_mhs_lulus35=Cast(Sum('jml_mhs_lulus35'), output_field=IntegerField()),
    jml_mhs_lulus40=Cast(Sum('jml_mhs_lulus40'), output_field=IntegerField()),
    jml_mhs_lulus45=Cast(Sum('jml_mhs_lulus45'), output_field=IntegerField()),
    jml_mhs_lulus50=Cast(Sum('jml_mhs_lulus50'), output_field=IntegerField()),
    jml_mhs_lulus55=Cast(Sum('jml_mhs_lulus55'), output_field=IntegerField()),
    jml_mhs_lulus60=Cast(Sum('jml_mhs_lulus60'), output_field=IntegerField())
    ).order_by('tahun_angkatan')

    univ_prodi_data = DaftarUnivProdiVisualisasi.objects.values('id_prodi', 'id_univ', 'nm_univ', 'nm_prodi')
    univ_prodi_dict = {up['id_prodi']: up for up in univ_prodi_data}

    res=[]
    for spv in annual_stats :
        dupv = univ_prodi_dict.get(spv['id_sms'])
        if dupv:
            nm_univ = dupv['nm_univ']
            id_univ = dupv['id_univ']
            nm_prodi = dupv['nm_prodi']
            id_prodi = dupv['id_prodi']
            if id_univ == selected_id: 
                res.append({
                    'thn': spv['tahun_angkatan'],
                    'id_sms': spv['id_sms'],
                    'nm_univ': nm_univ,
                    'id_prodi': id_prodi,
                    'nm_prodi': nm_prodi,
                    'jml_mhs_lulus35': spv['jml_mhs_lulus35'],
                    'jml_mhs_lulus40': spv['jml_mhs_lulus40'],
                    'jml_mhs_lulus45': spv['jml_mhs_lulus45'],
                    'jml_mhs_lulus50': spv['jml_mhs_lulus50'],
                    'jml_mhs_lulus55': spv['jml_mhs_lulus55'],
                    'jml_mhs_lulus60': spv['jml_mhs_lulus60']
                })

    grouped_data = defaultdict(lambda: {
        'jml_mhs_lulus35': 0,
        'jml_mhs_lulus40': 0,
        'jml_mhs_lulus45': 0,
        'jml_mhs_lulus50': 0,
        'jml_mhs_lulus55': 0,
        'jml_mhs_lulus60': 0
    })

    result_year = []
    result_all = []
    total35 = 0
    total40 = 0
    total45 = 0
    total50 = 0
    total55 = 0
    total60 = 0
    for entry in res:
        key = (entry['thn'])
        grouped_data[key]['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
        grouped_data[key]['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
        grouped_data[key]['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
        grouped_data[key]['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
        grouped_data[key]['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
        grouped_data[key]['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']
    
    for key, counts in grouped_data.items():
        tahun_angkatan = key
        total35 += counts['jml_mhs_lulus35']
        total40 += counts['jml_mhs_lulus40']
        total45 += counts['jml_mhs_lulus45']
        total50 += counts['jml_mhs_lulus50']
        total55 += counts['jml_mhs_lulus55']
        total60 += counts['jml_mhs_lulus60']

        if selected_year!= 'All' and tahun_angkatan == int(selected_year):
            result_year.append({
                'tahun_angkatan': tahun_angkatan,
                'jml_mhs_lulus_35': counts['jml_mhs_lulus35'],
                'jml_mhs_lulus_40': counts['jml_mhs_lulus40'],
                'jml_mhs_lulus_45': counts['jml_mhs_lulus45'],
                'jml_mhs_lulus_50': counts['jml_mhs_lulus50'],
                'jml_mhs_lulus_55': counts['jml_mhs_lulus55'],
                'jml_mhs_lulus_60': counts['jml_mhs_lulus60'],
            })
            break
        else :
            continue
        
    result_all.append({
        'tahun_angkatan': "All Time",
        'jml_mhs_lulus_35':total35,
        'jml_mhs_lulus_40':total40,
        'jml_mhs_lulus_45':total45,
        'jml_mhs_lulus_50':total50,
        'jml_mhs_lulus_55':total55,
        'jml_mhs_lulus_60':total60,
    })

    if selected_year == 'All' :
        return JsonResponse(result_all, safe=False)
    else :
        return JsonResponse(result_year, safe=False)

def get_ketepatan_grad_time_univ_filter(request, id_univ):
    selected_id = id_univ
    statistik_data = StatistikProdiVisualisasi.objects.select_related('id_sms').values(
        'uuid', 'id_sms', 'tahun_angkatan', 'jml_mhs_lulus35', 'jml_mhs_lulus40', 'jml_mhs_lulus45', 'jml_mhs_lulus50', 'jml_mhs_lulus55', 'jml_mhs_lulus60'
    )
    univ_prodi_data = DaftarUnivProdiVisualisasi.objects.values('id_prodi', 'id_univ', 'nm_univ', 'nm_prodi')
    univ_prodi_dict = {up['id_prodi']: up for up in univ_prodi_data}
    res=[]
    for spv in statistik_data :
        dupv = univ_prodi_dict.get(spv['id_sms'])
        if dupv:
            nm_univ = dupv['nm_univ']
            id_univ = dupv['id_univ']
            nm_prodi = dupv['nm_prodi']
            id_prodi = dupv['id_prodi']
            total_lulus_atas = (spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40'] )*1.0
            total_lulus = spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40'] + spv['jml_mhs_lulus45'] + spv['jml_mhs_lulus50'] + spv['jml_mhs_lulus55'] + spv['jml_mhs_lulus60']
            if id_univ == selected_id: 
                res.append({
                    'thn': spv['tahun_angkatan'],
                    'id_sms': spv['id_sms'],
                    'nm_univ': nm_univ,
                    'id_prodi': id_prodi,
                    'nm_prodi': nm_prodi,
                    'total_lulus' : total_lulus,
                    'total_lulus_atas': total_lulus_atas,
                    'jml_mhs_lulus35': spv['jml_mhs_lulus35'],
                    'jml_mhs_lulus40': spv['jml_mhs_lulus40'],
                    'jml_mhs_lulus45': spv['jml_mhs_lulus45'],
                    'jml_mhs_lulus50': spv['jml_mhs_lulus50'],
                    'jml_mhs_lulus55': spv['jml_mhs_lulus55'],
                    'jml_mhs_lulus60': spv['jml_mhs_lulus60']
                })


    total_aggregate = {
        'jml_mhs_lulus35': 0,
        'jml_mhs_lulus40': 0,
        'jml_mhs_lulus45': 0,
        'jml_mhs_lulus50': 0,
        'jml_mhs_lulus55': 0,
        'jml_mhs_lulus60': 0,
        'total_lulus_atas': 0,
        'total_lulus': 0
        }
    
    result_all=[]
    for entry in res:
        total_aggregate['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
        total_aggregate['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
        total_aggregate['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
        total_aggregate['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
        total_aggregate['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
        total_aggregate['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']
        total_aggregate['total_lulus_atas'] += entry['total_lulus_atas']
        total_aggregate['total_lulus'] += entry['total_lulus']

    total_aggregate['persentase'] = float(total_aggregate['total_lulus_atas'] / total_aggregate['total_lulus']) if total_aggregate['total_lulus'] > 0 else 0
    result_all.append({
        'tahun_angkatan': "All Time",
        'persentase': total_aggregate['persentase'],
    })
    return JsonResponse(result_all, safe=False)

def get_prog_grad_time_univ_filter(request, id_univ):
    selected_id = id_univ
    statistik_data = StatistikProdiVisualisasi.objects.select_related('id_sms').values(
        'uuid', 'id_sms', 'tahun_angkatan', 'jml_mhs_lulus35', 'jml_mhs_lulus40', 'jml_mhs_lulus45', 'jml_mhs_lulus50', 'jml_mhs_lulus55', 'jml_mhs_lulus60'
    )
    univ_prodi_data = DaftarUnivProdiVisualisasi.objects.values('id_prodi', 'id_univ', 'nm_univ', 'nm_prodi')
    univ_prodi_dict = {up['id_prodi']: up for up in univ_prodi_data}
    res=[]
    res_all=[]
    for spv in statistik_data :
        dupv = univ_prodi_dict.get(spv['id_sms'])
        if dupv:
            nm_univ = dupv['nm_univ']
            id_univ = dupv['id_univ']
            nm_prodi = dupv['nm_prodi']
            id_prodi = dupv['id_prodi']
            total_lulus_atas = (spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40'] )*1.0
            total_lulus = spv['jml_mhs_lulus35'] + spv['jml_mhs_lulus40'] + spv['jml_mhs_lulus45'] + spv['jml_mhs_lulus50'] + spv['jml_mhs_lulus55'] + spv['jml_mhs_lulus60']
            if id_univ == selected_id: 
                res.append({
                    'thn': spv['tahun_angkatan'],
                    'id_sms': spv['id_sms'],
                    'nm_univ': nm_univ,
                    'id_prodi': id_prodi,
                    'nm_prodi': nm_prodi,
                    'total_lulus' : total_lulus,
                    'total_lulus_atas': total_lulus_atas,
                    'jml_mhs_lulus35': spv['jml_mhs_lulus35'],
                    'jml_mhs_lulus40': spv['jml_mhs_lulus40'],
                    'jml_mhs_lulus45': spv['jml_mhs_lulus45'],
                    'jml_mhs_lulus50': spv['jml_mhs_lulus50'],
                    'jml_mhs_lulus55': spv['jml_mhs_lulus55'],
                    'jml_mhs_lulus60': spv['jml_mhs_lulus60']
                })

    grouped_data = defaultdict(lambda: {
        'jml_mhs_lulus35': 0,
        'jml_mhs_lulus40': 0,
        'jml_mhs_lulus45': 0,
        'jml_mhs_lulus50': 0,
        'jml_mhs_lulus55': 0,
        'jml_mhs_lulus60': 0
    })

    for entry in res:
        key = (entry['thn'])
        grouped_data[key]['jml_mhs_lulus35'] += entry['jml_mhs_lulus35']
        grouped_data[key]['jml_mhs_lulus40'] += entry['jml_mhs_lulus40']
        grouped_data[key]['jml_mhs_lulus45'] += entry['jml_mhs_lulus45']
        grouped_data[key]['jml_mhs_lulus50'] += entry['jml_mhs_lulus50']
        grouped_data[key]['jml_mhs_lulus55'] += entry['jml_mhs_lulus55']
        grouped_data[key]['jml_mhs_lulus60'] += entry['jml_mhs_lulus60']
       
    
    for key, counts in grouped_data.items():
        tahun_angkatan = key
        total_lulus_atas = (counts['jml_mhs_lulus35'] + counts['jml_mhs_lulus40'] )*1.0
        total_lulus = counts['jml_mhs_lulus35'] + counts['jml_mhs_lulus40'] + counts['jml_mhs_lulus45'] + counts['jml_mhs_lulus50'] + counts['jml_mhs_lulus55'] + counts['jml_mhs_lulus60']
        persentase = float(total_lulus_atas / total_lulus) if total_lulus > 0 else 0
        res_all.append({
            'tahun_angkatan':tahun_angkatan,
            'persentase':persentase,
        })

    return JsonResponse(res_all, safe=False)

def get_prodi_info(request, id_prodi):
    prodi_info = DaftarUnivProdiVisualisasi.objects.filter(id_prodi = id_prodi).values('nm_univ', 'nm_prodi', 'tahun_berdiri_prodi', 'rank_prodi').first()
    return JsonResponse(prodi_info, safe=False)

def get_avg_ipk(request, id_prodi):
    all_time = StatistikProdiVisualisasi.objects.filter(id_sms=id_prodi).aggregate(
    avg_ipk_overall=Avg(Case(When(avg_ipk_overall__gt=0, then=F('avg_ipk_overall')), default=None)),
    avg_ipk_tepat_waktu=Avg(Case(When(avg_ipk_tepat_waktu__gt=0, then=F('avg_ipk_tepat_waktu')), default=None)),
    avg_ipk_telat=Avg(Case(When(avg_ipk_telat__gt=0, then=F('avg_ipk_telat')), default=None))
    ) 
    results = [{'tahun_angkatan': 'All Time', **all_time}]

    return JsonResponse(results, safe=False)

def get_avg_sks(request, id_prodi):
    all_time = StatistikProdiVisualisasi.objects.filter(
        id_sms=id_prodi
    ).aggregate(
        avg_sks_sem1=Avg(Case(When(avg_sks_sem1__gt=0, then=F('avg_sks_sem1')), default=None)),
        avg_sks_sem2=Avg(Case(When(avg_sks_sem2__gt=0, then=F('avg_sks_sem2')), default=None)),
        avg_sks_sem3=Avg(Case(When(avg_sks_sem3__gt=0, then=F('avg_sks_sem3')), default=None)),
        avg_sks_sem4=Avg(Case(When(avg_sks_sem4__gt=0, then=F('avg_sks_sem4')), default=None)),
        avg_sks_sem5=Avg(Case(When(avg_sks_sem5__gt=0, then=F('avg_sks_sem5')), default=None)),
        avg_sks_sem6=Avg(Case(When(avg_sks_sem6__gt=0, then=F('avg_sks_sem6')), default=None)),
        avg_sks_sem7=Avg(Case(When(avg_sks_sem7__gt=0, then=F('avg_sks_sem7')), default=None)),
        avg_sks_sem8=Avg(Case(When(avg_sks_sem8__gt=0, then=F('avg_sks_sem8')), default=None))
    )

    result = [all_time]


    return JsonResponse(result, safe=False)

def get_avg_grad_time_prodi_filter(request, id_prodi):
    all_time = StatistikProdiVisualisasi.objects.filter(id_sms = id_prodi).aggregate(
        avg_grad_time=Cast(
            (Sum(F('jml_mhs_lulus35') * 3.5) + 
             Sum(F('jml_mhs_lulus40') * 4.0) + 
             Sum(F('jml_mhs_lulus45') * 4.5) + 
             Sum(F('jml_mhs_lulus50') * 5.0) + 
             Sum(F('jml_mhs_lulus55') * 5.5) + 
             Sum(F('jml_mhs_lulus60') * 6.0)) / 
            Sum(F('jml_mhs_lulus35') + F('jml_mhs_lulus40') + F('jml_mhs_lulus45') + 
                F('jml_mhs_lulus50') + F('jml_mhs_lulus55') + F('jml_mhs_lulus60')),
            output_field=FloatField()
        )
    )

    return JsonResponse(all_time, safe=False)

def get_ketepatan_grad_time_prodi_filter(request, id_prodi):
    all_time = StatistikProdiVisualisasi.objects.filter(id_sms = id_prodi).aggregate(
        avg_grad_time=Cast(
            (Sum(F('jml_mhs_lulus35')) + 
             Sum(F('jml_mhs_lulus40'))) * 1.0 / 
            Sum(F('jml_mhs_lulus35') + F('jml_mhs_lulus40') + F('jml_mhs_lulus45') + 
                F('jml_mhs_lulus50') + F('jml_mhs_lulus55') + F('jml_mhs_lulus60')),
            output_field=FloatField()
        )
    )

    return JsonResponse(all_time, safe=False)

def get_prog_grad_time_prodi_filter(request, id_prodi):
    by_year = StatistikProdiVisualisasi.objects.filter(id_sms = id_prodi).values('tahun_angkatan').annotate(
    avg_grad_time=Cast(
        (Sum(F('jml_mhs_lulus35')) + Sum(F('jml_mhs_lulus40'))) *1.0 / 
        Sum(F('jml_mhs_lulus35') + F('jml_mhs_lulus40') + F('jml_mhs_lulus45') + 
            F('jml_mhs_lulus50') + F('jml_mhs_lulus55') + F('jml_mhs_lulus60')),
        output_field=FloatField()
        )
    ).order_by('tahun_angkatan')

    return JsonResponse(list(by_year), safe=False)

def get_dist_grad_prodi_filter(request, id_prodi, year):
    selected_year = year
    annual_stats = StatistikProdiVisualisasi.objects.filter(id_sms = id_prodi).values('tahun_angkatan').annotate(
    tahun=Cast('tahun_angkatan', output_field=CharField()),
    jml_mhs_lulus35=Cast(Sum('jml_mhs_lulus35'), output_field=IntegerField()),
    jml_mhs_lulus40=Cast(Sum('jml_mhs_lulus40'), output_field=IntegerField()),
    jml_mhs_lulus45=Cast(Sum('jml_mhs_lulus45'), output_field=IntegerField()),
    jml_mhs_lulus50=Cast(Sum('jml_mhs_lulus50'), output_field=IntegerField()),
    jml_mhs_lulus55=Cast(Sum('jml_mhs_lulus55'), output_field=IntegerField()),
    jml_mhs_lulus60=Cast(Sum('jml_mhs_lulus60'), output_field=IntegerField())
    ).order_by('tahun_angkatan')

    # Convert QuerySet to a list of dicts for further processing
    annual_stats_list = list(annual_stats)

    # Aggregate total for all time
    total_stats = StatistikProdiVisualisasi.objects.filter(id_sms = id_prodi).aggregate(
        jml_mhs_lulus35=Sum('jml_mhs_lulus35'),
        jml_mhs_lulus40=Sum('jml_mhs_lulus40'),
        jml_mhs_lulus45=Sum('jml_mhs_lulus45'),
        jml_mhs_lulus50=Sum('jml_mhs_lulus50'),
        jml_mhs_lulus55=Sum('jml_mhs_lulus55'),
        jml_mhs_lulus60=Sum('jml_mhs_lulus60')
    )

    # Convert sums to int and add 'All Time' label
    all_time_stats = {
        'tahun': 'All Time',
        **{key: int(value) for key, value in total_stats.items() if value is not None}
    }

    # Combine both lists
    combined_results = annual_stats_list + [all_time_stats]

    list_selected = []
    for res in list(combined_results) :
        year = res['tahun']
        jml_mhs_lulus35 = res['jml_mhs_lulus35']
        jml_mhs_lulus40 = res['jml_mhs_lulus40']
        jml_mhs_lulus45 = res['jml_mhs_lulus45']
        jml_mhs_lulus50 = res['jml_mhs_lulus50']
        jml_mhs_lulus55 = res['jml_mhs_lulus55']
        jml_mhs_lulus60 = res['jml_mhs_lulus60']

        if year == selected_year : 
            list_selected.append({"selected_year": year, "jml_mhs_lulus35":jml_mhs_lulus35, "jml_mhs_lulus40":jml_mhs_lulus40, "jml_mhs_lulus45":jml_mhs_lulus45, "jml_mhs_lulus50":jml_mhs_lulus50, "jml_mhs_lulus55":jml_mhs_lulus55, "jml_mhs_lulus60":jml_mhs_lulus60})
            break
        elif year == "All Time" :
            list_selected.append({"selected_year": "All Time", "jml_mhs_lulus35":jml_mhs_lulus35, "jml_mhs_lulus40":jml_mhs_lulus40, "jml_mhs_lulus45":jml_mhs_lulus45, "jml_mhs_lulus50":jml_mhs_lulus50, "jml_mhs_lulus55":jml_mhs_lulus55, "jml_mhs_lulus60":jml_mhs_lulus60})
            break
        else :
            continue

    return JsonResponse(list_selected, safe=False)

@csrf_exempt
def get_ipk_total(request):
    data = json.loads(request.body)
    IPK_sem_1 = data['IPK_sem_1']
    IPK_sem_2 = data['IPK_sem_2']
    IPK_sem_3 = data['IPK_sem_3']
    IPK_sem_4 = data['IPK_sem_4']
    id_prodi = data['id']

    IPK_sem_1 = float(IPK_sem_1)
    IPK_sem_2 = float(IPK_sem_2)
    IPK_sem_3 = float(IPK_sem_3)
    IPK_sem_4 = float(IPK_sem_4)

    ipk = StatistikProdiPrediksi.objects.filter(id_sms = id_prodi).values("avg_ipk_sem1", "avg_ipk_sem2", "avg_ipk_sem3", "avg_ipk_sem4")
    skor_data_array = [
        {
            "ipk_sem1": IPK_sem_1,
            "ipk_sem2": IPK_sem_2,
            "ipk_sem3": IPK_sem_3,
            "ipk_sem4": IPK_sem_4,
        }
    ]
    new_list = list(ipk) + skor_data_array
    
    return JsonResponse(new_list, safe=False)


@csrf_exempt
def get_sks_total(request):
    data = json.loads(request.body)
    
    SKSL_sem_1 = data['SKSL_sem_1']
    SKSL_sem_2 = data['SKSL_sem_2']
    SKSL_sem_3 = data['SKSL_sem_3']
    SKSL_sem_4 = data['SKSL_sem_4']
    id_prodi = data['id']

    sks = StatistikProdiPrediksi.objects.filter(id_sms = id_prodi).values("avg_skst_sem1", "avg_skst_sem2", "avg_skst_sem3", "avg_skst_sem4")


    # Penjumlahan sks total
    skst_sem1 = int(SKSL_sem_1)
    skst_sem2 = int(SKSL_sem_1) + int(SKSL_sem_2)
    skst_sem3 = int(SKSL_sem_1) + int(SKSL_sem_2) + int(SKSL_sem_3)
    skst_sem4 = int(SKSL_sem_1) + int(SKSL_sem_2) + int(SKSL_sem_3) + int(SKSL_sem_4)

    skor_data_array = [
        {
            "skst_sem1": skst_sem1,
            "skst_sem2": skst_sem2,
            "skst_sem3": skst_sem3,
            "skst_sem4": skst_sem4,
        }
    ]
    new_list = list(sks) + skor_data_array

    print(new_list)
    return JsonResponse(new_list, safe=False)

@csrf_exempt
def get_sks_needed(request):
    data = json.loads(request.body)
    SKSL_sem_1 = data['SKSL_sem_1']
    SKSL_sem_2 = data['SKSL_sem_2']
    SKSL_sem_3 = data['SKSL_sem_3']
    SKSL_sem_4 = data['SKSL_sem_4']

    # Penjumlahan sks total
    skst_sem4 = int(SKSL_sem_1) + int(SKSL_sem_2) + int(SKSL_sem_3) + int(SKSL_sem_4)
    sks_needed = float((144-skst_sem4)/4)

    skor_data_array = [
        {
            "sks_needed": sks_needed,
        }
    ]
    return JsonResponse(skor_data_array, safe=False)

def get_ketepatan_grad_time(request, id_prodi):
    grad_time = StatistikProdiPrediksi.objects.filter(id_sms = id_prodi).values('avg_persentase_lulus_tepat_waktu')
    print(list(grad_time))
    return JsonResponse(list(grad_time), safe=False)

@csrf_exempt
def handle_table_bulk(request):
    data = json.loads(request.body)
    page_size = int(data['pageSize'])
    current_page = int(data['pageNumber'])
    data_list = list(data['data'])

    start_index = (current_page - 1) * page_size
    end_index = start_index + page_size
    
    if page_size == 0 :
        paginated_data = data_list
    else :
        for idx, item in enumerate(data_list, start=1):
            item['number'] = idx

        paginated_data = data_list[start_index:end_index]
    return JsonResponse(paginated_data, safe=False)
    
def select_year(request):
    tahun = StatistikProdiVisualisasi.objects.values('tahun_angkatan').distinct().order_by('tahun_angkatan')
    tahun_list = list(tahun)

    for item in tahun_list:
        item['tahun_angkatan'] = str(item['tahun_angkatan'])
        item['value_tahun'] = str(item['tahun_angkatan'])

    tahun_list.append({
        "tahun_angkatan": "All Time",
        "value_tahun": "All"
    })
    return JsonResponse(tahun_list, safe=False)

def get_total_univ(request):
    univ = DaftarUnivProdiVisualisasi.objects.values('id_univ').distinct().count()
    return JsonResponse(univ, safe=False)

def get_total_prodi(request):
    prodi = DaftarUnivProdiVisualisasi.objects.values('id_prodi').distinct().count()
    return JsonResponse(prodi, safe=False)