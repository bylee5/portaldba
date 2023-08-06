from django.db import models
from datetime import datetime

class Memo(models.Model):
	svr = models.CharField(max_length=100) # 서버

	class Meta:
		db_table = 'memo'

	def __str__(self):
		return self.svr