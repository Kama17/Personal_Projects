
import sqlite3 as sql
from flask import request
from databaseManage import  DBManage



class bookIn():
	def __init__(self):
		#self.DBManage = DBManage().updateWIPTable()
		self.path = r'C:\Users\2609\Desktop\MS\database\db.db'
		self.table_names = ['JOB_DETAILS','JOB_ROUTING']
		self.conn = sql.connect(self.path) # connection string neet to be change
		self.cur = self.conn.cursor()


	def get_job_number(self):

		job_number =  request.args['job_no']
		return job_number

	def searchWIP(self,job_number):
	
		self.cur.execute(f"SELECT * FROM WIP WHERE WIP_ENTITY_NAME = '{job_number}' and DEPARTMENT != 'WELD DEPT';")
		records = self.cur.fetchall()
		self.conn.close()

		return records

	def search_weekly_supply(self,job_number):

		job_record = []

		#check if record exists
		self.cur.execute(f"SELECT * FROM JOB_DETAILS WHERE WIP_ENTITY_NAME = '{job_number}';")
		check_records = self.cur.fetchone()

		if check_records == None:
			self.conn.close()
			
			return None
		# retrive date from the tables
		else:
			for table in self.table_names:
				self.cur.execute(f"SELECT * FROM {table} WHERE WIP_ENTITY_NAME = '{job_number}';")
				job_record.append(self.cur.fetchall())
							
		self.conn.close()	
		return job_record
		
	




