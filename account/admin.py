from django.contrib import admin

from .models import Account, AccountRepository, Account_hash

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id','account_create_dt', 'account_update_dt', 'account_requestor', 'account_devteam', 'account_svr', 'account_user', 'account_host', 'account_pass', 'account_hash', 'account_grant', 'account_grant_with', 'account_db', 'account_table', 'account_info', 'account_sql', 'account_url', 'account_del_yn')
    list_filter = ['account_create_dt']
    search_fields = ['account_host']

admin.site.register(Account, AccountAdmin)

admin.site.register(AccountRepository)
admin.site.register(Account_hash)
