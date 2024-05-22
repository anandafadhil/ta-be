from django.db import models
import uuid


class DaftarProdiPrediksi(models.Model):
    id_univ = models.TextField(blank=True, null=True)
    nama_univ = models.TextField(blank=True, null=True)
    id_prodi = models.TextField(primary_key=True)
    nama_prodi = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daftar_prodi_prediksi'


class DaftarUnivProdiVisualisasi(models.Model):
    id_univ = models.TextField(blank=True, null=True)
    nm_univ = models.TextField(blank=True, null=True)
    tahun_berdiri_univ = models.BigIntegerField(blank=True, null=True)
    rank_univ = models.BigIntegerField(blank=True, null=True)
    id_prodi = models.TextField(primary_key=True)
    nm_prodi = models.TextField(blank=True, null=True)
    tahun_berdiri_prodi = models.BigIntegerField(blank=True, null=True)
    rank_prodi = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daftar_univ_prodi_visualisasi'


class StatistikProdiPrediksi(models.Model):
    id_sms = models.TextField(primary_key=True)
    avg_ips_sem1 = models.FloatField(blank=True, null=True)
    avg_ips_sem2 = models.FloatField(blank=True, null=True)
    avg_ips_sem3 = models.FloatField(blank=True, null=True)
    avg_ips_sem4 = models.FloatField(blank=True, null=True)
    avg_ipk_sem1 = models.FloatField(blank=True, null=True)
    avg_ipk_sem2 = models.FloatField(blank=True, null=True)
    avg_ipk_sem3 = models.FloatField(blank=True, null=True)
    avg_ipk_sem4 = models.FloatField(blank=True, null=True)
    avg_sks_sem1 = models.FloatField(blank=True, null=True)
    avg_sks_sem2 = models.FloatField(blank=True, null=True)
    avg_sks_sem3 = models.FloatField(blank=True, null=True)
    avg_sks_sem4 = models.FloatField(blank=True, null=True)
    avg_skst_sem1 = models.FloatField(blank=True, null=True)
    avg_skst_sem2 = models.FloatField(blank=True, null=True)
    avg_skst_sem3 = models.FloatField(blank=True, null=True)
    avg_skst_sem4 = models.FloatField(blank=True, null=True)
    avg_kenaikan_skst = models.FloatField(blank=True, null=True)
    avg_persentase_lulus_tepat_waktu = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'statistik_prodi_prediksi'


class StatistikProdiVisualisasi(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_sms = models.TextField(blank=True, null=True)
    tahun_angkatan = models.BigIntegerField(blank=True, null=True)
    jml_mhs_lulus35 = models.BigIntegerField(blank=True, null=True)
    jml_mhs_lulus40 = models.BigIntegerField(blank=True, null=True)
    jml_mhs_lulus45 = models.BigIntegerField(blank=True, null=True)
    jml_mhs_lulus50 = models.BigIntegerField(blank=True, null=True)
    jml_mhs_lulus55 = models.BigIntegerField(blank=True, null=True)
    jml_mhs_lulus60 = models.BigIntegerField(blank=True, null=True)
    avg_sks_sem1 = models.FloatField(blank=True, null=True)
    avg_sks_sem2 = models.FloatField(blank=True, null=True)
    avg_sks_sem3 = models.FloatField(blank=True, null=True)
    avg_sks_sem4 = models.FloatField(blank=True, null=True)
    avg_sks_sem5 = models.FloatField(blank=True, null=True)
    avg_sks_sem6 = models.FloatField(blank=True, null=True)
    avg_sks_sem7 = models.FloatField(blank=True, null=True)
    avg_sks_sem8 = models.FloatField(blank=True, null=True)
    avg_ipk_overall = models.FloatField(blank=True, null=True)
    avg_ipk_tepat_waktu = models.FloatField(blank=True, null=True)
    avg_ipk_telat = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'statistik_prodi_visualisasi'


class WilayahUniv(models.Model):
    # id_sp = models.OneToOneField(DaftarUnivProdiVisualisasi, on_delete=models.CASCADE, primary_key=True, db_column='id_sp')
    id_sp = models.TextField(primary_key=True)
    provinsi = models.TextField(blank=True, null=True)
    provinsi_label = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wilayah_univ'

class SavedUniProdi(models.Model):
    id_univ = models.TextField(blank=True, null=True)
    nama_univ = models.TextField(blank=True, null=True)
    id_prodi = models.TextField(primary_key=True)
    nama_prodi = models.TextField(blank=True, null=True)