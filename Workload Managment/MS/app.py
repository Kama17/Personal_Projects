from flask import Flask, flash, render_template, request,redirect,session, url_for
import os
import pandas as pd
from datetime import datetime
import webbrowser
from waitress import serve
from flask_sqlalchemy import SQLAlchemy
import csv
from sqlalchemy import union_all


app = Flask(__name__)
app.secret_key = '125987'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import * 


WIP_path = (r'..\Supply All Departments.csv')
db_path = (r'database\db.db')


@app.route('/enter', methods = ['POST'])
def enter():

	return render_template('enteroperator.html')

@app.route('/addoperator', methods = ['POST'])
def addoperator():

	first_name = request.form['firstname']
	last_name = request.form['lastname']
	action = request.form['action']

	check_operator = operatorNames.query.filter_by(FIRST_NAME = first_name, LAST_NAME = last_name).first()
	if action == 'submit':
		if check_operator:
			flash(f'Operator {first_name} {last_name} already exists.')
			return render_template('enteroperator.html')
		else:

			add_operator = operatorNames(FIRST_NAME = first_name, LAST_NAME = last_name)
			db.session.add(add_operator)
			db.session.commit()
			flash(f'Operator {first_name} {last_name} added.')
			return render_template('enteroperator.html')

	elif action == 'delete':
		if check_operator:
			delete_operator = operatorNames.query.filter_by(FIRST_NAME = first_name, LAST_NAME = last_name).first()
			db.session.delete(delete_operator)
			db.session.commit()
			flash(f'Operator {first_name} {last_name} deleted.')
			return render_template('enteroperator.html')
		flash(f'Operator {first_name} {last_name} does not exists.')
	return render_template('enteroperator.html')



@app.route('/downtimereason', methods = ['POST'])
def downtime():
	reason = request.form['downtimereason']
	action = request.form['action']

	if action == 'submit':
		add_downtime = downtimeReason(REASON = reason)
		db.session.add(add_downtime)
		db.session.commit()
		flash(f'Reason Added')
		return render_template('enteroperator.html')

	elif action == 'delete':
		delete_reason = downtimeReason.query.filter_by(REASON = reason).first()
		db.session.delete(delete_reason)
		db.session.commit()
		flash(f'Downtime reason deleted')
		return render_template('enteroperator.html')


@app.route('/scrapreason', methods = ['POST'])
def scrapreason():
	reason = request.form['scrapreason']
	action = request.form['action']

	if action == 'submit':
		add_scrap = scrapReason(REASON = reason)
		db.session.add(add_scrap)
		db.session.commit()
		flash(f'Scrap reason added')
		return render_template('enteroperator.html')

	elif action == 'delete':
		delete_reason = scrapReason.query.filter_by(REASON = reason).first()
		db.session.delete(delete_reason)
		db.session.commit()
		flash(f'Reason Deleted')
		return render_template('enteroperator.html')

@app.route('/export')
def export():
	data = wipCompletion.query.filter_by(STATUS = 'Complete').all()
	data_list = [to_dict(item) for item in data]
	
	
	for i in data_list:
		if i['COMPLETE'] != 0:
			i['TOTAL_TIME'] = i['DATE_COMPLETE'] - i['DATE_START']
			time_number = i['DATE_COMPLETE'] - i['DATE_START']
			time_in_hours = time_number.total_seconds()/3600
			i['PERFORMANCE %'] = round(((i['COMPLETE'] / (time_in_hours *i['PARTS_PER_HOUR'])) * 100),2)
			i['QUALITY %'] = round((((i['COMPLETE'] - i['SCRAP_QUANTITY']) / i['COMPLETE']) * 100),2)
			i['AVAILABILITY %'] = round((((time_in_hours -(i['DOWNTIME']/60)) / time_in_hours) * 100),2)
			i['OEE %'] = round(((i['PERFORMANCE %']/100) * (i['QUALITY %']/100) * (i['AVAILABILITY %']/100))*100,2)
		else:
			i['TOTAL_TIME'] = 0
			time_number = 0
			time_in_hours = 0
			i['PERFORMANCE %'] = 0
			i['QUALITY %'] = 0
			i['AVAILABILITY %'] = 0
			i['OEE %'] = 0
	df = pd.DataFrame(data_list)
	df.to_excel(r'../'+'Transactions_Table.xlsx', index=False)
	completeTable = wipCompletion.query.filter_by(STATUS = 'Complete').all()
	flash(f'File exported successfully')
	return render_template('transaction.html' ,wip = completeTable)

