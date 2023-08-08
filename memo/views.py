from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Memo

@login_required
def memo(request):
    dba_board = Memo.objects.all().filter(dba_board_seqno=1)
    context = {'dba_board': dba_board}
    return render(request, 'memo/memo.html', context)

@login_required
def memo_select(request, memo_id):
    if request.method == 'GET':
        print("memo_id:", memo_id)
        dba_board = Memo.objects.all().filter(id=memo_id)
        context = {'dba_board': dba_board}
        return render(request, 'memo/memo.html', context)
    return render(request, 'memo/memo.html') 

@login_required
def memo_insert(request):
    if request.method == 'POST':
        dba_board_seqno = request.POST.get('memo_id')
        board_content = request.POST.get('memo_textarea')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        print("dba_board_seqno:", dba_board_seqno)
        print("board_content:", board_content)

        # insert 쿼리
        insert_sql = "REPLACE INTO dba_board (dba_board_seqno, last_writer) VALUES (" + \
                        "'" + dba_board_seqno + "'," + \
                        "'" + board_content + "');" 
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
            'memo_id': dba_board_seqno,
            'memo_textarea': board_content,
            'alert_type': alert_type,
            'alert_message': alert_message
        }
        return render(request, 'memo/dummy_ajax.html', context)
    else:
        return render(request, 'memo/memo.html') 
 