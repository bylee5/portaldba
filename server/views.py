from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Server

@login_required
def server(request):
    server_svr_list = server_svr_list = Server.objects.all()
    context = {'server_svr_list': server_svr_list}
    return render(request, 'server/server.html', context)

@login_required
def server_remove(request):
    server_svr_list = Server.objects.all()
    context = {'server_svr_list': server_svr_list}
    return render(request, 'server/server_remove.html', context)