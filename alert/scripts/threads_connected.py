#!/usr/bin/pyhton
import sys
import pymysql
from pymysql.constants import CLIENT
import requests
import datetime
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '../.env')

db_server = env('DB_HOST')
db_user = env('DB_USER')
db_pass = env('DB_PASSWORD')
db_port = int(env('DB_PORT'))

conn = pymysql.connect(host=db_server, 
                       user=db_user, 
                       password=db_pass, 
                       db='portaldba', 
                       port=db_port,
                       charset='utf8', 
                       connect_timeout=2,
                       client_flag=CLIENT.MULTI_STATEMENTS)

sql = '''
    SELECT b.dbsvr, b.pri_ip, b.port1, a.db_monitoring_seqno, a.server_list_seqno, a.monitoring_code_seqno, a.monitoring_threshold, a.up_down_from_threshold, a.monitoring_error_at, a.monitoring_query, a.alert_term, c.monitoring_code_title, c.send_url, TIME_TO_SEC(TIMEDIFF(NOW(),a.monitoring_error_at)), a.check_count_threshold, a.check_count_current, c.send_topic_name, a.monitoring_schedule,
	IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),'-') > 0,(LPAD(MINUTE(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),'-',-1),2,0)),(LPAD(MINUTE(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),2,0))))
	AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),'-') > 0,(LPAD(HOUR(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),'-',-1),2,0)),(LPAD(HOUR(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),2,0))))
	AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),'-') > 0,(LPAD(DAY(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),'-',-1),2,0)),(LPAD(DAY(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),2,0))))
	AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),'-') > 0,(LPAD(MONTH(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),'-',-1),2,0)),(LPAD(MONTH(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),2,0))))
	AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'7'),
	IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-') > 0,(LPAD(DAYOFWEEK(NOW())-1+7,2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',-1),2,0)),(LPAD(DAYOFWEEK(NOW())-1+7,2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),2,0)))),
	IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-') > 0,(LPAD(DAYOFWEEK(NOW())-1,2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',-1),2,0)),(LPAD(DAYOFWEEK(NOW())-1,2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),2,0))))
	) as monitoring_now -- 현재 모니터링 대상인가?
	FROM db_monitoring a, server_list b, db_monitoring_code c
	WHERE a.server_list_seqno = b.id
	AND a.monitoring_code_seqno = c.monitoring_code_seqno
	AND a.monitoring_code_seqno in (1)
	AND a.monitoring_yn = 'Y'
	AND (
		a.monitoring_error_at is not NULL or
		(
			-- MIN 비교
			IF(
				INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),'-') > 0, -- 스케쥴이 RANGE로 설정되어 있는가?
					/* RANGE로 설정되어 있는 경우 */ (LPAD(MINUTE(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),'-',-1),2,0)),
					/* 특정 숫자 또는 Asterisk가 지정된 경우 */ (LPAD(MINUTE(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 1),' ',-1),2,0)))
			)

			-- HOUR 비교
			AND IF(
				INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),'-') > 0, -- 스케쥴이 RANGE로 설정되어 있는가?
					/* RANGE로 설정되어 있는 경우 */ (LPAD(HOUR(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),'-',-1),2,0)),
					/* 특정 숫자 또는 Asterisk가 지정된 경우 */ (LPAD(HOUR(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),2,0)))
			)

			-- DAY 비교
			AND IF(
				INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),'-') > 0, -- 스케쥴이 RANGE로 설정되어 있는가?
					/* RANGE로 설정되어 있는 경우 */ (LPAD(HOUR(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1),'-',-1),2,0)),
					/* 특정 숫자 또는 Asterisk가 지정된 경우 */ (LPAD(HOUR(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 3),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),2,0)))
			)

			-- MONTH 비교
			AND IF(
				INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),'-') > 0, -- 스케쥴이 RANGE로 설정되어 있는가?
					/* RANGE로 설정되어 있는 경우 */ (LPAD(MONTH(NOW()),2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1),'-',-1),2,0)),
					/* 특정 숫자 또는 Asterisk가 지정된 경우 */ (LPAD(MONTH(NOW()),2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 4),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 2),' ',-1),2,0)))
			)

			-- DAYOFWEEK 비교
			AND IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'7'),
					 -- 스케쥴에 7이 있는 경우
					IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-') > 0, -- 스케쥴이 RANGE로 설정되어 있는가?
						/* RANGE로 설정되어 있는 경우 */ (LPAD(DAYOFWEEK(NOW())-1+7,2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',-1),2,0)),
						/* 특정 숫자 또는 Asterisk가 지정된 경우 */ (LPAD(DAYOFWEEK(NOW())-1+7,2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),2,0)))
					),
					 -- 스케쥴에 7이 없는 경우
					IF(INSTR(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-') > 0, -- 스케쥴이 RANGE로 설정되어 있는가?
						/* RANGE로 설정되어 있는 경우 */ (LPAD(DAYOFWEEK(NOW())-1,2,0) BETWEEN LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',1),2,0) AND LPAD(substring_index(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),'-',-1),2,0)),
						/* 특정 숫자 또는 Asterisk가 지정된 경우 */ (LPAD(DAYOFWEEK(NOW())-1,2,0) like IF(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1)='*','%',LPAD(substring_index(substring_index(a.monitoring_schedule,' ', 5),' ',-1),2,0)))
					)
			)
		)
	)
'''

