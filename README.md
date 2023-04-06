DBA 업무를 위한 포탈 사이트를 구축한다.
---
구현 기술 스택
```
Django 4.1.7 버전
BootStrap 5.2.3 버전
Jquery 3.6.4 버전
MySQL 8.0.32 버전
```
라이브러리
```
pip3 install pymysql
pip3 install django-environ
```
DB 접속 정보
```
cd /path/to/portaldba
vi .env
```
DB 스키마 
```
cd /path/to/portaldba
python3 manage.py migrate
```
서버 시작
```
cd /path/to/portaldba
python3 manage.py runserver 127.0.0.1:8000
```
관리자 계정 생성
```
cd /path/to/portaldba
python3 manage.py createsuperuser
```