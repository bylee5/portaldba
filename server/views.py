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

        # alert type 초기화
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

            # DO TO
            # 성공 후 데일리 백업 체크, 히스토리 로깅
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            print("로그히스토리용 insert_sql : " + insert_sql)
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

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
def server_delete(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_id')
        d_server_dbtype = request.POST.get('d_server_dbtype')
        d_server_dbenv = request.POST.get('d_server_dbenv')
        d_server_dbservice = request.POST.get('d_server_dbservice')
        d_server_dbsvr = request.POST.get('d_server_dbsvr')
        d_server_dbver = request.POST.get('d_server_dbver')
        d_server_usg = request.POST.get('d_server_usg')
        d_server_pri_ip = request.POST.get('d_server_pri_ip')
        d_server_pub_ip = request.POST.get('d_server_pub_ip')
        d_server_vip = request.POST.get('d_server_vip')
        d_server_port1 = request.POST.get('d_server_port1')
        d_server_priority = request.POST.get('d_server_priority')
        d_server_manager1 = request.POST.get('d_server_manager1')
        d_server_manager2 = request.POST.get('d_server_manager2')
        d_server_audit_yn = request.POST.get('d_server_audit_yn')
        d_server_delete_reason = request.POST.get('d_server_delete_reason')
        d_server_delete_note = request.POST.get('d_server_delete_note')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""
        
        delete_sql = "UPDATE server_list " + \
                        "SET deleted_at = " + "'" + last_modify_dt + "'" + \
                        ", delete_yn = 'Y' " + \
                        ", delete_reason = " + "'" + d_server_delete_reason + "'" + \
                        ", delete_note = " + "'" + d_server_delete_note + "'" + \
                        " WHERE id = " + d_id + ";"

        try:
            cursor = connections['default'].cursor()
            cursor.execute(delete_sql)
            connection.commit()

            # DO TO
            # 성공 후 데일리 백업 체크, 히스토리 로깅
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            print("로그히스토리용 delete_sql : " + delete_sql)
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

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
def server_update(request):
    if request.method == 'POST':
        u_id = request.POST.get('u_id')
        u_server_dbtype = request.POST.get('u_server_dbtype')
        u_server_dbenv = request.POST.get('u_server_dbenv')
        u_server_dbservice = request.POST.get('u_server_dbservice')
        u_server_dbsvr = request.POST.get('u_server_dbsvr')
        u_server_dbver = request.POST.get('u_server_dbver')
        u_server_usg = request.POST.get('u_server_usg')
        u_server_pri_ip = request.POST.get('u_server_pri_ip')
        u_server_pub_ip = request.POST.get('u_server_pub_ip')
        u_server_vip = request.POST.get('u_server_vip')
        u_server_port1 = request.POST.get('u_server_port1')
        u_server_priority = request.POST.get('u_server_priority')
        u_server_manager1 = request.POST.get('u_server_manager1')
        u_server_manager2 = request.POST.get('u_server_manager2')
        u_server_audit_yn = request.POST.get('u_server_audit_yn')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        update_sql = "UPDATE server_list " + \
                        "SET updated_at = '" + last_modify_dt + "'" + \
                        ", dbtype = '" + u_server_dbtype + "'" + \
                        ", dbenv = " + "'" + u_server_dbenv + "'" + \
                        ", dbservice = " + "'" + u_server_dbservice + "'" + \
                        ", dbsvr = " + "'" + u_server_dbsvr + "'" + \
                        ", dbver = " + "'" + u_server_dbver + "'" + \
                        ", usg = " + "'" + u_server_usg + "'" + \
                        ", pri_ip = " + "'" + u_server_pri_ip + "'" + \
                        ", pub_ip = " + "'" + u_server_pub_ip + "'" + \
                        ", vip = " + "'" + u_server_vip + "'" + \
                        ", port1 = " + "'" + u_server_port1 + "'" + \
                        ", priority = " + "'" + u_server_priority + "'" + \
                        ", manager1 = " + "'" + u_server_manager1 + "'" + \
                        ", manager2 = " + "'" + u_server_manager2 + "'" + \
                        ", audit_yn = " + "'" + u_server_audit_yn + "'" + \
                        " WHERE id = " + u_id + ";"

        try:
            cursor = connections['default'].cursor()
            cursor.execute(update_sql)
            connection.commit()

            # DO TO
            # 성공 후 데일리 백업 체크, 히스토리 로깅
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            print("로그히스토리용 update_sql : " + update_sql)
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

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
def server_multi_dml(request):
    if request.method == 'POST':
        checkboxValues = request.POST.getlist('checkboxValues[]')
        server_id_list = ",".join( repr(e) for e in checkboxValues).replace("'","") # QUERY에 쓰일 서버명

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        # 체크박스가 체크된 경우
        if len(checkboxValues) != 0:
            dml_type = request.POST.get('dml_type')

            # 다중 수정인 경우
            if dml_type == 'update':
                mu_type = request.POST.get('mu_type')
                mu_value = request.POST.get('mu_value')


                u_query = "UPDATE server_list " + \
                            "SET updated_at = '" + last_modify_dt + "'" \
                            ", " + mu_type + " = '" + mu_value + "'" \
                            " WHERE id IN(" + server_id_list + ");"

                try:
                    cursor = connections['default'].cursor()
                    cursor.execute(u_query)
                    connection.commit()

                    # 성공 후 데일리 백업 체크, 히스토리 로깅
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                    print("로그히스토리용 u_query : " + u_query)
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

                except Exception as e:
                    connection.rollback()
                    alert_type = "ERR_3"
                    alert_message = e
                finally:
                    cursor.close()

            # 다중 삭제인 경우
            elif dml_type == 'delete':
                md_server_delete_reason = request.POST.get('md_server_delete_reason')
                md_server_delete_note = request.POST.get('md_server_delete_note')
                d_query = "UPDATE server_list " + \
                                "SET deleted_at = '" + last_modify_dt + "'" \
                                ", delete_yn = 'Y'" + \
                                ", delete_reason = " + "'" + md_server_delete_reason + "'" + \
                                ", delete_note = " + "'" + md_server_delete_note + "'" + \
                                " WHERE id IN(" + server_id_list + ");"

                try:
                    cursor = connections['default'].cursor()
                    cursor.execute(d_query)
                    connection.commit()

                    # 성공 후 데일리 백업 체크, 히스토리 로깅
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                    print("로그히스토리용 d_query : " + d_query)
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

                except Exception as e:
                    connection.rollback()
                    alert_type = "ERR_3"
                    alert_message = e
                finally:
                    cursor.close()

        # 체크박스가 체크되지 않은 경우
        else:
            alert_type = "ERR_3"
            alert_message = "반영 대상이 없습니다. 작업대상 ID 체크박스를 클릭해주세요."
            last_modify_dt = ""

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
    server_svr_list = Server.objects.all().filter(delete_yn='Y')
    context = {'server_svr_list': server_svr_list}
    return render(request, 'server/server_remove.html', context)

@login_required
def server_remove_select(request):
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
                delete_yn='Y'
            ).order_by('-deleted_at')
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
                delete_yn='Y'
            ).order_by('-deleted_at')

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
            'page_max': page_max
        }

        return render(request, 'server/server_remove_select.html', context)

    else:
        return render(request, 'server/server_remove.html')