with conn:
    with conn.cursor() as cursor:
        cursor.execute(sql)

        if cursor.rowcount == 0:
            sys.exit("종료")

        res = cursor.fetchall()
        for row in res:
            print(row)
            dbname = row[0]
            dbhost = row[1]
            dbPort = row[2]
            monitor_id = row[3]
            server_list_seqno	= row[4]
            monitoring_code_seqno	= row[5]
            threshold_num = row[6]
            threshold_ud	= row[7]
            errored_at = row[8]
            monitor_query = row[9]
            alert_term = row[10]
            curl_title = row[11]
            curl_url	= row[12]
            how_long_error = row[13]
            check_count_threshold	= row[14]
            check_count_current = row[15]
            send_topic_name = row[16]
            monitoring_schedule	= row[17]
            monitoring_now = row[18]
            
            dbconn = pymysql.connect(host=dbname, 
                            user=db_user, 
                            password=db_pass, 
                            db='information_schema',
                            port=db_port,
                            charset='utf8', 
                            connect_timeout=2,
                            client_flag=CLIENT.MULTI_STATEMENTS)

            with dbconn:
                with dbconn.cursor() as dbcursor:
                    sql = "show status like 'threads_connected'"
                    dbcursor.execute(sql)
                    thread_count = int(dbcursor.fetchone()[1])
                    print("thread_count " + str(thread_count))
            
            # 모니터링 조건에 맞는 결과가 없는 경우
            if thread_count < threshold_num:
                # Problem 알람을 받았던 모니터링일 때
                if errored_at != None:
                    # 멤버분들이 모니터링 알람을 받으셨을 것 같은데요... 그럼 다시 OK 알람 받으세요~
                    header = {'Content-type': 'application/json'}
                    icon_emoji = ":pill:"
                    username = "Moni"
                    channel = "monitor"
                    text = "[OK] {0} {1}=*{2}*".format(dbname, curl_title, str(thread_count))

                    attachments = [{
                        "color": "#0000FF",
                        "mrkdwn_in": ["text"]
                    }]
                    attachments[0]['text'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " / Schdl : `{0}` \n탐지값={1} / 임계값={2}".format(monitoring_schedule, 
                                                                                                                                                thread_count, 
                                                                                                                                                threshold_num)

                    data = {"channel": channel, "username": username, "icon_emoji": icon_emoji, "text": text, "attachments": attachments}
                    print(data)
                    requests.post(curl_url, headers=header, json=data)
                    print('슬랙 OK 얼럿 전송')
                    
                    
                    # 이 모니터링은 OK니까 또 OK일때에는 모니터링 문자 받을 필요 없겠지
                    sql = '''
                            UPDATE db_monitoring
                            SET monitoring_error_at = NULL, check_count_current = 0
                            WHERE db_monitoring_seqno = '{0}'
                        '''.format(monitor_id)
                    cursor.execute(sql)
                    conn.commit()
                    
                    
                    # 히스토리 저장
                    sql = '''
                            INSERT INTO db_monitoring_history
                            (db_monitoring_group,db_monitoring_seqno,server_list_seqno,monitoring_code_seqno,action_type,monitoring_num,monitoring_threshold,monitoring_at,msg_content,alert_term,check_count_threshold,check_count_current,monitoring_schedule)
                            VALUES ('{0}','{1}','{2}','{3}','PO','{4}','{5}',now(),'{6}','{7}','{8}','{9}','{10}')
                        '''.format('Test', monitor_id, server_list_seqno, monitoring_code_seqno, thread_count, threshold_num, 'CURLOPT_POSTFIELDS', alert_term, check_count_threshold, check_count_current, monitoring_schedule)
                    cursor.execute(sql)
                    conn.commit()
                    
                    print(dbname + " OK (First)")
                    
                # OK 알람을 받았던 모니터링일 때
                else:
                    # 초당 수백건 호출 중. 업데이트가 무의미하다 판단하여 초기화 생략.
                    # Problem 메시지 전에 정상 체크되는 경우 check_count_current 초기화가 생략되어 누적되는 증상이 있어 0보다 큰 경우만 업데이트 하도록 변경.
                    if check_count_current > 0:
                        sql = '''
                                UPDATE db_monitoring
                                SET check_count_current = 0
                                WHERE db_monitoring_seqno = '{0}'
                            '''.format(monitor_id)
                        cursor.execute(sql)
                        conn.commit()

                        # 히스토리 저장
                        sql = '''
                                INSERT INTO db_monitoring_history
                                (db_monitoring_group,db_monitoring_seqno,server_list_seqno,monitoring_code_seqno,action_type,monitoring_num,monitoring_threshold,monitoring_at,msg_content,alert_term,check_count_threshold,check_count_current,monitoring_schedule)
                                VALUES ('{0}','{1}','{2}','{3}','CO','{4}','{5}',now(),'{6}','{7}','{8}','{9}','{10}')
                            '''.format('Test', monitor_id, server_list_seqno, monitoring_code_seqno, thread_count, threshold_num, 'CURLOPT_POSTFIELDS', alert_term, check_count_threshold, check_count_current, monitoring_schedule)
                        cursor.execute(sql)
                        conn.commit()
                        
                        # 모니터링 조건에 걸려왔으나 Problem 알람은 안 받았을 것 같으니 그냥 넘어가자.
                        print(dbname + " OK (Just Checked)")
                    
                    else:
                        # 모니터링 조건에 걸리지도 않았는데 앞서 Problem 알람도 안 받았을 것 같으니 그냥 넘어가자.
                        print(dbname + " OK (Repeated)")
            
            # 모니터링 조건에 맞는 결과가 있는 경우
            else:
                check_count_current += 1
                
                # Problem 알람을 받지 않았거나, 받았으나 alertTerm이 차서 다시 받아야하는 경우일 때의 조건. 단, 현재 모니터링 대상인 서버에 한한다.
                if errored_at == None or (how_long_error >= alert_term and monitoring_now == 1):
                    # 장애일 경우 당시 잠수타는 접속들을 봅시다.
                    sqlconn = pymysql.connect(host=dbname, 
                            user=db_user, 
                            password=db_pass, 
                            db='information_schema',
                            port=db_port,
                            charset='utf8', 
                            connect_timeout=2,
                            client_flag=CLIENT.MULTI_STATEMENTS)

                    with sqlconn:
                        with sqlconn.cursor() as sqlcursor:
                            sql = '''
                                select PROCESSLIST_HOST as host, count(*) cnt, max(PROCESSLIST_TIME)
                                from performance_schema.threads
                                where PROCESSLIST_COMMAND = 'sleep'
                                group by PROCESSLIST_HOST
                                order by cnt desc
                                limit 50
                                '''
                            sqlcursor.execute(sql)
                    
                    attachment2 = {
                            "color" : "#FF0000",
                            "title" : "Sleep 상태인 Thread의 Host별 Count",
                            "text" : "```HOST \tCOUNT(Sleep) \tMAX(TIME)\n",
                            "mrkdwn_in" : ["text"]
                        }
                    
                    if sqlcursor.rowcount > 0:
                        print('슬랙 NG 메시지 작성')
                        res = sqlcursor.fetchall()

                        for row in res:
                            print(row)
                            selectedHost = row[0]
                            selectedCnt = row[1]
                            selectedMaxTime = row[2]
                            
                            attachment2['text'] = attachment2['text'] + "{0}\t{1}\t{2}\n".format(selectedHost,selectedCnt,selectedMaxTime)
                    
                    attachment2['text'] = attachment2['text'] + "```"
                    print(attachment2)
                    
                    # 멤버분들이 모니터링 알람을 아직 안 받으셨을 것 같은데요... 그럼 Problem 알람 받고 재깍재깍 체크할 것.
                    # 현재체크횟수가 체크횟수임계치만큼 도달할 경우에만 메시지 발송
                    if check_count_current >= check_count_threshold:
                        header = {'Content-type': 'application/json'}
                        icon_emoji = ":skull_and_crossbones:"
                        username = "Moni"
                        channel = "monitor"
                        text = "[PROBLEM] {0} {1}=*{2}*".format(dbname, curl_title, str(thread_count))

                        attachments = [{
                            "color": "#FF0000",
                            "mrkdwn_in": ["text"]
                        }]
                        attachments[0]['text'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " / Schdl : `{0}`\n탐지값={1} / 임계값={2}\n체크횟수={3}/{4}".format(monitoring_schedule, 
                                                                                                                                                                    thread_count, 
                                                                                                                                                                    threshold_num, 
                                                                                                                                                                    check_count_current, 
                                                                                                                                                                    check_count_threshold)

                        attachments.append(attachment2)

                        data = {"channel": channel, "username": username, "icon_emoji": icon_emoji, "text": text, "attachments": attachments}
                        print(data)
                        requests.post(curl_url, headers=header, json=data)
                        print('슬랙 NG 얼럿 전송')
                        
                        # Problem이니까 또 Problem일때에는 모니터링 문자 받을 필요 없겠지?
                        sql = '''
                            UPDATE db_monitoring
                            SET monitoring_error_at = NOW(), check_count_current = check_count_current + 1
                            WHERE db_monitoring_seqno = '{0}';
                            '''.format(monitor_id)
                        cursor.execute(sql)
                        conn.commit()
                        
                        # 히스토리 저장
                        sql = '''
                                INSERT INTO db_monitoring_history
                                (db_monitoring_group,db_monitoring_seqno,server_list_seqno,monitoring_code_seqno,action_type,monitoring_num,monitoring_threshold,monitoring_at,msg_content,alert_term,check_count_threshold,check_count_current,monitoring_schedule)
                                VALUES ('{0}','{1}','{2}','{3}','P','{4}','{5}',now(),'{6}','{7}','{8}','{9}','{10}')
                            '''.format('Test', monitor_id, server_list_seqno, monitoring_code_seqno, thread_count, threshold_num, 'CURLOPT_POSTFIELDS', alert_term, check_count_threshold, check_count_current, monitoring_schedule)
                        cursor.execute(sql)
                        conn.commit()
                        
                        print(dbname + " Problem (First) " + str(check_count_current) + "/" + str(check_count_threshold))
                    
                    else:
                        # 이 모니터링은 Problem 같지만 좀더 체크해보기 위해 check count 값만 늘려두자.
                        sql = '''
                            UPDATE db_monitoring
                            SET check_count_current = check_count_current + 1
                            WHERE db_monitoring_seqno = '{0}';
                            '''.format(monitor_id)
                        cursor.execute(sql)
                        conn.commit()
                        
                        # 히스토리 저장
                        sql = '''
                                INSERT INTO db_monitoring_history
                                (db_monitoring_group,db_monitoring_seqno,server_list_seqno,monitoring_code_seqno,action_type,monitoring_num,monitoring_threshold,monitoring_at,msg_content,alert_term,check_count_threshold,check_count_current,monitoring_schedule)
                                VALUES ('{0}','{1}','{2}','{3}','C','{4}','{5}',now(),'{6}','{7}','{8}','{9}','{10}')
                            '''.format('Test', monitor_id, server_list_seqno, monitoring_code_seqno, thread_count, threshold_num, 'CURLOPT_POSTFIELDS', alert_term, check_count_threshold, check_count_current, monitoring_schedule)
                        cursor.execute(sql)
                        conn.commit()
                        
                        print(dbname + " Problem (Just Checked) " + str(check_count_current) + "/" + str(check_count_threshold))
                
                else:
                    # 계속 에러중이네... check count 값만 늘려두자.
                    sql = '''
                        UPDATE db_monitoring
                        SET check_count_current = check_count_current + 1
                        WHERE db_monitoring_seqno = '{0}';
                        '''.format(monitor_id)
                    cursor.execute(sql)
                    conn.commit()
                    
                    # 히스토리 저장
                    sql = '''
                            INSERT INTO db_monitoring_history
                            (db_monitoring_group,db_monitoring_seqno,server_list_seqno,monitoring_code_seqno,action_type,monitoring_num,monitoring_threshold,monitoring_at,msg_content,alert_term,check_count_threshold,check_count_current,monitoring_schedule)
                            VALUES ('{0}','{1}','{2}','{3}','PR','{4}','{5}',now(),'{6}','{7}','{8}','{9}','{10}')
                        '''.format('Test', monitor_id, server_list_seqno, monitoring_code_seqno, thread_count, threshold_num, 'CURLOPT_POSTFIELDS', alert_term, check_count_threshold, check_count_current, monitoring_schedule)
                    cursor.execute(sql)
                    conn.commit()
                    
                    print(dbname + " Problem (Repeated) " + str(check_count_current) + "/" + str(check_count_threshold))

# 종료