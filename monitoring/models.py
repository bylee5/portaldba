from django.db import models
from datetime import datetime

class Monitoring(models.Model):
	svr = models.CharField(max_length=100) # DB서버

	class Meta:
		db_table = 'monitoring'

	def __str__(self):
		return self.svr

class Monitoring(models.Model):
	svr = models.CharField(max_length=100) # DB서버

	class Meta:
		db_table = 'monitoring'

	def __str__(self):
		return self.svr

class Monitoring(models.Model):
	svr = models.CharField(max_length=100) # DB서버

	class Meta:
		db_table = 'monitoring'

	def __str__(self):
		return self.svr