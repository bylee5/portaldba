from django.db import models

class ServerList(models.Model):
    id = models.SmallAutoField(primary_key=True)
    dbsvr = models.CharField(max_length=30, blank=True, null=True)
    usg = models.CharField(max_length=100, blank=True, null=True)
    port1 = models.PositiveSmallIntegerField(blank=True, null=True)
    pri_ip = models.CharField(max_length=15, blank=True, null=True)
    pub_ip = models.CharField(max_length=15, blank=True, null=True)
    priority = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'server_list'
        unique_together = (('pri_ip', 'port1'), ('dbsvr', 'port1'),)
        app_label = 'portaldba'

class JobInfo(models.Model):
    job_info_seqno = models.AutoField(primary_key=True)
    job_info_name = models.CharField(max_length=150)
    job_info_detail = models.CharField(max_length=300, blank=True, null=True)
    job_info_note = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_info'
        app_label = 'portaldba'

class JobServerMap(models.Model):
    job_server_map_seqno = models.BigAutoField(primary_key=True)
    job_info_seqno = models.PositiveIntegerField()
    server_list_seqno = models.PositiveSmallIntegerField()
    use_yn = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'job_server_map'
        unique_together = (('job_info_seqno', 'server_list_seqno'),)
        app_label = 'portaldba'
