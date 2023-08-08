from django.db import models
from datetime import datetime

class Memo(models.Model):
	board_content = models.TextField() # 보드 내용
	last_writer = models.IntegerField() # IP

	class Meta:
		db_table = 'dba_board'

	def __str__(self):
		return self.last_writer