@app.route('/')
def login():
	session.clear()
	WIP().loadWIP(WIP_path)
	return render_template('login.html')


@app.route('/operator' ,methods = ['GET', 'POST'])
def operator_login():
	return render_template('operator.html')


@app.route('/index')
def index():
	wip_modif = datetime.fromtimestamp(os.stat(WIP_path).st_mtime).strftime('%d-%m-%Y %H:%M')

	in_progress = wipRoutings.query.filter_by(STATUS = 'In Progress').distinct().subquery()
	get_wip = wipRoutings.query.filter_by(WIP_ENTITY_NAME = in_progress.c.WIP_ENTITY_NAME).all()

	a= set([i.WIP_ENTITY_NAME for i in get_wip])
	c = [[w for w in get_wip if w.WIP_ENTITY_NAME == i] for  i in a]


	if request.method == 'POST':
			
		return render_template('index.html',wip_modif = wip_modif,routings = update_wip[1], update_wip =  wipRoutings.query.filter_by(STATUS = 'In Progress').all())

	return render_template('index.html', wip_modif = wip_modif,update_wip = c)

@app.route('/bend', methods = ['GET', 'POST'])
def bend():
	global FILE
	global dep_routing
	global file
	global file_name
	global week
	global new_plan


	if request.method == 'POST':
		#Loading complately new week
		file = request.files['plan']
		week = int(file.filename.split()[1])
		file_name = file.filename.split(' ')[:3]
		file_name = '-'.join(file_name)
		file = file
		new_plan = pd.read_excel(file)
		session['current_week'] = file_name
		#Create table
		table, dep_routing = tableCreate(file,file_name, week, new_plan)
		FILE = table
		return render_template('bend.html',file_value = FILE, name = file_name, file = table, title = file_name, dep_routing = dep_routing)

	# Upload week for current session variable
	else:
		if session:

			table, dep_routing = tableCreate(file,file_name, week, new_plan)
			FILE = table
			return render_template('bend.html',file_value = FILE, name = file_name, file = table, title = file_name, dep_routing = dep_routing)

			#return render_template('bend.html',file = FILE,dep_routing = dep_routing)#, dep_routing = dep_routing)
		return render_template('bend.html')




@app.route('/booking', methods = ['GET', 'POST'])
def booking():

	in_progress = wipRoutings.query.filter_by(STATUS = 'In Progress').distinct().subquery()
	get_wip = wipRoutings.query.filter_by(WIP_ENTITY_NAME = in_progress.c.WIP_ENTITY_NAME).all()

	a = set([i.WIP_ENTITY_NAME for i in get_wip])
	c = [[w for w in get_wip if w.WIP_ENTITY_NAME == i] for  i in a]

	action = ""
	job_no =  request.args.get('job_no')

	from_wip_routings = wipRoutings.query.filter_by(WIP_ENTITY_NAME = job_no).all()
	from_wip = WIP.query.filter_by(WIP_ENTITY_NAME = job_no).all()
	op_names = operatorNames.query.all()

		

	if from_wip_routings: 
		action = "update"
		return render_template('index.html', 
			job_rec = from_wip_routings, 
			data0 = from_wip_routings[0].WEEK_NUMBER,
			data1 = from_wip_routings[0].WIP_ENTITY_NAME,
			data2 = from_wip_routings[0].PART_NUMBER,
			data3 = from_wip_routings[0].PART_DESCRIPTION,
			data4 = from_wip_routings[0].QUANTITY,
			action = action,op_names = op_names,
			update_wip = c) # Set value action to insert and pass to submit route
			#update_wip =  DBManage().refreshWIPTable())

	elif from_wip:
		
		action = "insert" # Set te value action to update and pass to submit route

		return render_template('index.html', 
			job_rec = from_wip,
			data0 = from_wip[0].WEEK_NUMBER,
			data1 = from_wip[0].WIP_ENTITY_NAME,
			data2 = from_wip[0].PART_NUMBER,
			data3 = from_wip[0].PART_DESCRIPTION,
			data4 = from_wip[0].QUANTITY,
			action = action, op_names = op_names,
			update_wip = c)
	return redirect('index')


