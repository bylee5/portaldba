from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import math

from .models import Account, AccountRepository

@login_required
def account(request):
    account_svr_list = account_svr_list = Account.objects.all().filter(account_del_yn='N').order_by('account_svr').values('account_svr').distinct()
    context = {'account_svr_list': account_svr_list}
    return render(request, 'account/account.html', context)

@login_required
def account_remove(request):
    account_svr_list = Account.objects.all().filter(account_del_yn='Y').order_by('account_svr').values('account_svr').distinct()
    context = {'account_svr_list': account_svr_list}
    return render(request, 'account/account_remove.html', context)

@login_required
def account_repository_select(request):
    if request.method == 'POST':
        s_repository_team = request.POST.get('s_repository_team')
        s_repository_type = request.POST.get('s_repository_type')
        s_repository_name = request.POST.get('s_repository_name')
        s_repository_url = request.POST.get('s_repository_url')
        s_account_user = request.POST.get('s_account_user')
        s_url = request.POST.get('s_url')
        s_info = request.POST.get('s_info')

        # print("============= page : ")
        # print(request.POST.get('page'))

        repository_list = AccountRepository.objects.filter(
            repository_team__contains=s_repository_team,
            repository_type__startswith=s_repository_type,
            repository_name__contains=s_repository_name,
            repository_url__contains=s_repository_url,
            account_user__contains=s_account_user,
            url__contains=s_url,
            info__contains=s_info
        ).order_by('-id')

        page = int(request.POST.get('page'))
        s_total_count = repository_list.count()
        page_max = math.ceil(s_total_count / 40)
        paginator = Paginator(repository_list, page * 40)

        try:
            if int(page) >= page_max:  # 마지막 페이지 멈춤 구현
                repository_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                repository_list = paginator.get_page(1)
        except PageNotAnInteger:
            repository_list = paginator.get_page(1)
        except EmptyPage:
            repository_list = paginator.get_page(paginator.num_pages)

        print("page_max : " + str(page_max))

        context = {
            'repository_list': repository_list,
            'repository_team': s_repository_team,
            'repository_type': s_repository_type,
            'repository_name': s_repository_name,
            'repository_url': s_repository_url,
            'account_user': s_account_user,
            'url': s_url,
            'info': s_info,
            'total_count': s_total_count,
            'page_max': page_max
        }

        return render(request, 'account/account_repository_select.html', context)

    else:
        return render(request, 'account/account_repository.html')

#########################################################################
# fast select
#########################################################################
@login_required
def account_select_fast(request):
    if request.method == 'POST':
        account_user = request.POST.get('account_search')
        account_svr_list = Account.objects.all().filter(account_del_yn='N').order_by('account_svr').values('account_svr').distinct()
        callmorepostFlag = 'true'

        account_list = Account.objects.filter(
            account_user__contains=account_user,
            account_del_yn='N'
        ).order_by('-id')

        page = 1
        total_count = account_list.count()
        page_max = math.ceil(total_count / 30)
        paginator = Paginator(account_list, page * 30)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                account_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                account_list = paginator.get_page(1)
        except PageNotAnInteger:
            account_list = paginator.get_page(1)
        except EmptyPage:
            account_list = paginator.get_page(paginator.num_pages)

        context = {
            'account_user': account_user,
            'account_list': account_list,
            'account_svr_list': account_svr_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max,
            'alert_type': "ERR_0"
        }
        return render(request, 'account/account.html', context)

    else:
        return render(request, 'account/account.html')