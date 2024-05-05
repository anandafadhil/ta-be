from django.shortcuts import render
from django.http import response, HttpResponse, JsonResponse
from .models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers


# def homepage(request):
#     univ_name_distinct = DaftarProdiPrediksi.objects.values_list('nama_univ', flat=True).distinct()
#     return JsonResponse({'distinct_universities': list(univ_name_distinct)})

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
    statistik_prodi = StatistikProdiPrediksi.objects.filter(id_sms=id_prodi).values_list('avg_ips_sem1', 'avg_ips_sem2', 'avg_ips_sem3', 'avg_ips_sem4', 'avg_ipk_sem1', 
                                                                                         'avg_ipk_sem2', 'avg_ipk_sem3', 'avg_ipk_sem4', 'avg_sks_sem1', 'avg_sks_sem2', 
                                                                                         'avg_sks_sem3', 'avg_sks_sem4', 'avg_skst_sem1', 'avg_skst_sem2', 'avg_skst_sem3', 
                                                                                         'avg_skst_sem4', 'avg_kenaikan_skst', 'avg_persentase_lulus_tepat_waktu')
    return JsonResponse({'data': list(statistik_prodi)})

# @csrf_exempt
# def handle_data_sks(request):
#     data = json.loads(request.body)
#     # print("data", data)
#     SKS_sem_1 = data['sem1sksSemester']
#     SKST_sem_1 = data['sem1sksDPO']
#     IPK_sem_1 = data['sem1ipsKumulatif']
#     SKS_sem_2 = data['sem2sksSemester']
#     SKST_sem_2 = data['sem2sksDPO']
#     IPK_sem_2 = data['sem2ipsKumulatif']
#     SKS_sem_3 = data['sem3sksSemester']
#     SKST_sem_3 = data['sem3sksDPO']
#     IPK_sem_3 = data['sem3ipsKumulatif']
#     SKS_sem_4 = data['sem4sksSemester']
#     SKST_sem_4 = data['sem4sksDPO']
#     IPK_sem_4 = data['sem4ipsKumulatif']
#     id_prodi = data['id']
#     print("id", id_prodi)
#     stat_prod = get_statistik_prodi(id_prodi=id_prodi)
#     # stat_prod_data = stat_prod.json()['data']
#     print("stat", list(stat_prod))

#     #pengolahan data
#     """
#     declare:
#     skstotalsem1 = sem1sksDPO
#     skstotalsem2 = sem1sksDPO + sem2sksDPO
#     ...
#     skstotalsem4 = ...
    
#     ---------------------------------------
#     tabel:
#     sem1ipsKumulatif/avg_ips_sem1
#     sem1sksSemester/avg_sks_sem1
#     ...
#     sem4ipsKumulatif/avg_ips_sem4
#     sem4sksSemester/avg_sks_sem4

#     skstotalsem1 / avg_skst_sem1
#     ...
#     skstotalsem4 / avg_skst_sem4

#     avg(sem1sksDPO ... sem4sksDPO)/avg_kenaikan_skst

#     avg_persentase_lulus_tepat_waktu
#     """
#     return JsonResponse({"message": "SUCCESS"})

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
    print("id", id_prodi)

    stat_prod = get_statistik_prodi(id_prodi=id_prodi)

    stat_prod_data = stat_prod.content.decode()
    # Assuming 'stat_prod_data' contains a 'data' key that has the stats dictionary
    stats_dict = json.loads(stat_prod_data)
    print("stat", stats_dict)

    # Access the 'data' key to get the statistics
    IPK_sem_1 = float(IPK_sem_1)
    stats = stats_dict['data']
    first_stat = stats[0]
    avg_ipk_sem1 = first_stat[4]
    skor_ipk_sem1 = IPK_sem_1 / avg_ipk_sem1
    # skor_ipk_sem2 = IPK_sem_2 / stats['avg_ipk_sem2']
    # skor_ipk_sem3 = IPK_sem_3 / stats['avg_ipk_sem3']
    # skor_ipk_sem4 = IPK_sem_4 / stats['avg_ipk_sem4']

    # skor_sks_sem1 = SKS_sem_1 / stats['avg_sks_sem1']
    # skor_sks_sem2 = SKS_sem_2 / stats['avg_sks_sem2']
    # skor_sks_sem3 = SKS_sem_3 / stats['avg_sks_sem3']
    # skor_sks_sem4 = SKS_sem_4 / stats['avg_sks_sem4']

    # skst_sem1 = SKSL_sem_1
    # skst_sem2 = SKSL_sem_1 + SKSL_sem_2
    # skst_sem3 = SKSL_sem_1 + SKSL_sem_2 + SKSL_sem_3
    # skst_sem4 = SKSL_sem_1 + SKSL_sem_2 + SKSL_sem_3 + SKSL_sem_4
    # skor_skst_sem1 = skst_sem1 / stats['avg_skst_sem1']
    # skor_skst_sem2 = skst_sem2 / stats['avg_skst_sem2']
    # skor_skst_sem3 = skst_sem3 / stats['avg_skst_sem3']
    # skor_skst_sem4 = skst_sem4 / stats['avg_skst_sem4']

    # kenaikan_skst = (skst_sem1 + skst_sem2 + skst_sem3 + skst_sem4) / 4.0
    # skor_kenaikan_skst = kenaikan_skst / stats['avg_kenaikan_skst']

    # rata_rata_prodi = stats['avg_persentase_lulus_tepat_waktu']

    print("skor", skor_ipk_sem1)

    return JsonResponse({"message": "SUCCESS"})

@csrf_exempt
def handle_data_bulk(request):
    data = json.loads(request.body)
    # print(data)
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
            'SKST_sem_1': student['SKST_sem_1'],
            'SKST_sem_2': student['SKST_sem_2'],
            'SKST_sem_3': student['SKST_sem_3'],
            'SKST_sem_4': student['SKST_sem_4'],
        }
        students_data.append(student_data)

        """
        PROCESSING DATA HERE
        MODEL
        """
    print("ceK", list(students_data))
    return JsonResponse({"data": students_data})

def processed_data_bulk(request):
    students_data = request.session.get('processed_data')
    print("AAAA", students_data)
    if students_data is not None:
        print('aaa')
        return JsonResponse({"data": students_data})
    else:
        return JsonResponse({"error": "No data founddd"}, status=404)


