DBA 업무를 위한 포탈 사이트를 구축한다.
---
구현 기술 스택
```
Django 5.0.3 버전
BootStrap 5.2.3 버전
Jquery 3.6.4 버전
MySQL 8.0.32 버전
```
라이브러리
```
pip3 install -r requirements.txt
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
python3 manage.py runserver 0.0.0.0:8000
```
관리자 계정 생성
```
cd /path/to/portaldba
python3 manage.py createsuperuser
```
스케줄 작업은 Jenkins에서 진행
```
Build periodically Schedule : * * * * * 
Build Steps Execute shell : sudo python3 /path/to/portaldba/alert/scripts/threads_connected.py
```
