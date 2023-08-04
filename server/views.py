from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Server

import math

@login_required
def server(request):
    server_svr_list = server_svr_list = Server.objects.all().filter(delete_yn='N')
    context = {'server_svr_list': server_svr_list}
    return render(request, 'server/server.html', context)

@login_required
def server_dummy(request):
    return render(request, 'server/dummy_ajax.html')

@login_required
def server_select(request):
    if request.method == 'POST':
        dbtype = request.POST.get('s_dbtype')
        dbenv = request.POST.get('s_dbenv')
        dbservice = request.POST.get('s_dbservice')
        dbsvr = request.POST.get('s_dbsvr')
        dbver = request.POST.get('s_dbver')
        audit_yn = request.POST.get('s_audit_yn')
        url = request.POST.get('s_url')
        callmorepostFlag = 'true'

        if dbsvr == '':
            # 전체 서버 검색
            server_list = Server.objects.filter(
                dbtype__contains=dbtype,
                dbenv__contains=dbenv,
                dbservice__contains=dbservice,
                dbver__contains=dbver,
                audit_yn__contains=audit_yn,
                url__contains=url,
                delete_yn='N'
            ).order_by('-id')
        else:
            # 특정 서버 검색
            server_list = Server.objects.filter(
                dbtype__contains=dbtype,
                dbenv__contains=dbenv,
                dbservice__contains=dbservice,
                dbsvr=dbsvr,
                dbver__contains=dbver,
                audit_yn__contains=audit_yn,
                url__contains=url,
                delete_yn='N'
            ).order_by('-id')

        page = int(request.POST.get('page'))
        total_count = server_list.count()
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(server_list, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                server_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                server_list = paginator.get_page(1)
        except PageNotAnInteger:
            server_list = paginator.get_page(1)
        except EmptyPage:
            server_list = paginator.get_page(paginator.num_pages)

        context = {
            'dbtype': dbtype,
            'dbenv': dbenv,
            'dbservice': dbservice,
            'dbsvr': dbsvr,
            'dbver': dbver,
            'audit_yn': audit_yn,
            'url': url,
            'server_list': server_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max,
            'alert_type': "ERR_0"
        }

        return render(request, 'server/server_select.html', context)

    else:
        return render(request, 'server/server.html')    

@login_required
def server_insert(request):
    if request.method == 'POST':
        # 입력란
        dbtype = request.POST.get('i_server_dbtype')
        dbenv = request.POST.get('i_server_dbenv')
        dbservice = request.POST.get('i_server_dbservice')
        dbsvr = request.POST.get('i_server_dbsvr')
        dbver = request.POST.get('i_server_dbver')
        usg = request.POST.get('i_server_usg')
        pri_ip = request.POST.get('i_server_pri_ip')
        pub_ip = request.POST.get('i_server_pub_ip')
        vip = request.POST.get('i_server_vip')
        port1 = request.POST.get('i_server_port1')
        priority = request.POST.get('i_server_priority')
        manager1 = request.POST.get('i_server_manager1')
        manager2 = request.POST.get('i_server_manager2')
        audit_yn = request.POST.get('i_server_audit_yn')
        url = request.POST.get('i_server_url')
        forceinsert_flag = request.POST.get('forceinsert_flag')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # 
        alert_type = "ERR_0"
        alert_message = ""

        # insert 쿼리
        insert_sql = "INSERT INTO server_list (created_at, updated_at, " + \
                        "dbtype, dbenv, dbservice, dbsvr, dbver, " + \
                        "usg, pri_ip, pub_ip, vip, port1, " + \
                        "priority, manager1, manager2, audit_yn, url, " + \
                        "delete_yn, delete_reason, delete_note) VALUES( " + \
                        "'" + last_modify_dt + "'," + \
                        "'" + last_modify_dt + "'," + \
                        "'" + dbtype + "'," + \
                        "'" + dbenv + "'," + \
                        "'" + dbservice + "'," + \
                        "'" + dbsvr + "'," + \
                        "'" + dbver + "'," + \
                        "'" + usg + "'," + \
                        "'" + pri_ip + "'," + \
                        "'" + pub_ip + "'," + \
                        "'" + vip + "'," + \
                        "'" + port1 + "'," + \
                        "'" + priority + "'," + \
                        "'" + manager1 + "'," + \
                        "'" + manager2 + "', " + \
                        "'" + audit_yn + "'" + ", " + \
                        "'" + url + "', " + \
                        "'N', '', '')"
        try:
            cursor = connections['default'].cursor()
            cursor.execute(insert_sql)
            connection.commit()
        except Exception as e:
            connection.rollback()
            alert_type = "ERR_3"
            alert_message = e
        finally:
            cursor.close()

        # 검색란
        dbtype = request.POST.get('s_dbtype')
        dbenv = request.POST.get('s_dbenv')
        dbservice = request.POST.get('s_dbservice')
        dbsvr = request.POST.get('s_dbsvr')
        dbver = request.POST.get('s_dbver')
        audit_yn = request.POST.get('s_audit_yn')
        url = request.POST.get('s_url')
        callmorepostFlag = 'true'

        if dbsvr == '':
            # 전체 서버 검색
            server_list = Server.objects.filter(
                dbtype__contains=dbtype,
                dbenv__contains=dbenv,
                dbservice__contains=dbservice,
                dbver__contains=dbver,
                audit_yn__contains=audit_yn,
                url__contains=url,
                delete_yn='N'
            ).order_by('-id')
        else:
            # 특정 서버 검색
            server_list = Server.objects.filter(
                dbtype__contains=dbtype,
                dbenv__contains=dbenv,
                dbservice__contains=dbservice,
                dbsvr=dbsvr,
                dbver__contains=dbver,
                audit_yn__contains=audit_yn,
                url__contains=url,
                delete_yn='N'
            ).order_by('-id')

        page = int(request.POST.get('page'))
        total_count = server_list.count()
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(server_list, page * 35)

        try:
            if int(page) >= page_max:  # 마지막 페이지 멈춤 구현
                server_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                server_list = paginator.get_page(1)
        except PageNotAnInteger:
            server_list = paginator.get_page(1)
        except EmptyPage:
            server_list = paginator.get_page(paginator.num_pages)

        context = {
            'dbtype': dbtype,
            'dbenv': dbenv,
            'dbservice': dbservice,
            'dbsvr': dbsvr,
            'dbver': dbver,
            'audit_yn': audit_yn,
            'url': url,
            'server_list': server_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max,
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt
        }

        return render(request, 'server/server_select.html', context)

    else:
        return render(request, 'server/server.html')


@login_required
def server_remove(request):
    server_svr_list = Server.objects.all()
    context = {'server_svr_list': server_svr_list}
    return render(request, 'server/server_remove.html', context)