#website for truss
from flask import *
import sqlite3
from flask_socketio import SocketIO, join_room, leave_room
import uuid
import math



app = Flask(__name__)
socketio = SocketIO(app)



app.secret_key='asdsdfsdfs13sdf_df%&'


#homepage
@app.route('/')
def home_page():
	return render_template('homepage.html')


#education page
@app.route('/education')
def education():
	return render_template('education.html')

#online program page
@app.route('/education_online')
def education_online():
	return render_template('education_online.html')

#offline program page
@app.route('/education_offline')
def education_offline():
	return render_template('education_offline.html')

#download material page
@app.route('/education_download')
def education_download():
	return render_template('education_download.html')

#recorded classes page
@app.route('/education_recordedclasses')
def education_recordedclasses():
	return render_template('education_recordedclasses.html')

#live classes page
@app.route('/education_liveclasses')
def education_liveclasses():
	return render_template('education_liveclasses.html')

#login or sign up option page
@app.route('/lors')
def lors():
	return render_template('LorS.html')

#sign up page
@app.route('/signup')
def signup():
	return render_template('signup.html')

#route to add record to a database during signup
@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
	if request.method == 'POST':
		username = request.form['username']
		password1 = request.form['password1']
		password2 = request.form['password2']
		age=request.form['age']
		email = request.form['email']
		archetype = request.form['archetype']
		role= request.form['role']
		location = request.form['location']
		if password1 == password2:
			try:
				con = sqlite3.connect("truss_users.sqlite3")
				cur = con.cursor()
				cur.execute("INSERT into user (username, password, age, email, archetype, role, location) values (?,?,?,?,?,?,?)",(username, password1, age, email, archetype, role, location))
				con.commit()
				msg="Record added successfully"

				

				if role == 'Founder':
					return render_template('founder_signup.html')
				elif role == 'Mentor':
					return render_template('mentor_signup.html')
				else:
					return render_template('cofounder_signup.html')
			except:
				con.rollback()
				msg="*** Username already exists ***"
				return render_template("signup.html",msg = msg)
			finally:
				cur.execute('SELECT id FROM user WHERE username = (?) AND password = (?)', (username, password1))
				global user_id
				user_id=cur.fetchone()
				user_id=user_id[0]
				con.close()

		else:
			error="*** Passwords do not match ***"
			return render_template("signup.html",error = error)


@app.route('/addfounder',methods = ['POST', 'GET'])
def addfounder():
	if request.method == 'POST':
		name_startup = request.form['nameofstartup']
		stage = request.form['stage']
		startup_pitch = request.form['startup_pitch']
		person_pitch = request.form['person_pitch']
		industry = request.form['industry']
		instituon = request.form['instituon']
		achievements=request.form['achievements']
		have_skill=request.form['have_skill']
		want_skill=request.form['want_skill']

		try:
			con = sqlite3.connect("truss_users.sqlite3")
			cur = con.cursor()
			cur.execute("INSERT into founder (id, name_startup, stage, startup_pitch, person_pitch, industry, instituon, achievements, have_skill, want_skill) values (?,?,?,?,?,?,?,?,?,?)",(user_id, name_startup, stage, startup_pitch, person_pitch, industry, instituon, achievements, have_skill, want_skill))
			con.commit()
			msg="Record added successfully"
			return render_template('relogin.html')
		except:
			con.rollback()
			msg="Error"
			return render_template("founder_signup.html",msg = msg)
		finally:
			con.close()

#the cofounder part of signup
@app.route('/addcofounder',methods = ['POST', 'GET'])
def addcofounder():
	if request.method == 'POST':
		pitch = request.form['pitch']
		industry = request.form['industry']
		instituon = request.form['instituon']
		achievements=request.form['achievements']
		have_skill=request.form['have_skill']

		try:
			con = sqlite3.connect("truss_users.sqlite3")
			cur = con.cursor()
			cur.execute("INSERT into cofounder (id, pitch, industry, instituon, achievements, have_skill) values (?,?,?,?,?,?)",(user_id, pitch, industry, instituon, achievements, have_skill))
			con.commit()
			msg="Record added successfully"
			return render_template('relogin.html')
		except:
			con.rollback()
			msg="Error"
			return render_template("cofounder_signup.html",msg = msg)
		finally:
			con.close()

