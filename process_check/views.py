from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connections
import time

from .models import ServerList, JobInfo, JobServerMap

from collections import namedtuple

@login_required
def server_list(request):
    s_query = "SELECT COUNT(*) AS cnt FROM server_list"

    with connections['default'].cursor() as cursor:
        cursor.execute(s_query)
        row = cursor.fetchone()

    context = {'svr_count': row[0],}
    return render(request, 'process_check/server_list.html', context)

@login_required
def server_list_left_ajax(request):
    if request.method == 'POST':
        s_svr_name = request.POST.get('s_svr_name')

        if s_svr_name is None:
            s_svr_name=''

        s_query = "/*left*/SELECT sl.dbsvr AS svr_info_name, COUNT(ji.job_info_seqno) AS svr_total, IFNULL(SUM(jsm.use_yn),0) AS svr_use_total" + \
                  " FROM server_list AS sl" + \
                  " LEFT OUTER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                  " LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                  " WHERE sl.dbsvr LIKE '%" + s_svr_name + "%'" + \
                  " GROUP BY sl.dbsvr " + \
                  " ORDER BY sl.dbsvr "

        with connections['default'].cursor() as cursor:
            svr_info_lists = []
            cursor.execute(s_query)
            svr_info_lists = namedtuplefetchall(cursor)

        if(len(svr_info_lists) == 0): # 검색결과가 없다면
            print("검색결과 없음")

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

@login_required
def server_list_reload_left_ajax(request):
    if request.method == 'POST':
        time.sleep(0.2)
        svr_info_name = request.POST.getlist('svr_info_name[]')
        s_svr_name = request.POST.get('s_svr_name')
        s_job = request.POST.get('s_job')
        checkbox_unregister = request.POST.get('checkbox_unregister')
        checkbox_off = request.POST.get('checkbox_off')

        if s_svr_name is None:
            s_svr_name=''

        s_query = "SELECT sl.dbsvr AS svr_info_name, COUNT(ji.job_info_seqno) AS svr_total, IFNULL(SUM(jsm.use_yn),0) AS svr_use_total" + \
                  " FROM server_list AS sl" + \
                  " LEFT OUTER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                  " LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                  " WHERE sl.dbsvr LIKE '%" + s_svr_name + "%'" + \
                  " GROUP BY sl.dbsvr " + \
                  " ORDER BY sl.dbsvr "

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
    
@login_required
def server_list_right_ajax(request):
    if request.method == 'POST':

        svr_info_names = request.POST.getlist('svr_info_name[]') # 원래 입력값
        svr_info_name = ", ".join( repr(e) for e in svr_info_names) # QUERY에 쓰일 JOB_NAME 값

        s_job = request.POST.get('s_job') # 원래 입력값
        checkbox_unregister = request.POST.get('checkbox_unregister') # 원래 입력값
        checkbox_off = request.POST.get('checkbox_off') # 원래 입력값

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
                    s_query = "SELECT '" + svr_name + "' AS svr, ji.job_info_name, jsm.use_yn" + \
                              " FROM job_server_map AS jsm" + \
                              " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                              " AND jsm.server_list_seqno = " + \
                              " (SELECT id FROM server_list WHERE dbsvr='" + svr_name + "')" + \
                              " WHERE 1=1" + \
                              " AND ji.job_info_name like '%" + s_job + "%'" + \
                              str_checkbox_off + \
                              " ORDER BY ji.job_info_name"

                try:
                    with connections['default'].cursor() as cursor:
                        cursor.execute(s_query)
                        job_lists = namedtuplefetchall(cursor)
                        svr_job_lists.append([svr_name, job_lists])

                finally:
                    cursor.close()

        context = {
            'svr_job_lists': svr_job_lists,
            'svr_info_name': svr_info_name,
        }

        return render(request, 'process_check/server_list_right_ajax.html', context)
    
    else:
        return render(request, 'process_check/server_list_right_ajax.html')

@login_required
def server_list_delete_svr_use_yn_ajax(request):
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        svr = request.POST.get('svr')
        flag = request.POST.get('flag') # true or false
        use_yn = request.POST.get('use_yn') # None 일경우, 미등록 처리 하기 위함

        flag = 1 if flag == 'true' else 0 # true = 1, false = 0

        # 등록잡 삭제하기
        print("등록된 잡 삭제하기")
        query = "/*delete_job_use_yn_ajax*/ DELETE FROM job_server_map" + \
                " WHERE 1=1" + \
                " AND job_info_seqno = (SELECT job_info_seqno FROM job_info ji WHERE ji.job_info_name = '" + job_name+ "')" + \
                " AND server_list_seqno = (SELECT id FROM server_list sl WHERE sl.dbsvr='" + svr + "')"

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(query)
        finally:
            cursor.close()

    context = {
        'job_name': job_name,
        'svr': svr,
        'flag': flag,
    }

    return render(request, 'process_check/server_list_dummy_ajax.html', context)

