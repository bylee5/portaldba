from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connections
import time

from .models import ServerList, JobInfo, JobServerMap

from collections import namedtuple

@login_required
def server_list(request):
    s_query = "SELECT COUNT(*) AS cnt FROM portaldba.server_list"

    with connections['default'].cursor() as cursor:
        cursor.execute(s_query)
        row = cursor.fetchone()

    context = {'process_check_svr_count': row[0],}
    return render(request, 'process_check/process_check.html', context)

def server_list_left_ajax(request):
    if request.method == 'POST':
        s_svr_name = request.POST.get('s_svr_name')

        # print("-------------------------------------------------------------")
        # print(s_svr_name)

        if s_svr_name is None:
            s_svr_name=''

        s_query = "/*left*/SELECT sl.dbsvr AS svr_info_name, COUNT(ji.job_info_seqno) AS svr_total, IFNULL(SUM(jsm.use_yn),0) AS svr_use_total" + \
                  " FROM server_list AS sl" + \
                  " LEFT OUTER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                  " LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                  " WHERE sl.dbsvr LIKE '%" + s_svr_name + "%'" + \
                  " GROUP BY sl.dbsvr " + \
                  " ORDER BY sl.dbsvr "

        # print(s_query)
        # print("-------------------------------------------------------------")

        with connections['default'].cursor() as cursor:
            svr_info_lists = []
            cursor.execute(s_query)
            svr_info_lists = namedtuplefetchall(cursor)

        if(len(svr_info_lists) == 0): # 검색결과가 없다면
            print("하나도없네")

        context = {
            'svr_info_lists': svr_info_lists,
            's_svr_name': s_svr_name,
        }

        return render(request, 'process_check/server_list_left_ajax.html', context)

    else:
        return render(request, 'process_check/server_list_left_ajax.html')

def namedtuplefetchall(cursor):
    #"Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def server_list_reload_left_ajax(request):
    if request.method == 'POST':
        time.sleep(0.2)
        svr_info_name = request.POST.getlist('svr_info_name[]')
        s_svr_name = request.POST.get('s_svr_name')
        s_job = request.POST.get('s_job')
        checkbox_unregister = request.POST.get('checkbox_unregister')
        checkbox_off = request.POST.get('checkbox_off')

        # print("-------------------------------------------------------------")
        # print("server_job_list_reload_left_ajax")
        # print("-------------------------------------------------------------")
        # print(s_svr_name)
        # print(svr_info_name)
        # print(s_job)
        # print(checkbox_unregister)
        # print(checkbox_off)
        # print("-------------------------------------------------------------")

        if s_svr_name is None:
            s_svr_name=''

        s_query = "/*left*/SELECT sl.dbsvr AS svr_info_name, COUNT(ji.job_info_seqno) AS svr_total, IFNULL(SUM(jsm.use_yn),0) AS svr_use_total" + \
                  " FROM server_list AS sl" + \
                  " LEFT OUTER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                  " LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                  " WHERE sl.dbsvr LIKE '%" + s_svr_name + "%'" + \
                  " GROUP BY sl.dbsvr " + \
                  " ORDER BY sl.dbsvr "

        # print(s_query)
        # print("-------------------------------------------------------------")

        with connections['default'].cursor() as cursor:
            svr_info_lists = []
            cursor.execute(s_query)
            svr_info_lists = namedtuplefetchall(cursor)

        context = {
            'svr_info_lists': svr_info_lists,
            'svr_info_name_checked_list': svr_info_name,
            's_job': s_job,
            'checkbox_unregister': checkbox_unregister,
            'checkbox_off': checkbox_off,
        }

        return render(request, 'process_check/server_list_left_ajax.html', context)

    else:
        return render(request, 'process_check/server_list_left_ajax.html')
    

def server_list_right_ajax(request):
    if request.method == 'POST':

        svr_info_names = request.POST.getlist('svr_info_name[]') # 원래 입력값
        svr_info_name = ", ".join( repr(e) for e in svr_info_names) # QUERY에 쓰일 JOB_NAME 값

        s_job = request.POST.get('s_job') # 원래 입력값
        checkbox_unregister = request.POST.get('checkbox_unregister') # 원래 입력값
        checkbox_off = request.POST.get('checkbox_off') # 원래 입력값

        # print("-------------------------------------------------------------")
        # print("right POST 테스트")
        # print("-------------------------------------------------------------")
        # print(job_info_names)
        # print("s_svr : " + str(s_svr))
        # print("checkbox_unregister : " + str(checkbox_unregister))
        # print("checkbox_off : " + str(checkbox_off))
        # print("-------------------------------------------------------------")

        if s_job is None:
            s_job = ''

        if len(svr_info_names) == 0:
            # print("비어있는 값 입력")
            svr_job_lists = ''
            svr_info_name = "''"

        else:
            svr_job_lists = []
            for svr_name in svr_info_names:
                if checkbox_off =='ON':
                    str_checkbox_off = " AND use_yn=1"
                else:
                    str_checkbox_off = ""

                # 미등록 안보기 ON
                if checkbox_unregister == 'ON':
                    print("미등록 안보기 ON")
                    s_query = "SELECT '" + svr_name + "' AS svr, ji.job_info_name, jsm.use_yn" + \
                              " FROM job_server_map AS jsm" + \
                              " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                              " AND jsm.server_list_seqno = " + \
                              " (SELECT id FROM server_list WHERE dbsvr='" + svr_name + "')" + \
                              " WHERE 1=1" + \
                              " AND jsm.use_yn IS NOT NULL" + \
                              " AND ji.job_info_name like '%" + s_job + "%'" + \
                              str_checkbox_off + \
                              " ORDER BY ji.job_info_name"

                # 미등록 OFF
                else:
                    # print("미등록 안보기 OFF")
                    s_query = "SELECT '" + svr_name + "' AS svr, ji.job_info_name, jsm.use_yn" + \
                              " FROM job_server_map AS jsm" + \
                              " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                              " AND jsm.server_list_seqno = " + \
                              " (SELECT id FROM server_list WHERE dbsvr='" + svr_name + "')" + \
                              " WHERE 1=1" + \
                              " AND ji.job_info_name like '%" + s_job + "%'" + \
                              str_checkbox_off + \
                              " ORDER BY ji.job_info_name"

                # print(s_query)
                # print("-------------------------------------------------------------")

                try:
                    with connections['default'].cursor() as cursor:
                        cursor.execute(s_query)
                        job_lists = namedtuplefetchall(cursor)
                        svr_job_lists.append([svr_name, job_lists])

                finally:
                    cursor.close()

        # print(job_svr_lists)
        context = {
            'svr_job_lists': svr_job_lists,
            'svr_info_name': svr_info_name,
        }

        return render(request, 'process_check/server_list_right_ajax.html', context)
    else:
        return render(request, 'process_check/server_list_right_ajax.html')