#the mentor part of the sign up
@app.route('/addmentor',methods = ['POST', 'GET'])
def addmentor():
	if request.method == 'POST':
		industry = request.form['industry']
		instituon = request.form['instituon']
		experience = request.form['experience']
		pitch = request.form['pitch']
		have_skill=request.form['have_skill']

		try:
			con = sqlite3.connect("truss_users.sqlite3")
			cur = con.cursor()
			cur.execute("INSERT into mentor (id, industry, experience, instituon, pitch, have_skill) values (?,?,?,?,?,?)", (user_id, industry, experience, instituon, pitch, have_skill))
			con.commit()
			msg="Record added successfully"
			return render_template('relogin.html')
		except:
			con.rollback()
			msg="Error"
			return render_template("cofounder_signup.html",msg = msg)
		finally:
			con.close()


#Login page
@app.route('/login',methods = ['POST', 'GET'])
def login():
	msg=''
	if  request.method == 'POST':
		global user
		user = request.form['username']
		passw = request.form['password']
		session['user_id']=user
		con = sqlite3.connect("truss_users.sqlite3")
		cur = con.cursor()
		cur.execute('SELECT * from user WHERE username = (?) AND password = (?)', (user, passw))
		account=cur.fetchone()
		if account != None:
			session['user_id']=account[0]
			global user_id
			user_id=account[0]
			role=account[4]
			return redirect(url_for('finder'))
		else:
			msg = '*** Incorrect username or password ***'
		con.close()
	return render_template('login.html',msg=msg)


@app.route('/finder')
def finder():

	con = sqlite3.connect("truss_users.sqlite3")
	cur = con.cursor()
	user_id=session.get("user_id")
	cur.execute('SELECT username, age, role, location, id FROM user WHERE (role == "Founder" OR role =="Co-Founder") and (user.id != (?)) ORDER BY user.id DESC', (user_id,))
	everyone=cur.fetchall()
	return render_template('finder.html', everyone=everyone)

#to view others profile
@app.route('/profile/<request_id>')
def profile(request_id):
	requested_id=request_id
	con = sqlite3.connect("truss_users.sqlite3")
	cur = con.cursor()
	cur.execute('SELECT ROLE from user where user.id==(?)', (requested_id,))
	profile_role = cur.fetchone()
	if (profile_role[0]=='Founder'):
		cur.execute('SELECT * from user, founder WHERE user.id == founder.id and user.id==(?)', (requested_id,))
		profile_data=cur.fetchone()

		name=profile_data[1]
		email=profile_data[3]
		archetype=profile_data[5]
		age=profile_data[6]
		role='FOUNDER'
		name_startup=profile_data[9]
		stage=profile_data[10]
		startup_pitch=profile_data[11]
		industry=profile_data[12]
		instituon=profile_data[13]
		location=profile_data[7]
		person_pitch=profile_data[14]
		achievements=profile_data[15]
		have_skill=profile_data[16]
		want_skill=profile_data[17]

		return render_template('founder_dashboard.html', age=age, name=name, email=email, role=role, archetype=archetype, name_startup=name_startup, stage=stage, industry=industry, instituon=instituon, location=location, startup_pitch=startup_pitch, person_pitch=person_pitch, achievements=achievements, have_skill=have_skill, want_skill=want_skill)
	else:
		cur.execute('SELECT * from user, cofounder WHERE user.id == cofounder.id and user.id==(?)', (requested_id,))
		profile_data=cur.fetchone()

		name=profile_data[1]
		email=profile_data[3]
		archetype=profile_data[5]
		age=profile_data[6]
		role='CO-FOUNDER'
		pitch=profile_data[9]
		industry=profile_data[10]
		instituon=profile_data[11]
		location=profile_data[7]
		achievements=profile_data[12]
		have_skill=profile_data[13]

		return render_template('cofounder_dashboard.html', age=age, name=name, email=email, role=role, archetype=archetype, pitch=pitch, industry=industry, instituon=instituon, location=location, achievements=achievements, have_skill=have_skill)

