from django.db import models
from datetime import datetime

class Data_life_cycle(models.Model):
	svr = models.CharField(max_length=100) # 서버

	class Meta:
		db_table = 'data_life_cycle'

	def __str__(self):
		return self.svr