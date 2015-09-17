from flask import Flask, jsonify, request
from pymongo import MongoClient
from config import db
from config import gcmKey
from gcm import GCM
import json
app = Flask(__name__)

@app.route('/updateTT', methods=['POST'])
def update_timetable():
	if request.method == "POST":
		data = request.json
		dt = jsonify(data)
		b =  data['batch']
		if data['batch'] == int(b):
			print int(b)
		
		gcm = GCM(gcmKey)
		users = db.users.find({"batch" : b})
		#print users
		reg_ids = []
		for i in users:
			reg_ids.append(i['registration_id'])
			#print i, "lol"

		print len(reg_ids)
		response = gcm.json_request(registration_ids=reg_ids, data=data['data'])
		return "YOLO"+"\n"


@app.route('/register', methods=['POST'])
def add_user():
	if request.method == "POST":
		rollno = request.form['rollnumber']
		reg_id = request.form['regno']
		print request.form
		batch_det = rollno[:-3]
		db.users.insert({
				"rollnumber": rollno,
				"registration_id": reg_id,
				"batch": batch_det
				})
		return jsonify( ( { "Signed Up" : 1 } ) )

# Route is for backing up attendance
@app.route('/backup', methods= ['POST'] )
def backup():
	if request.method == "POST":
		data_array = request.json
		for data in data_array:
			attendance = db.attendance.find_one( { 
						 "rollno" : data['rollno'],
						 "date-time" : dat['date-time'],
						 "subject" : data['subject']
					 	})
			if attendance is None:
				try:
					db.attendance.insert(data)
				except:
					return jsonify( ( { "BackedUp": 0 } ) )
			else:
				try:
					db.attendance.remove(attendance)
					db.attendance.insert(data)
				except:
					return jsonify( ( { "BackedUp": 0 } ) )
		
		return jsonify( ( { "BackedUp": 1 } ) )

# To get attendance of a particular user
@app.route('/attendance', methods = ['POST'])
def get_attendance():
	if request.method == "POST":
		rollno = request.json['rollno']
		try:
			attendance = db.attendance.find( { "rollno" : rollno } )
			a = []
			for i in attendance:
				temp = {
					"rollno" : i['rollno'],
					"subject" : i['subject'],
					"date-time" : i['date-time'],
					"present" : i['present']
				}
				a.append(temp)
			a = json.dumps(a)
			return a
		except:
			return jsonify ( ( { "Error": 1 } ) )

if __name__ =="__main__":
  app.run(debug=True)

