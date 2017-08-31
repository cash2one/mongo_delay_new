import pymysql,os,sys
pymysql.install_as_MySQLdb()
cur = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(cur)