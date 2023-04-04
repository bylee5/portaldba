from django.db import models
from datetime import datetime

class Server(models.Model):
	svr = models.CharField(max_length=100) # DB서버
	ver = models.CharField(max_length=100) # DB버전
	usg = models.CharField(max_length=100) # 용도
	vip = models.CharField(max_length=100) # 가상 ip
	pri_ip = models.CharField(max_length=100) # 사설 ip
	pub_ip = models.CharField(max_length=100) # 공용 ip
	port1 = models.IntegerField() # 포트 번호
	priority = models.CharField(max_length=100) # 분류
	manager1 = models.CharField(max_length=100) # 정
	manager2 = models.CharField(max_length=100) # 부
	created_at = models.DateTimeField(default=datetime.now) # 생성일
	updated_at = models.DateTimeField(default=datetime.now) # 변경일
	
	class Meta:
		db_table = 'server_list'

	def __str__(self):
		return self.svr
