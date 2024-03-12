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
    
    s_query = "select distinct monitoring_code_title from db_monitoring_code"
    
    with connections['default'].cursor() as cursor:
        title_list = []
        cursor.execute(s_query)
        title_list = namedtuplefetchall(cursor)

    s_query = "select distinct dbsvr from server_list"
    
    with connections['default'].cursor() as cursor:
        server_list = []
        cursor.execute(s_query)
        server_list = namedtuplefetchall(cursor)

    context = {
            'alert_title_lists': alert_title_list,
            'alert_server_lists': alert_server_list,
            'title_lists': title_list,
            'server_lists': server_list,
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
        i_query += "monitoring_threshold = '{0}', check_count_threshold = '{1}', alert_term = '{2}'".foramt(threshold, cycle, sleep)
            
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
def alert_multi_dml(request):
    if request.method == 'POST':
        checkboxValues = request.POST.getlist('checkboxValues[]')
        alert_id_list = ",".join( repr(e) for e in checkboxValues).replace("'","") # QUERY에 쓰일 서버명

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y/%m/%d %H:%M:%S")

        try:
            if len(checkboxValues) != 0:
                # 체크박스 클릭되어 다중 변경 대상이 있음
                dml_type = request.POST.get('dml_type')

                if dml_type == 'update':
                    mu_type = request.POST.get('mu_type')
                    mu_value = request.POST.get('mu_value')

                    u_query = '''UPDATE db_monitoring 
                                    SET {0} = '{1}'
                                WHERE db_monitoring_seqno IN ({2})
                                '''.format(mu_type, mu_value, alert_id_list)

                    with connections['default'].cursor() as cursor:
                        cursor.execute(u_query)

                elif dml_type == 'delete':
                    md_alert_del_reason = request.POST.get('md_alert_del_reason')
                    md_alert_del_note = request.POST.get('md_alert_del_note')
                    d_query = '''DELETE FROM db_monitoring 
                                WHERE db_monitoring_seqno IN ({0})
                                '''.format(alert_id_list)
                    
                    with connections['default'].cursor() as cursor:
                        cursor.execute(d_query)

                alert_type = "ERR_0"
                alert_message = ""

            else:
                # 체크박스 클릭 없음
                alert_type = "ERR_3"
                alert_message = "반영 대상이 없습니다. 작업대상 ID 체크박스를 클릭해주세요."
                last_modify_dt = ""

        except Exception as e:
            alert_type = "ERR_3"
            alert_message = e

        alert_yn = request.POST.get('s_alert_yn')
        alert_title = request.POST.get('s_alert_title')
        alert_dbsvr = request.POST.get('s_alert_dbsvr')
        callmorepostFlag = 'true'

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
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt,
            'alert_sql_flag': 'Y'
        }

        return render(request, 'alert/alert_select.html', context)

    else:
        return render(request, 'alert/alert.html')
    
@login_required
def alert_delete(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_id')
        d_monitoring_code_title = request.POST.get('d_monitoring_code_title')
        d_dbsvr = request.POST.get('d_dbsvr')
        d_monitoring_schedule = request.POST.get('d_monitoring_schedule')
        d_monitoring_yn = request.POST.get('d_monitoring_yn')
        d_monitoring_threshold = request.POST.get('d_monitoring_threshold')
        d_check_count_threshold = request.POST.get('d_check_count_threshold')
        d_alert_term = request.POST.get('d_alert_term')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""
        
        d_query = '''DELETE FROM db_monitoring 
                    WHERE db_monitoring_seqno = {0}
                    '''.format(d_id)
                    
        with connections['default'].cursor() as cursor:
            cursor.execute(d_query)
        
         # DO TO
        # 성공 후 데일리 백업 체크, 히스토리 로깅

        # 검색란
        alert_yn = request.POST.get('s_alert_yn')
        alert_title = request.POST.get('s_alert_title')
        alert_dbsvr = request.POST.get('s_alert_dbsvr')

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
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt,
            'alert_sql_flag': 'Y',
        }

        return render(request, 'alert/alert_select.html', context)

    else:
        return render(request, 'alert/alert.html')


