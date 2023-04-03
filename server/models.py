from django.db import models
from datetime import datetime

class Server(models.Model):
	svr = models.CharField(max_length=100) # DB서버
	usg = models.CharField(max_length=100) # 용도
	port1 = models.IntegerField() # 포트 번호
	ip1 = models.CharField(max_length=100) # ip1
	ip2 = models.CharField(max_length=100) # ip2
	priority = models.CharField(max_length=100) # 분류
	created_at = models.DateTimeField(default=datetime.now) # 생성일
	updated_at = models.DateTimeField(default=datetime.now) # 변경일
	
	class Meta:
		db_table = 'server_list'

	def __str__(self):
		return self.svr