@app.route('/<action>/bookout', methods = ['GET', 'POST'])
def bookout(action):
	
	in_progress = wipRoutings.query.filter_by(STATUS = 'In Progress').distinct().subquery()

	get_wip = wipRoutings.query.filter_by(WIP_ENTITY_NAME = in_progress.c.WIP_ENTITY_NAME).all()


	a= set([i.WIP_ENTITY_NAME for i in get_wip])
	c = [[w for w in get_wip if w.WIP_ENTITY_NAME == i] for  i in a]

	if request.method == 'POST':
		downtime_reason = downtimeReason.query.all()
		scrap_reason = scrapReason.query.all()
		job_no_out =  request.form['job_no_book_out']


		job_rec_book_out = wipRoutings.query.filter_by(WIP_ENTITY_NAME = job_no_out, STATUS = 'In Progress').first()

		if job_rec_book_out == None:
			return redirect('/index')
		
		return render_template('index.html', 
				job_rec_book_out = job_rec_book_out,
				update_wip = c, 
				action = 'search', downtime_reason = downtime_reason,scrap_reason = scrap_reason)
	
	elif request.method == 'GET':
		job_out_qty =  request.args.get('job_bookout_qty')
		job_no_out =  request.args.get('job_number')
		job_bookout_routing = request.args.get('job_bookout_routing')
		name = request.args.get('name')
		reason = request.args.get('downtime_reason')
		downtime = request.args.get('downtime')
		add_qty = request.args.get('add_qty')
		scrap_qty = request.args.get('scrap_qty')
		scrap_reason =request.args.get('scrap_reason')

		job_rec_book_out = wipRoutings.query.filter_by(WIP_ENTITY_NAME = job_no_out,OPERATION_DESCRIPTION = job_bookout_routing, STATUS = 'In Progress' ).first()
		

		if job_rec_book_out.QUANTITY == (job_rec_book_out.COMPLETE + int(job_out_qty)):

			job_rec_book_out.STATUS = 'Complete'
			job_rec_book_out.OPERATOR_NAME = ''
			job_rec_book_out.DOWNTIME_REASON =reason
			job_rec_book_out.DOWNTIME = downtime
			job_rec_book_out.SCRAP_QUANTITY = job_rec_book_out.SCRAP_QUANTITY + int(scrap_qty)
			job_rec_book_out.START_DATE = datetime(1, 1, 1, 0, 0)
		else:
			job_rec_book_out.OPERATOR_NAME = ''
			job_rec_book_out.STATUS = ''
			job_rec_book_out.START_DATE = datetime(1, 1, 1, 0, 0)
			job_rec_book_out.SCRAP_QUANTITY = job_rec_book_out.SCRAP_QUANTITY + int(scrap_qty)

		job_rec_book_out.COMPLETE += int(job_out_qty)

		if 'SAW' in job_rec_book_out.OPERATION_DESCRIPTION.upper():

			additional = wipRoutings.query.filter_by(WIP_ENTITY_NAME = job_no_out).all()
			for job in additional:
				job.ADDITIONAL_QUANTITY = int(add_qty)




		#db.session.commit()

		update_completion = wipCompletion.query.filter_by(WIP_ENTITY_NAME = job_no_out, STATUS = 'In Progress', OPERATION_DESCRIPTION = job_bookout_routing, OPERATOR_NAME = name).first()
		update_completion.DATE_COMPLETE = datetime.now()
		update_completion.COMPLETE = job_out_qty
		update_completion.STATUS = 'Complete'
		update_completion.DOWNTIME_REASON = reason
		update_completion.DOWNTIME = downtime
		update_completion.SCRAP_REASON = scrap_reason
		update_completion.SCRAP_QUANTITY = int(scrap_qty)

		db.session.commit()

		additional = wipRoutings.query.filter_by(WIP_ENTITY_NAME = job_no_out).all()
		total_scrap = wipCompletion.query.filter_by(WIP_ENTITY_NAME = job_no_out).all()

		sum_scrap_total = 0
		for i in total_scrap:
			sum_scrap_total += i.SCRAP_QUANTITY

		for i in additional:
			if i.STATUS != "Complete":
				i.ADDITIONAL_QUANTITY = additional[0].ADDITIONAL_QUANTITY -  sum_scrap_total

		db.session.commit()


		

		render_template('index.html', update_wip = c)
		
	return redirect('/index')

