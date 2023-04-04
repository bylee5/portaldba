from django.shortcuts import render
from .models import Server
from django.core.paginator import Paginator  
from django.contrib.auth.decorators import login_required

@login_required
def server(request):
    page = request.GET.get('page', '1')  # 페이지
    query = "SELECT * FROM server_list order by id desc"
    server_list = Server.objects.raw(query)
    paginator = Paginator(server_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'server_list': page_obj}
    return render(request, 'server/server.html', context)