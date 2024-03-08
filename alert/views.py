from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Alert

import math

from collections import namedtuple

@login_required
def alert(request):
    s_query = '''
            select distinct mc.monitoring_code_title 
            from db_monitoring m 
                join db_monitoring_code mc on (m.monitoring_code_seqno = mc.monitoring_code_seqno)
            '''
    
    with connections['default'].cursor() as cursor:
        alert_title_list = []
        cursor.execute(s_query)
        alert_title_list = namedtuplefetchall(cursor)

    s_query = '''
            select distinct sl.dbsvr
            from db_monitoring m
                join server_list sl on (m.server_list_seqno = sl.id)
            '''
    
    with connections['default'].cursor() as cursor:
        alert_server_list = []
        cursor.execute(s_query)
        alert_server_list = namedtuplefetchall(cursor)

    context = {
            'alert_title_lists': alert_title_list,
            'alert_server_lists': alert_server_list,
            'alert_type': "ERR_0"
        }
    
    return render(request, 'alert/alert.html', context)


@login_required
def alert_select(request):
    if request.method == 'POST':
        alert_yn = request.POST.get('s_alert_yn')
        alert_title = request.POST.get('s_alert_title')
        alert_dbsvr = request.POST.get('s_alert_dbsvr')
        callmorepostFlag = 'true'

        # 검색이 있다면
        if alert_yn == '' or alert_yn == 'None':
            alert_yn = ''
        else:
            alert_yn = " AND a.monitoring_yn = '{0}' ".format(alert_yn.strip())
        
        if alert_title == '' or alert_title == 'None':
            alert_title = ''
        else:
            alert_title = " AND c.monitoring_code_title = '{0}' ".format(alert_title.strip())

        if alert_dbsvr == '' or alert_dbsvr == 'None':
            alert_dbsvr = ''
        else:
            alert_dbsvr = " AND b.dbsvr = '{0}' ".format(alert_dbsvr.strip())
    
        s_query = '''
                SELECT
                    c.monitoring_code_title,
                    c.monitoring_code_seqno,
                    a.server_list_seqno,
                    b.dbsvr,
                    b.pri_ip,
                    b.port1,
                    a.db_monitoring_seqno,
                    a.monitoring_yn,
                    a.monitoring_threshold,
                    IFNULL(a.monitoring_error_at, 'NULL') AS monitoring_error_at,
                    a.alert_term,
                    IFNULL(TIME_TO_SEC(TIMEDIFF(NOW(), a.monitoring_error_at)), 'NULL') AS how_long_error,
                    a.check_count_threshold,
                    a.check_count_current,
                    a.monitoring_schedule,
                    IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), '-') > 0,
                        (LPAD(MINUTE(NOW()), 2, 0) BETWEEN LPAD(
                                substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), '-', 1), 2,
                                0) AND LPAD(
                                substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), '-', -1), 2,
                                0)), (LPAD(MINUTE(NOW()), 2, 0) like
                                        IF(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), '-') > 0,
                                (LPAD(HOUR(NOW()), 2, 0) BETWEEN LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), '-',
                                                        1), 2, 0) AND LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), '-',
                                                        -1), 2, 0)), (LPAD(HOUR(NOW()), 2, 0) like IF(
                                        substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), '-') > 0,
                                (LPAD(DAY(NOW()), 2, 0) BETWEEN LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), '-',
                                                        1), 2, 0) AND LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), '-',
                                                        -1), 2, 0)), (LPAD(DAY(NOW()), 2, 0) like IF(
                                        substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), '-') > 0,
                                (LPAD(MONTH(NOW()), 2, 0) BETWEEN LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), '-',
                                                        1), 2, 0) AND LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), '-',
                                                        -1), 2, 0)), (LPAD(MONTH(NOW()), 2, 0) like IF(
                                        substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), '7'),
                                IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), '-') > 0,
                                    (LPAD(DAYOFWEEK(NOW()) - 1 + 7, 2, 0) BETWEEN LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', 1), 2, 0) AND LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', -1), 2, 0)), (LPAD(DAYOFWEEK(NOW()) - 1 + 7, 2, 0) like IF(
                                            substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1) = '*', '%',
                                            LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), 2, 0)))),
                                IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), '-') > 0,
                                    (LPAD(DAYOFWEEK(NOW()) - 1, 2, 0) BETWEEN LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', 1), 2, 0) AND LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', -1), 2, 0)), (LPAD(DAYOFWEEK(NOW()) - 1, 2, 0) like IF(
                                            substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1) = '*', '%',
                                            LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), 2, 0))))
                        ) AS monitoring_now,
                        a.created_at,
                        a.updated_at
                FROM db_monitoring a
                    join server_list b on (a.server_list_seqno = b.id)
                    join db_monitoring_code c on (a.monitoring_code_seqno = c.monitoring_code_seqno)
                WHERE 1=1
                AND a.monitoring_code_seqno in (select monitoring_code_seqno from db_monitoring_code)
                '''
        s_query += alert_yn
        s_query += alert_title
        s_query += alert_dbsvr
        s_query += " ORDER BY a.monitoring_code_seqno desc, dbsvr, a.monitoring_schedule, a.db_monitoring_seqno"
                
        with connections['default'].cursor() as cursor:
            alert_list = []
            cursor.execute(s_query)
            alert_list = namedtuplefetchall(cursor)
            
        page = int(request.POST.get('page'))
        total_count = len(alert_list)
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(alert_list, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                alert_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                alert_list = paginator.get_page(1)
        except PageNotAnInteger:
            alert_list = paginator.get_page(1)
        except EmptyPage:
            alert_list = paginator.get_page(paginator.num_pages)


        context = {
            'alert_yn': alert_yn,
            'alert_title': alert_title,
            'alert_dbsvr': alert_dbsvr,
            'alert_list': alert_list,
            'total_count': total_count,
            'callmorepostFlag': callmorepostFlag,
            'page_max': page_max,
            'alert_type': "ERR_0"
        }

        return render(request, 'alert/alert_select.html', context)

    else:
        return render(request, 'alert/alert.html')    

@login_required
def alert_insert(request):
    if request.method == 'POST':
        alert_title = request.POST.get('i_alert_title')
        alert_dbsvr = request.POST.get('i_alert_dbsvr')
        schedule = request.POST.get('i_schedule')
        alert_yn = request.POST.get('i_alert_yn')
        threshold = request.POST.get('i_threshold')
        cycle = request.POST.get('i_cycle')
        sleep = request.POST.get('i_sleep')
        callmorepostFlag = 'true'

        if schedule == '':
            schedule = '* * * * *'

        s_query = "select id from server_list where dbsvr ='{0}'".format(alert_dbsvr)
        with connections['default'].cursor() as cursor:
            cursor.execute(s_query)
            dbsvr_row = cursor.fetchone()
        
        s_query = "select monitoring_code_seqno from db_monitoring_code where monitoring_code_title ='{0}'".format(alert_title)
        with connections['default'].cursor() as cursor:
            cursor.execute(s_query)
            title_row = cursor.fetchone()

        i_query = "insert into db_monitoring set server_list_seqno = '{0}', monitoring_code_seqno = '{1}', monitoring_schedule = '{2}',".format(dbsvr_row[0], title_row[0], schedule)
        i_query += "monitoring_yn = '{0}',".format(alert_yn)
        i_query += "monitoring_threshold = '{0}', check_count_threshold = '{1}', alert_term = '{2}'".format(threshold, cycle, sleep)
            
        with connections['default'].cursor() as cursor:
            cursor.execute(i_query)

        s_query = '''
                SELECT
                    c.monitoring_code_title,
                    c.monitoring_code_seqno,
                    a.server_list_seqno,
                    b.dbsvr,
                    b.pri_ip,
                    b.port1,
                    a.db_monitoring_seqno,
                    a.monitoring_yn,
                    a.monitoring_threshold,
                    IFNULL(a.monitoring_error_at, 'NULL') AS monitoring_error_at,
                    a.alert_term,
                    IFNULL(TIME_TO_SEC(TIMEDIFF(NOW(), a.monitoring_error_at)), 'NULL') AS how_long_error,
                    a.check_count_threshold,
                    a.check_count_current,
                    a.monitoring_schedule,
                    IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), '-') > 0,
                        (LPAD(MINUTE(NOW()), 2, 0) BETWEEN LPAD(
                                substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), '-', 1), 2,
                                0) AND LPAD(
                                substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), '-', -1), 2,
                                0)), (LPAD(MINUTE(NOW()), 2, 0) like
                                        IF(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 1), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), '-') > 0,
                                (LPAD(HOUR(NOW()), 2, 0) BETWEEN LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), '-',
                                                        1), 2, 0) AND LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), '-',
                                                        -1), 2, 0)), (LPAD(HOUR(NOW()), 2, 0) like IF(
                                        substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 2), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), '-') > 0,
                                (LPAD(DAY(NOW()), 2, 0) BETWEEN LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), '-',
                                                        1), 2, 0) AND LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), '-',
                                                        -1), 2, 0)), (LPAD(DAY(NOW()), 2, 0) like IF(
                                        substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 3), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), '-') > 0,
                                (LPAD(MONTH(NOW()), 2, 0) BETWEEN LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), '-',
                                                        1), 2, 0) AND LPAD(
                                        substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), '-',
                                                        -1), 2, 0)), (LPAD(MONTH(NOW()), 2, 0) like IF(
                                        substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1) = '*', '%',
                                        LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 4), ' ', -1), 2, 0))))
                        AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), '7'),
                                IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), '-') > 0,
                                    (LPAD(DAYOFWEEK(NOW()) - 1 + 7, 2, 0) BETWEEN LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', 1), 2, 0) AND LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', -1), 2, 0)), (LPAD(DAYOFWEEK(NOW()) - 1 + 7, 2, 0) like IF(
                                            substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1) = '*', '%',
                                            LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), 2, 0)))),
                                IF(INSTR(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), '-') > 0,
                                    (LPAD(DAYOFWEEK(NOW()) - 1, 2, 0) BETWEEN LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', 1), 2, 0) AND LPAD(
                                            substring_index(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1),
                                                            '-', -1), 2, 0)), (LPAD(DAYOFWEEK(NOW()) - 1, 2, 0) like IF(
                                            substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1) = '*', '%',
                                            LPAD(substring_index(substring_index(a.monitoring_schedule, ' ', 5), ' ', -1), 2, 0))))
                        ) AS monitoring_now,
                        a.created_at,
                        a.updated_at
                FROM db_monitoring a
                    join server_list b on (a.server_list_seqno = b.id)
                    join db_monitoring_code c on (a.monitoring_code_seqno = c.monitoring_code_seqno)
                WHERE 1=1
                AND a.monitoring_code_seqno in (select monitoring_code_seqno from db_monitoring_code)
                ORDER BY a.monitoring_code_seqno desc, dbsvr, a.monitoring_schedule, a.db_monitoring_seqno
                '''
                
        with connections['default'].cursor() as cursor:
            alert_list = []
            cursor.execute(s_query)
            alert_list = namedtuplefetchall(cursor)
        

        page = int(request.POST.get('page'))
        total_count = len(alert_list)
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(alert_list, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                alert_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                alert_list = paginator.get_page(1)
        except PageNotAnInteger:
            alert_list = paginator.get_page(1)
        except EmptyPage:
            alert_list = paginator.get_page(paginator.num_pages)


        context = {
            'alert_yn': alert_yn,
            'alert_title': alert_title,
            'alert_dbsvr': alert_dbsvr,
            'alert_list': alert_list,
            'total_count': total_count,
            'callmorepostFlag': callmorepostFlag,
            'page_max': page_max,
            'alert_type': "ERR_0"
        }

        return render(request, 'alert/alert_select.html', context)

    else:
        return render(request, 'alert/alert.html')   

def namedtuplefetchall(cursor):
    #"Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

@login_required
def threads_connected(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)

@login_required
def threads_running(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)

@login_required
def slave_delay(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)

@login_required
def innodb_lock(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)

@login_required
def slow_query(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)

@login_required
def undo_size(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)