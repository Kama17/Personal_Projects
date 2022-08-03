from app import db
import csv
from app import session
from sqlalchemy import MetaData, and_, Table,Column,Integer,ForeignKey
from flask_sqlalchemy import declarative_base
from sqlalchemy.orm import relationship,backref


metadata = MetaData(db.engine)
Base = declarative_base()


class WIP(db.Model):
	__tablename__ = "WIP"

	id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
	WEEK_NUMBER = db.Column(db.Integer, nullable = False)
	WIP_ENTITY_NAME = db.Column(db.Integer, nullable = False)
	PART_NUMBER = db.Column(db.Integer, nullable = False)
	PART_DESCRIPTION = db.Column(db.String, nullable = False)
	QUANTITY = db.Column(db.Integer,nullable = True)
	DEPARTMENT_CLASS = db.Column(db.String, nullable = False)
	DEPARTMENT = db.Column(db.String, nullable = False)
	OPERATION_DESCRIPTION = db.Column(db.String, nullable = False)
	PARTS_PER_HOUR = db.Column(db.Integer, nullable = False)

	parent_id = db.Column(db.Integer, db.ForeignKey("WIP_ROUTINGS.id"))
	parent = db.relationship("wipRoutings", backref=backref("WIP", uselist=False))

	def loadWIP(self, WIP_path):
		WIP.query.delete()

		#load new table from csv file
		with open(WIP_path,"r") as csvfile:
		    file = csv.reader(csvfile)
		    for row in file:
		    	
	        	insert = WIP(WEEK_NUMBER = row[0] ,
			        		WIP_ENTITY_NAME = row[1],
			        		PART_NUMBER  = row[2],
			        		PART_DESCRIPTION = row[3],
			        		QUANTITY = row[4],
			        		DEPARTMENT_CLASS = row[6],
			        		DEPARTMENT  = row[7],
			        		OPERATION_DESCRIPTION  =row[11],
			        		PARTS_PER_HOUR  =row[14])
	        	db.session.add(insert)
		    db.session.commit()


association_table = db.Table(
    "routings_to_completions",
    db.Column("wipRoutings_id",db.Integer, db.ForeignKey("WIP_ROUTINGS.id"), primary_key=True),
    db.Column("wipComplete_id",db.Integer, db.ForeignKey("WIP_COMPLETION.id"), primary_key=True),
)


class wipRoutings(db.Model):
	__tablename__ = "WIP_ROUTINGS"

	id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
	WEEK_NUMBER = db.Column(db.Integer, nullable = False)
	WIP_ENTITY_NAME = db.Column(db.Integer, nullable = False)
	PART_NUMBER = db.Column(db.Integer, nullable = False)
	PART_DESCRIPTION = db.Column(db.String, nullable = False)
	OPERATION_DESCRIPTION = db.Column(db.String, nullable = False)
	QUANTITY = db.Column(db.Integer, nullable = False)
	COMPLETE = db.Column(db.Integer, nullable = True)
	START_DATE = db.Column(db.DateTime, nullable = True)
	STATUS = db.Column(db.String, nullable = True)
	OPERATOR_NAME = db.Column(db.String)
	ADDITIONAL_QUANTITY = db.Column(db.Integer)
	SCRAP_QUANTITY = db.Column(db.Integer)
	PARTS_PER_HOUR = db.Column(db.Integer, nullable = False)

	associate_completions = db.relationship(
        "wipCompletion", secondary=association_table,  backref="all_completions"
    )



	

	def refreshWIPTable(self):
		wip_data = wipRoutings.query.filter_by(STATUS = 'In Progress').all()
		return wip_data


