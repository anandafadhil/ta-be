from django.shortcuts import render
from django.http import response, HttpResponse, JsonResponse
from .models import *

# def homepage(request):
#     univ_name_distinct = DaftarProdiPrediksi.objects.values_list('nama_univ', flat=True).distinct()
#     return JsonResponse({'distinct_universities': list(univ_name_distinct)})

def get_univ_distinct(request):
    univ_name_distinct = DaftarProdiPrediksi.objects.values_list('nama_univ', flat=True).distinct()
    return JsonResponse({'distinct_universities': list(univ_name_distinct)})

def get_prodi_name(request):
    distinct_universities = DaftarUnivProdiVisualisasi.objects.values_list('nm_univ', flat=True).distinct()
    return JsonResponse({'distinct_universities': list(distinct_universities)})

def get_prodi(request):
    id_u = '0D1E63E9-CBFB-4546-A242-875C310083A5'
    prodi = DaftarUnivProdiVisualisasi.objects.filter(id_univ = id_u).order_by("nm_prodi").values_list("nm_prodi", flat=True)
    return JsonResponse({'prodi':list(prodi)})
