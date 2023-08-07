from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Memo

@login_required
def memo(request):
    memo_id = Memo.objects.all().filter(id=1)
    context = {'memo_id': '1', 'memo_textarea': '\n memo_textarea \n 내용'}
    return render(request, 'memo/memo.html', context)

@login_required
def memo_insert(request, memo_id):
    print(memo_id)
    if request.method == 'POST':
        memo_textarea = request.POST.get('memo_textarea')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""
        print(memo_textarea)
        # insert 쿼리
        insert_sql = "select 1"
        try:
            cursor = connections['default'].cursor()
            cursor.execute(insert_sql)
            connection.commit()

            # DO TO
            # 성공 후 데일리 백업 체크, 히스토리 로깅
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            print("로그히스토리용 insert_sql : " + insert_sql)
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

        except Exception as e:
            connection.rollback()
            alert_type = "ERR_3"
            alert_message = e
        finally:
            cursor.close()
    
        context = {
            'memo_id': '1',
            'alert_type': alert_type,
            'alert_message': alert_message
        }
        return render(request, 'memo/memo.html', context)
    else:
        return render(request, 'memo/memo.html') 
 