@login_required
def server_list_update_svr_use_yn_ajax(request):
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        svr = request.POST.get('svr')
        flag = request.POST.get('flag') # true or false
        use_yn = request.POST.get('use_yn') # None 일경우, 미등록 처리 하기 위함

        flag = 1 if flag == 'true' else 0 # true = 1, false = 0

        # 미등록 서버,잡 입력받는경우. INSERT
        if use_yn == 'None':
            print("미등록입니다. 신규 등록합니다.")
            query =   "INSERT INTO job_server_map (job_info_seqno, server_list_seqno, use_yn)" + \
                        " SELECT ji.job_info_seqno, sl.id, 1" + \
                        " FROM server_list sl JOIN job_info AS ji" + \
                        " WHERE 1=1" + \
                        " AND ji.job_info_name='" + job_name + "'" + \
                        " AND sl.dbsvr='" + svr + "'"

        # 기 등록 서버, 잡 입력받은경우
        else:
            print("등록입니다. 업데이트합니다.")
            query = "/*update_job_use_yn_ajax*/UPDATE job_server_map jsm SET use_yn=" + str(flag) + \
                    " WHERE 1=1" + \
                    " AND jsm.job_info_seqno = (SELECT job_info_seqno FROM job_info ji WHERE ji.job_info_name = '" + job_name+ "')" + \
                    " AND jsm.server_list_seqno = (SELECT id FROM server_list sl WHERE sl.dbsvr='" + svr + "')"

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(query)
        finally:
            cursor.close()

    context = {
        'job_name': job_name,
        'svr': svr,
        'flag': flag,
    }

    return render(request, 'process_check/server_list_dummy_ajax.html', context)

@login_required
def server_job_list(request):
    s_query = "SELECT COUNT(*) AS cnt FROM job_info"
    with connections['default'].cursor() as cursor:
        cursor.execute(s_query)
        row = cursor.fetchone()

    context = {
        'job_count': row[0],
    }

    return render(request, 'process_check/server_job_list.html', context)

@login_required
def server_job_list_left_ajax(request):
    if request.method == 'POST':
        s_job_name = request.POST.get('s_job_name')

        if s_job_name is None:
            s_job_name=''

        # 잡 리스트 및 JOB 스케줄 가져오기
        s_query = "/*left*/SELECT ji.job_info_name, COUNT(dbsvr) AS svr_total, IFNULL(SUM(use_yn),0) AS svr_use_total" + \
                    " FROM server_list sl" + \
                    " INNER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                    " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                    " where ji.job_info_name like '%" + s_job_name + "%'" + \
                    " GROUP BY ji.job_info_name" + \
                    " ORDER BY ji.job_info_name"

        with connections['default'].cursor() as cursor:
            job_info_lists = []
            cursor.execute(s_query)
            job_info_lists = namedtuplefetchall(cursor)

        if(len(job_info_lists) == 0): # 검색결과가 없다면
            print("검색결과 없음")

        context = {
            'job_info_lists': job_info_lists,
            's_job_name': s_job_name,
        }

        return render(request, 'process_check/server_job_list_left_ajax.html', context)

    else:
        return render(request, 'process_check/server_job_list_left_ajax.html')

@login_required
def server_job_list_right_ajax(request):
    if request.method == 'POST':
        job_info_names = request.POST.getlist('job_info_name[]') # 원래 입력값
        job_info_name = ", ".join( repr(e) for e in job_info_names) # QUERY에 쓰일 JOB_NAME 값

        s_svr = request.POST.get('s_svr') # 원래 입력값
        checkbox_unregister = request.POST.get('checkbox_unregister') # 원래 입력값
        checkbox_off = request.POST.get('checkbox_off') # 원래 입력값

        if s_svr is None:
            s_svr=''

        if len(job_info_names) == 0:
            job_svr_lists = ''
            job_info_name = "''"

        else:
            job_svr_lists = []
            for job_name in job_info_names:
                if checkbox_off =='ON':
                    str_checkbox_off = " AND use_yn=1"
                else:
                    str_checkbox_off = ""

                # 미등록 안보기 ON
                if checkbox_unregister == 'ON':
                    s_query =   "/*right*/SELECT ji.job_info_name, sl.dbsvr AS svr, jsm.use_yn" + \
                                " FROM server_list sl" + \
                                " INNER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                                " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                                " WHERE 1=1" + \
                                " AND sl.dbsvr IS NOT NULL AND jsm.use_yn IS NOT NULL" + \
                                " AND ji.job_info_name='" + job_name + "'" + \
                                " AND sl.dbsvr like '%" + s_svr + "%'" + \
                                str_checkbox_off + \
                                " ORDER BY ji.job_info_name, svr"

                # 미등록 OFF
                else:
                    s_query =  "/*right*/SELECT ji.job_info_name, sl.dbsvr AS svr, jsm.use_yn" + \
                                " FROM server_list sl JOIN job_info AS ji" + \
                                " LEFT JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno AND ji.job_info_seqno = jsm.job_info_seqno" + \
                                " WHERE 1=1" + \
                                " AND ji.job_info_name='" + job_name + "'" + \
                                " AND sl.dbsvr like '%" + s_svr + "%'" + \
                               str_checkbox_off + \
                               " ORDER BY ji.job_info_name, svr"

                try:
                    with connections['default'].cursor() as cursor:
                        cursor.execute(s_query)
                        svr_lists = namedtuplefetchall(cursor)
                        job_svr_lists.append([job_name, svr_lists])
                finally:
                    cursor.close()

        context = {
            'job_svr_lists': job_svr_lists,
            'job_info_name': job_info_name,
        }

        return render(request, 'process_check/server_job_list_right_ajax.html', context)
    
    else:
        return render(request, 'process_check/server_job_list_right_ajax.html')

