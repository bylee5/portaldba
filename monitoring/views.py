from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Monitoring

import math

@login_required
def monitoring(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def threads_connected(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def threads_running(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def slave_delay(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def innodb_lock(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def slow_query(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def undo_size(request):
    monitoring_svr_list = Monitoring.objects.all()
    context = {'monitoring_svr_list': monitoring_svr_list}
    return render(request, 'monitoring/monitoring.html', context)