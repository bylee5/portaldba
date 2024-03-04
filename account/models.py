from django.db import models
from datetime import datetime

class Account(models.Model):
	account_create_dt = models.DateTimeField(default=datetime.now)		# 생성일        -- 2020-02-06
	account_update_dt = models.DateTimeField(default=datetime.now)    	# 변경일        -- 2020-02-06
	account_end_dt = models.DateTimeField(null=True) 				       			# 만료일        -- null
	account_requestor = models.CharField(blank=True, max_length=100, default='')      			# 요청자명      -- 이정희
	account_devteam = models.CharField(blank=True, max_length=100, default='') 		# 요청팀      	-- 표준화
	account_svr = models.CharField(blank=True, max_length=100, default='')          				# 호스트명      -- db-a
	account_user = models.CharField(max_length=50, default='')         				# 아이디        -- imsi_test
	account_host = models.CharField(max_length=100, default='')         				# 허용호스트    -- 127.0.0.1
	account_pass = models.CharField(max_length=100, default='')           			# 패스워드      	-- Test01)! select password("Test01)!");
	account_hash = models.CharField(blank=True, max_length=100, default='')           			# 해쉬         	-- select password("Test01)!"); -- *BB498F1B5EDFDB45CA0F6FD3FDAF0A4FE01730E5 -- 41자리
	account_grant = models.CharField(blank=True, max_length=100, default='')          			# 권한         	-- select, insert, update, delete
	account_grant_with = models.CharField(blank=True, max_length=100, default='N')   # grant with  	--
	account_db = models.CharField(blank=True, max_length=100, default='')             			# db          	-- test
	account_table = models.CharField(blank=True, max_length=100, default='')          			# table       	-- test
	account_info = models.CharField(blank=True, max_length=100, default='')            			# 용도         	-- 테스트용
	account_sql = models.CharField(blank=True, max_length=350, default='')            			# sql         	-- 주석 sql~~~~
	account_url = models.CharField(blank=True, max_length=100, default='')            			# url         	-- 지라 혹은 위키
	account_del_yn = models.CharField(blank=True, max_length=100, default='N')       # 삭제여부		-- N/Y
	account_del_dt = models.DateTimeField(null=True)                   				# 삭제조치일
	account_del_reason = models.CharField(null=True, blank=True, max_length=100, default='')     			# 삭제사유
	account_del_note = models.CharField(null=True, blank=True, max_length=100, default='')       			# 삭제비고

	# Meta 클래스는 모델에 대한 메타데이터를 정의한다.
	class Meta:
		db_table = 'account_account' # 데이터베이스 이름을 사용자가 지정
		# ordering = ['-account_create_dt'] # 기본 정렬 순서 정의하며 -표시는 내림차순을 표현
		# indexes = [models.Index(fields=['-account_create_dt']),] # 인덱스 생성이며 -표시는 MySQL에서 미지원

	# 객체를 표현하는 문자열을 반환
	def __str__(self):
		return self.account_svr

class AccountRepository(models.Model):
	create_dt = models.DateTimeField(default=datetime.now) # 일자
	repository_type = models.CharField(blank=True, max_length=10, default='') # 구분. PHP, JAVA 기타 등등
	repository_team = models.CharField(blank=True, max_length=20, default='') # 연관부서
	repository_name = models.CharField(blank=True, max_length=100, default='') # 레포지터리 명
	repository_url = models.CharField(blank=True, max_length=400, default='') # 레포지터리 URL
	account_user = models.CharField(blank=True, max_length=50, default='') # 계정명
	url = models.CharField(blank=True, max_length=100, default='') # JIRA URL
	info = models.CharField(blank=True, max_length=100, default='') # INFO

	class Meta:
		db_table = 'account_repository'

	def __str__(self):
		return self.repository_name

class Account_hash(models.Model):
	password_encrypt = models.CharField(blank=True, max_length=100, default='', unique=True) # 패스워드 암호화
	password_hash = models.CharField(blank=True, max_length=250, default='') # 패스워드 해시

	class Meta:
		db_table = 'account_hash'

	def __str__(self):
		return self.password_encrypt