@app.route('/<action>/submit', methods = ['POST','GET'])
def submit(action):

	sub = request.args.getlist('no')
	checkbox_checked = request.args.get('check_box')
	name = request.args.get('name')
	parts_per_hour = request.args.get('part_per_hour')

	#Check if routing check box was selected
	if checkbox_checked == None:
		return render_template('index.html', message = 'Please select routing.')# ,update_wip = DBManage().refreshWIPTable())

	#Check if job already started	
	check_if_exists = wipRoutings.query.filter_by(WIP_ENTITY_NAME = sub[0], STATUS = 'In Progress').first()
	if check_if_exists:
		return render_template('index.html',message = 'Job already started.')# ,update_wip = DBManage().refreshWIPTable())
	

	if action == 'insert':


		from_wip = WIP.query.filter_by(WIP_ENTITY_NAME = sub[0]).all()

		insert_start_date = wipCompletion(WEEK_NUMBER = sub[3] ,WIP_ENTITY_NAME = sub[0], PART_NUMBER = sub[1], 
										QUANTITY = sub[2],OPERATION_DESCRIPTION = checkbox_checked, DATE_START = datetime.now(), 
										OPERATOR_NAME = name, STATUS = 'In Progress', SCRAP_QUANTITY = 0, PARTS_PER_HOUR = float(parts_per_hour))
		for wip_record in from_wip:	
			if wip_record.DEPARTMENT == checkbox_checked:

				insert_record = wipRoutings(WIP_ENTITY_NAME = wip_record.WIP_ENTITY_NAME,PART_NUMBER = wip_record.PART_NUMBER, 
										QUANTITY = wip_record.QUANTITY, WEEK_NUMBER = wip_record.WEEK_NUMBER, PART_DESCRIPTION = wip_record.PART_DESCRIPTION,
										OPERATION_DESCRIPTION = wip_record.DEPARTMENT, COMPLETE = 0,START_DATE = datetime.now() ,PARTS_PER_HOUR = wip_record.PARTS_PER_HOUR ,STATUS = 'In Progress' ,OPERATOR_NAME = name,
										ADDITIONAL_QUANTITY = 0,SCRAP_QUANTITY = 0)

				insert_record.associate_completions.append(insert_start_date)
			else:
				insert_record = wipRoutings(WIP_ENTITY_NAME = wip_record.WIP_ENTITY_NAME,PART_NUMBER = wip_record.PART_NUMBER, 
										QUANTITY = wip_record.QUANTITY, WEEK_NUMBER = wip_record.WEEK_NUMBER, PART_DESCRIPTION = wip_record.PART_DESCRIPTION,
										OPERATION_DESCRIPTION = wip_record.DEPARTMENT,COMPLETE = 0,START_DATE = datetime.now(),PARTS_PER_HOUR = wip_record.PARTS_PER_HOUR, STATUS = '',ADDITIONAL_QUANTITY = 0,SCRAP_QUANTITY = 0)

			
			
			db.session.add(insert_start_date)
			db.session.add(insert_record)
			
	elif action == 'update':

		update_record = wipRoutings.query.filter_by(WIP_ENTITY_NAME = sub[0], OPERATION_DESCRIPTION = checkbox_checked).first()
		update_record.STATUS = 'In Progress'
		update_record.START_DATE = START_DATE = datetime.now()
		update_record.OPERATOR_NAME = request.args.get('name')

		insert_start_date = wipCompletion(WEEK_NUMBER = sub[3] ,WIP_ENTITY_NAME = sub[0], PART_NUMBER = sub[1],QUANTITY = sub[2],
										OPERATION_DESCRIPTION = checkbox_checked, DATE_START = datetime.now(), OPERATOR_NAME = name,PARTS_PER_HOUR = update_record.PARTS_PER_HOUR ,STATUS = 'In Progress')
		
		update_record.associate_completions.append(insert_start_date)

		db.session.add(insert_start_date)
		

	db.session.commit()

	render_template('index.html')
	return redirect('/index')


@app.route('/trans', methods = ['GET'])
def trans():

	completeTable = wipCompletion.query.filter_by(STATUS = 'Complete')
	
	return render_template('transaction.html',wip = completeTable)
 

if __name__ == '__main__':
	print('Application running...')
	print('DO NOT CLOSE THIS WINDOW.')
	print('Close this window after closing the browser.')
	print('If browser do not open copy and past this URL: http://127.0.0.1:5000')
	webbrowser.open('http://127.0.0.1:5000', new = 2)
	db.create_all()
	serve(app, port = 5000)
	#app.run(debug = True,threaded=True)
	
