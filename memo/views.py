from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Memo

import math

@login_required
def memo(request):
    memo_svr_list = Memo.objects.all()
    context = {'memo_svr_list': memo_svr_list}
    return render(request, 'memo/memo.html', context)