@login_required
def server_job_list_update_job_use_yn_ajax(request):
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        svr = request.POST.get('svr')
        flag = request.POST.get('flag') # true or false
        use_yn = request.POST.get('use_yn') # None 일경우, 미등록 처리 하기 위함

        flag = 1 if flag == 'true' else 0 # true = 1, false = 0

        # 미등록 서버,잡 입력받는경우. INSERT
        if use_yn == 'None':
            query =   "INSERT INTO job_server_map (job_info_seqno, server_list_seqno, use_yn)" + \
                        " SELECT ji.job_info_seqno, sl.id, 1" + \
                        " FROM server_list sl JOIN job_info AS ji" + \
                        " WHERE 1=1" + \
                        " AND ji.job_info_name='" + job_name + "'" + \
                        " AND sl.dbsvr='" + svr + "'"

        # 기 등록 서버, 잡 입력받은경우
        else:
            query = "UPDATE job_server_map jsm SET use_yn=" + str(flag) + \
                    " WHERE 1=1" + \
                    " AND jsm.job_info_seqno = (SELECT job_info_seqno FROM job_info ji WHERE ji.job_info_name = '" + job_name+ "')" + \
                    " AND jsm.server_list_seqno = (SELECT id FROM server_list sl WHERE sl.dbsvr='" + svr + "')"

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(query)
        finally:
            cursor.close()

    context = {
        'job_name': job_name,
        'svr': svr,
        'flag': flag,
    }

    return render(request, 'process_check/server_job_list_dummy_ajax.html', context)

@login_required
def server_job_list_delete_job_use_yn_ajax(request):
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        svr = request.POST.get('svr')
        flag = request.POST.get('flag') # true or false
        use_yn = request.POST.get('use_yn') # None 일경우, 미등록 처리 하기 위함

        flag = 1 if flag == 'true' else 0 # true = 1, false = 0

        # 등록잡 삭제하기
        query = "DELETE FROM job_server_map" + \
                " WHERE 1=1" + \
                " AND job_info_seqno = (SELECT job_info_seqno FROM job_info ji WHERE ji.job_info_name = '" + job_name+ "')" + \
                " AND server_list_seqno = (SELECT id FROM server_list sl WHERE sl.dbsvr='" + svr + "')"

        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(query)
        finally:
            cursor.close()


    context = {
        'job_name': job_name,
        'svr': svr,
        'flag': flag,
    }

    return render(request, 'process_check/server_job_list_dummy_ajax.html', context)

@login_required
def server_job_list_reload_left_ajax(request):
    if request.method == 'POST':
        time.sleep(0.2)
        job_info_name = request.POST.getlist('job_info_name[]')
        s_job_name = request.POST.get('s_job_name')
        s_svr = request.POST.get('s_svr')
        checkbox_unregister = request.POST.get('checkbox_unregister')
        checkbox_off = request.POST.get('checkbox_off')

        if s_job_name is None:
            s_job_name=''

        # 잡 리스트 및 JOB 스케줄 가져오기
        s_query = "SELECT ji.job_info_name, COUNT(dbsvr) AS svr_total, IFNULL(SUM(use_yn),0) AS svr_use_total" + \
                    " FROM server_list sl" + \
                    " INNER JOIN job_server_map AS jsm ON sl.id = jsm.server_list_seqno" + \
                    " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                    " where ji.job_info_name like '%" + s_job_name + "%'" + \
                    " GROUP BY ji.job_info_name" + \
                    " ORDER BY ji.job_info_name"

        try:
            with connections['default'].cursor() as cursor:
                job_info_lists = []
                cursor.execute(s_query)
                job_info_lists = namedtuplefetchall(cursor)
        finally:
            cursor.close()

        context = {
            'job_info_lists': job_info_lists,
            'job_info_name_checked_list': job_info_name,
            's_svr': s_svr,
            'checkbox_unregister': checkbox_unregister,
            'checkbox_off': checkbox_off,
        }

        return render(request, 'process_check/server_job_list_left_ajax.html', context)

    else:
        return render(request, 'process_check/server_job_list_left_ajax.html')