#my profile
@app.route('/my_profile')
def my_profile():
	con = sqlite3.connect("truss_users.sqlite3")
	cur = con.cursor()
	cur.execute('SELECT ROLE from user where user.id==(?)', (user_id,))
	user_role = cur.fetchone()
	if (user_role[0]=='Founder'):
		cur.execute('SELECT * from user, founder WHERE user.id == founder.id and user.id==(?)', (user_id,))
		profile_data=cur.fetchone()

		name=profile_data[1]
		email=profile_data[3]
		archetype=profile_data[5]
		age=profile_data[6]
		role='FOUNDER'
		name_startup=profile_data[9]
		stage=profile_data[10]
		startup_pitch=profile_data[11]
		industry=profile_data[12]
		instituon=profile_data[13]
		location=profile_data[7]
		person_pitch=profile_data[14]
		achievements=profile_data[15]
		have_skill=profile_data[16]
		want_skill=profile_data[17]

		return render_template('myprofile_founder.html', age=age, name=name, email=email, role=role, archetype=archetype, name_startup=name_startup, stage=stage, industry=industry, instituon=instituon, location=location, startup_pitch=startup_pitch, person_pitch=person_pitch, achievements=achievements, have_skill=have_skill, want_skill=want_skill)
	elif(user_role[0]=='Co-Founder'):
		cur.execute('SELECT * from user, cofounder WHERE user.id == cofounder.id and user.id==(?)', (user_id,))
		profile_data=cur.fetchone()

		name=profile_data[1]
		email=profile_data[3]
		archetype=profile_data[5]
		age=profile_data[6]
		role='CO-FOUNDER'
		pitch=profile_data[9]
		industry=profile_data[10]
		instituon=profile_data[11]
		location=profile_data[7]
		achievements=profile_data[12]
		have_skill=profile_data[13]

		return render_template('myprofile_cofounder.html', age=age, name=name, email=email, role=role, archetype=archetype, pitch=pitch, industry=industry, instituon=instituon, location=location, achievements=achievements, have_skill=have_skill)

	else:
		cur.execute('SELECT * from user, mentor WHERE user.id == mentor.id and user.id==(?)', (user_id,))
		profile_data=cur.fetchone()

		name=profile_data[1]
		email=profile_data[3]
		archetype=profile_data[5]
		age=profile_data[6]
		role='MENTOR'
		industry=profile_data[8]
		experience=profile_data[9]
		instituon=profile_data[10]
		location=profile_data[11]
		pitch=profile_data[12]
		
		return render_template('myprofile_mentor.html', age=age, name=name, email=email, role=role, archetype=archetype, industry=industry,  experience=experience, instituon=instituon, location=location, pitch=pitch)





#networking page
@app.route('/networking')
def networking():
	return render_template('networking.html')

#redirection for sign-out
@app.route('/signout')
def signout():
	session["user_id"] = None
	user_id = None
	return redirect(url_for('home_page'))

#under develoupment page
@app.route('/udp')
def udp():
	return render_template('UDP.html')

#testing page
@app.route('/testing')
def testing():
	#ifofuser=user_id
	con = sqlite3.connect("truss_users.sqlite3")
	cur = con.cursor()
	cur.execute('SELECT username, age, role FROM user WHERE role == "Founder" OR role =="Co-Founder"')
	account=cur.fetchall()
	#number=account[0]-1
	rest='gle.co.in/'
	return render_template('testing.html',account=account,rest=rest)


#chat box 
@app.route('/chat')#@app.route('/chat/<requested_user>')
def chat():#requested_user
	#the room no and requested user id are the same as user id is unique and we can use that a room no
	room=1

	username=user
	if room:
		return render_template('chat.html', username=username, room=room)
	else:
		return redirect(url_for('finder'))

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'], data['room'], data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])

#request sent page
@app.route('/request_sent')
def request_sent():
	return render_template('request_sent.html')


#filtering
@app.route('/filter',methods = ['POST', 'GET'])
def filter():
	if  request.method == 'POST':
		role = request.form['role']
		location = request.form['location']
		skill_set = request.form['skill_set']
		archetype = request.form['archetype']

		con = sqlite3.connect("truss_users.sqlite3")
		cur = con.cursor()

		if(role=="founder"):
			cur.execute('SELECT * FROM "user", "founder" WHERE user.id==founder.id and ("location"== (?) and archetype == (?) and have_skill==(?))', (location, archetype, skill_set))
			everyone=cur.fetchall()
		else:
			cur.execute('SELECT * FROM "user", "cofounder" WHERE user.id==cofounder.id and ("location"== (?) and archetype == (?) and have_skill==(?))', (location, archetype, skill_set))
			everyone=cur.fetchall()
		return render_template('finder.html', everyone=everyone)



#financial literacy download link
@app.route('/download')
def download_file():
	p="FINANCE_Lesson_plan.pdf"
	return send_file(p,as_attachment=True)

#leadership for entreprenurs link
@app.route('/download2')
def download_file2():
	q="Leadership.pdf"
	return send_file(q,as_attachment=True)




def get_uuid_id():
    return str(uuid.uuid4())

































#Elo rating algotihm for match  making
def Probability(rating1, rating2):
	return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))

def EloRating(Ra, Rb, K, d):

	Pb = Probability(Ra, Rb)
	Pa = Probability(Rb, Ra)
	if (d == 1) :
		Ra = Ra + K * (1 - Pa)
		Rb = Rb + K * (0 - Pb)
	else :
		Ra = Ra + K * (0 - Pa)
		Rb = Rb + K * (1 - Pb)
	

	print("Updated Ratings:-")
	print("Ra =", round(Ra, 6)," Rb =", round(Rb, 6))








if __name__ == '__main__':
	socketio.run(app, debug=True)


