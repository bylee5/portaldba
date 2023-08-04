from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
            print("전체 서버 검색")
            server_list = Server.objects.filter(
                dbtype__contains=dbtype,
                dbenv__contains=dbenv,
                dbservice__contains=dbservice,
                dbver__contains=dbver,
                audit_yn__contains=audit_yn,
                url__contains=url,
                delete_yn='N'
            ).order_by('-id')
            print("total_count:", server_list.count())
        else:
            print("특정 서버 검색")
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
def server_remove(request):
    server_svr_list = Server.objects.all()
    context = {'server_svr_list': server_svr_list}
    return render(request, 'server/server_remove.html', context)