class wipCompletion(db.Model):
	__tablename__ = "WIP_COMPLETION"

	id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
	WEEK_NUMBER = db.Column(db.Integer, nullable = False)
	WIP_ENTITY_NAME = db.Column(db.Integer, nullable = False)
	PART_NUMBER = db.Column(db.Integer, nullable = False)
	OPERATION_DESCRIPTION = db.Column(db.String, nullable = False)
	QUANTITY = db.Column(db.Integer)
	COMPLETE = db.Column(db.Integer)
	DATE_START = db.Column(db.DateTime)
	DATE_COMPLETE = db.Column(db.DateTime)
	PARTS_PER_HOUR = db.Column(db.Integer, nullable = False)
	OPERATOR_NAME = db.Column(db.String, nullable = False)
	STATUS = db.Column(db.String, nullable = True)
	DOWNTIME_REASON = db.Column(db.String)
	DOWNTIME = db.Column(db.Integer)
	SCRAP_REASON = db.Column(db.String)
	SCRAP_QUANTITY = db.Column(db.Integer)

	

	def insertToWIPcompletion(self, job_rec_book_out,job_out_qty, time):

		insert = wipCompletion(WEEK_NUMBER = job_rec_book_out.WEEK_NUMBER, WIP_ENTITY_NAME = job_rec_book_out.WIP_ENTITY_NAME
			, PART_NUMBER = job_rec_book_out.PART_NUMBER, OPERATION_DESCRIPTION = job_rec_book_out.OPERATION_DESCRIPTION,
			 QUANTITY = job_out_qty, DATE_COMPLETE = time)

		db.session.add(insert)
		db.session.commit()



def tableCreate(file, file_name, week, new_plan):


	SessionTable.metadata.create_all(db.engine)

	for row in new_plan.iterrows():
	    if (row[1][0] == int(week)) and (row[1][7] != 'WELD DEPT') and (row[1][7] !='PAINT CELL'):
	        insert_to_table = SessionTable(WEEK_NUMBER = row[1][0], WIP_ENTITY_NAME = row[1][1],
			  			PART_NUMBER =  row[1][2], PART_DESCRIPTION = row[1][3],ROUTING = row[1][7],QUANTITY = row[1][4])
	        db.session.add(insert_to_table)

	db.session.commit()
	joined_table = db.session.query(SessionTable,wipRoutings).outerjoin(wipRoutings,and_(wipRoutings.WIP_ENTITY_NAME == SessionTable.WIP_ENTITY_NAME, wipRoutings.OPERATION_DESCRIPTION == SessionTable.ROUTING)).all()


	dep_routing = db.session.query(SessionTable.ROUTING.distinct()).order_by(SessionTable.ROUTING).all()

	SessionTable.metadata.drop_all(db.engine)
	db.session.close()
	return joined_table , dep_routing


class SessionTable(Base):

	__tablename__ = 'sessionTable'
	id = db.Column(db.Integer, primary_key = True)
	WEEK_NUMBER = db.Column(db.Integer)
	WIP_ENTITY_NAME = db.Column(db.Integer)
	PART_NUMBER = db.Column(db.Integer)
	PART_DESCRIPTION =db.Column(db.String)
	ROUTING = db.Column(db.String)
	QUANTITY = db.Column(db.Integer)
	__table_args__ = {'extend_existing': True}

class operatorNames(db.Model):
	__tablename__ = 'OPERATOR_NAMES'
	id = db.Column(db.Integer, primary_key = True)
	FIRST_NAME = db.Column(db.String , nullable = False)
	LAST_NAME = db.Column(db.String, nullable = False)
	ID_NUMBER = db.Column(db.Integer)

class downtimeReason(db.Model):
	__tablename__ = 'DOWNTIME_REASON'
	id = db.Column(db.Integer, primary_key = True)
	REASON = db.Column(db.Integer , nullable = False)

class scrapReason(db.Model):
	__tablename__ = 'SCRAP_REASON'
	id = db.Column(db.Integer, primary_key = True)
	REASON = db.Column(db.Integer , nullable = False)

class password(db.Model):
	__tablename__ = 'PASSWORD'
	id = db.Column(db.Integer, primary_key = True)
	ADMIN = db.Column(db.String, nullable = False)
	PASSWORD = db.Column(db.String, nullable = False)


	
def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict


