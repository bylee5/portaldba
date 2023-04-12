from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Process_check

@login_required
def process_check(request):
    process_check_svr_list = Process_check.objects.all()
    context = {'process_check_svr_list': process_check_svr_list}
    return render(request, 'process_check/process_check.html', context)