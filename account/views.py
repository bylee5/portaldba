from django.shortcuts import render
from .models import Account

def index(request):
    account_list = Account.objects.all()
    context = {'account_list': account_list}
    return render(request, 'account/account.html', context)
