from django.db import models

class Alert(models.Model):
	svr = models.CharField(max_length=100) # DB서버

	class Meta:
		db_table = 'alert'

	def __str__(self):
		return self.svr