@login_required
def alert_update(request):
    if request.method == 'POST':
        u_id = request.POST.get('u_id')
        u_monitoring_code_title = request.POST.get('u_monitoring_code_title')
        u_dbsvr = request.POST.get('u_dbsvr')
        u_monitoring_schedule = request.POST.get('u_monitoring_schedule')
        u_monitoring_yn = request.POST.get('u_monitoring_yn')
        u_monitoring_threshold = request.POST.get('u_monitoring_threshold')
        u_check_count_threshold = request.POST.get('u_check_count_threshold')
        u_alert_term = request.POST.get('u_alert_term')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        u_query = '''UPDATE db_monitoring 
                        SET monitoring_schedule = '{0}',
                        monitoring_yn = '{1}',
                        monitoring_threshold = {2},
                        check_count_threshold = {3},
                        alert_term = {4}
                        WHERE db_monitoring_seqno = {5}
                        '''.format(u_monitoring_schedule, u_monitoring_yn, 
                                   u_monitoring_threshold, u_check_count_threshold, 
                                   u_alert_term, u_id)

        with connections['default'].cursor() as cursor:
            cursor.execute(u_query)
        
        # DO TO
        # 성공 후 데일리 백업 체크, 히스토리 로깅

        # 검색란
        alert_yn = request.POST.get('s_alert_yn')
        alert_title = request.POST.get('s_alert_title')
        alert_dbsvr = request.POST.get('s_alert_dbsvr')

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
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt,
            'alert_sql_flag': 'Y',
        }

        return render(request, 'alert/alert_select.html', context)

    else:
        return render(request, 'alert/alert.html')

@login_required
def alert_remove(request):
    monitoring_svr_list = Alert.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'alert/alert.html', context)

@login_required
def alert_add(request):
    s_query = "select * from db_monitoring_code"
    
    with connections['default'].cursor() as cursor:
        alert_code_lists = []
        cursor.execute(s_query)
        alert_code_lists = namedtuplefetchall(cursor)

    context = {'alert_code_lists': alert_code_lists}
    
    return render(request, 'alert/alert_add.html', context)

