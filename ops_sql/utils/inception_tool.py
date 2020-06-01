#coding=utf-8

import pymysql


def table_structure(db_conn, db_name, sql_content):
    # 目标数据库连接，sql语句
    sql = '/* %s */\
      inception_magic_start;\
      use %s; %s inception_magic_commit;' % (db_conn, db_name, sql_content)
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', passwd='', port=6669, db='', use_unicode=True, charset="utf8")  # 连接inception
        cur = conn.cursor()  #游标
        cur.execute(sql)     #执行
        result = cur.fetchall()  #接收全部的返回结果行
        cur.close()
        conn.close()
        status = 0
    except pymysql.Error as e:
        result = ["Mysql Error %d: %s" % (e.args[0], e.args[1])]
        status = -1
    return result, status

    #定义连接到回滚库, 建立连接
def get_bak(sql, db_name=''):   #host='127.0.0.1' 根据/etc/inc.cnf中inception_remote_backup_host=127.0.0.1定义
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db=db_name, charset='utf8')
    conn.autocommit(True)  #自动提交
    cur = conn.cursor()    #游标
    cur.execute(sql)       #执行
    return cur.fetchall()
