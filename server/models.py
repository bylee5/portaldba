from django.db import models
from datetime import datetime

class Server(models.Model):
	created_at = models.DateTimeField(default=datetime.now) # 생성일
	updated_at = models.DateTimeField(default=datetime.now) # 변경일
	dbtype = models.CharField(max_length=100) # DB종류|MySQL,MSSQL
	dbenv = models.CharField(max_length=100) # DB환경|Live,Stg,Dev,QA
	dbservice = models.CharField(max_length=100) # DB서비스|스크린, 버디스쿼드
	dbsvr = models.CharField(max_length=100) # DB서버명
	dbver = models.CharField(max_length=100) # DB버전
	usg = models.CharField(max_length=100) # 용도
	vip = models.CharField(max_length=100) # 가상 ip
	pri_ip = models.CharField(max_length=100) # 사설 ip
	pub_ip = models.CharField(max_length=100) # 공용 ip
	port1 = models.IntegerField() # 포트 번호
	priority = models.CharField(max_length=100) # 분류
	audit_yn = models.CharField(max_length=100) # 감사 로그 여부
	manager1 = models.CharField(max_length=100) # 정
	manager2 = models.CharField(max_length=100) # 부
	url = models.CharField(blank=True, max_length=500, default='') # url -- 지라 혹은 위키
	delete_yn = models.CharField(blank=True, max_length=100, default='N') # 삭제여부		-- N/Y
	deleted_at = models.DateTimeField(null=True) # 삭제조치일
	delete_reason = models.CharField(null=True, blank=True, max_length=100, default='') # 삭제사유
	delete_note = models.CharField(null=True, blank=True, max_length=100, default='') # 삭제비고

	class Meta:
		db_table = 'server_list'

	def __str__(self):
		return self.dbsvr
