from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.utils import timezone

from .models import Memo

@login_required
def memo(request):
    dba_board = Memo.objects.all().filter(id=1)
    context = {'dba_board': dba_board}
    return render(request, 'memo/memo.html', context)

@login_required
def memo_select(request, memo_id):
    if request.method == 'GET':
        dba_board = Memo.objects.all().filter(id=memo_id)

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        if dba_board.count() != 1:
            # 더미 데이터 추가
            sql = "REPLACE INTO dba_board (id, board_content) VALUES (%s, %s)"
            try: 
                cursor = connections['default'].cursor()
                cursor.execute(sql, (memo_id, ''))
                connection.commit()

                # DO TO
                # 성공 후 데일리 백업 체크, 히스토리 로깅
                print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                print("로그히스토리용 sql : " + sql)
                print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

            except Exception as e:
                connection.rollback()
                alert_type = "ERR_3"
                alert_message = e
            finally:
                cursor.close()
        context = {'dba_board': dba_board}
        return render(request, 'memo/memo.html', context)
    return render(request, 'memo/memo.html') 

@login_required
def memo_insert(request):
    if request.method == 'POST':
        memo_id = request.POST.get('memo_id')
        board_content = request.POST.get('memo_textarea')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        # alert type 초기화
        alert_type = "ERR_0"
        alert_message = ""

        # 기본 PK 조회
        if memo_id == '':
            memo_id = "1"

        # insert 쿼리
        insert_sql = "REPLACE INTO dba_board (id, board_content) VALUES (%s, %s)"

        try: 
            cursor = connections['default'].cursor()
            cursor.execute(insert_sql, (memo_id, board_content))
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
    
        dba_board = Memo.objects.all().filter(id=memo_id)
        context = {
            'dba_board': dba_board,
            'alert_type': alert_type,
            'alert_message': alert_message
        }
        return render(request, 'memo/dummy_ajax.html', context)
    else:
        return render(request, 'memo/memo.html') 
 