@login_required
def alert_add_select(request):
    if request.method == 'POST':
        s_query = "select * from db_monitoring_code"
    
        with connections['default'].cursor() as cursor:
            alert_code_lists = []
            cursor.execute(s_query)
            alert_code_lists = namedtuplefetchall(cursor)
        
        page = int(request.POST.get('page'))
        total_count = len(alert_code_lists)
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(alert_code_lists, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                alert_code_lists = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                alert_code_lists = paginator.get_page(1)
        except PageNotAnInteger:
            alert_code_lists = paginator.get_page(1)
        except EmptyPage:
            alert_code_lists = paginator.get_page(paginator.num_pages)

        context = {
                'alert_code_lists': alert_code_lists,
                'total_count': total_count,
                'callmorepostFlag': callmorepostFlag,
                'alert_type': "ERR_0",
            }
        
        return render(request, 'alert/alert_add_select.html', context)
    else:
        return render(request, 'alert/alert_add.html', context)

@login_required
def alert_add_insert(request):
    if request.method == 'POST':
        i_monitoring_code_title = request.POST.get('i_monitoring_code_title')
        i_monitoring_code_desc = request.POST.get('i_monitoring_code_desc')
        i_monitoring_yn = request.POST.get('i_monitoring_yn')
        i_send_url = request.POST.get('i_send_url')
        i_send_topic_name = request.POST.get('i_send_topic_name')
        callmorepostFlag = 'true'

        i_query = '''INSERT INTO db_monitoring_code
                        SET monitoring_code_title = '{0}',
                        monitoring_code_desc = '{1}',
                        monitoring_yn = '{2}',
                        send_url = '{3}',
                        send_topic_name = '{4}'
                    '''.format(i_monitoring_code_title, i_monitoring_code_desc, i_monitoring_yn,
                               i_send_url, i_send_topic_name)
            
        with connections['default'].cursor() as cursor:
            cursor.execute(i_query)

        s_query = "select * from db_monitoring_code"
    
        with connections['default'].cursor() as cursor:
            alert_code_lists = []
            cursor.execute(s_query)
            alert_code_lists = namedtuplefetchall(cursor)
        
        page = int(request.POST.get('page'))
        total_count = len(alert_code_lists)
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(alert_code_lists, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                alert_code_lists = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                alert_code_lists = paginator.get_page(1)
        except PageNotAnInteger:
            alert_code_lists = paginator.get_page(1)
        except EmptyPage:
            alert_code_lists = paginator.get_page(paginator.num_pages)

        context = {
                'alert_code_lists': alert_code_lists,
                'total_count': total_count,
                'callmorepostFlag': callmorepostFlag,
                'alert_type': "ERR_0",
            }
        
        return render(request, 'alert/alert_add_select.html', context)
    else:
        return render(request, 'alert/alert_add.html', context)


@login_required
def alert_add_delete(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_id')

        d_query = "DELETE FROM db_monitoring_code WHERE monitoring_code_seqno = {0}".format(d_id)
    
        with connections['default'].cursor() as cursor:
            cursor.execute(d_query)
        
        s_query = "select * from db_monitoring_code"
    
        with connections['default'].cursor() as cursor:
            alert_code_lists = []
            cursor.execute(s_query)
            alert_code_lists = namedtuplefetchall(cursor)
        
        page = int(request.POST.get('page'))
        total_count = len(alert_code_lists)
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(alert_code_lists, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                alert_code_lists = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                alert_code_lists = paginator.get_page(1)
        except PageNotAnInteger:
            alert_code_lists = paginator.get_page(1)
        except EmptyPage:
            alert_code_lists = paginator.get_page(paginator.num_pages)

        context = {
                'alert_code_lists': alert_code_lists,
                'total_count': total_count,
                'callmorepostFlag': callmorepostFlag,
                'alert_type': "ERR_0",
            }
        
        return render(request, 'alert/alert_add_select.html', context)
    else:
        return render(request, 'alert/alert_add.html', context)


@login_required
def alert_add_update(request):
    if request.method == 'POST':
        u_id = request.POST.get('u_id')
        u_monitoring_code_title = request.POST.get('u_monitoring_code_title')
        u_monitoring_code_desc = request.POST.get('u_monitoring_code_desc')
        u_send_url = request.POST.get('u_send_url')
        u_send_topic_name = request.POST.get('u_send_topic_name')
        u_monitoring_yn = request.POST.get('u_monitoring_yn')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        u_query = '''UPDATE db_monitoring_code 
                        SET monitoring_code_title = '{0}',
                        monitoring_code_desc = '{1}',
                        send_url = '{2}',
                        send_topic_name = '{3}',
                        monitoring_yn = '{4}'
                        WHERE monitoring_code_seqno = {5}
                        '''.format(u_monitoring_code_title, u_monitoring_code_desc,
                                    u_send_url, u_send_topic_name, u_monitoring_yn, u_id)

        with connections['default'].cursor() as cursor:
            cursor.execute(u_query)
        
        # DO TO
        # 성공 후 데일리 백업 체크, 히스토리 로깅
        
        s_query = "select * from db_monitoring_code"
    
        with connections['default'].cursor() as cursor:
            alert_code_lists = []
            cursor.execute(s_query)
            alert_code_lists = namedtuplefetchall(cursor)
        
        page = int(request.POST.get('page'))
        total_count = len(alert_code_lists)
        page_max = math.ceil(total_count / 35)
        paginator = Paginator(alert_code_lists, page * 35)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                alert_code_lists = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                alert_code_lists = paginator.get_page(1)
        except PageNotAnInteger:
            alert_code_lists = paginator.get_page(1)
        except EmptyPage:
            alert_code_lists = paginator.get_page(paginator.num_pages)

        context = {
                'alert_code_lists': alert_code_lists,
                'total_count': total_count,
                'callmorepostFlag': callmorepostFlag,
                'alert_type': "ERR_0",
                'alert_message': alert_message,
            }
        
        return render(request, 'alert/alert_add_select.html', context)
    else:
        return render(request, 'alert/alert_add.html', context)

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