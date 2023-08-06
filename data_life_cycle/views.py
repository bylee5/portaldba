from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Data_life_cycle

import math

@login_required
def data_life_cycle(request):
    data_life_cycle_svr_list = Data_life_cycle.objects.all()
    context = {'data_life_cycle_svr_list': data_life_cycle_svr_list}
    return render(request, 'data_life_cycle/data_life_cycle.html', context)