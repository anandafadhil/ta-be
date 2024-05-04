from django.urls import path
from .views import *

urlpatterns = [
    # path('', homepage, name='homepage'),
    path('distinct-universities/', get_univ_distinct, name='get_univ_distinct'),
    path('get-prodi/', get_prodi_name, name='get_prodi_name'),
        path('prodi/', get_prodi, name='get_prodi'),
]