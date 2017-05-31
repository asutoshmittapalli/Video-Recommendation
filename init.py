from flask import Flask, render_template, request, session
from flask import redirect, url_for, Response
from flask_pymongo import PyMongo
from flask_session import Session
import json
from py2neo import Graph,authenticate
from flaskext.mysql import MySQL
#import MySQLdb

from pymongo import MongoClient
client = MongoClient()
db=client['youtube']
collection = db['videos']

login=''

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'youtube'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/youtube'

mongo = PyMongo(app)
authenticate("localhost:7474", "neo4j", "ashu0805")
graph = Graph("http://localhost:7474/db/data/")

#graph = Graph(user="neo4j",password="ashu0805")
#mysql.init_app(app)

client = MongoClient()


@app.route('/')
def home():
   global login
   return render_template('cleanpage1.html')
   
@app.route('/auth', methods=['GET', 'POST'])
def auth():
	if request.method == 'POST':
		u = request.form['username']
		p = request.form['password']

	global login
	login=''

	session['username'] = u
	if(str(p)=="egg") : 
		login = u
		return render_template("cleanpage2.html",username = login)
	else : 
		return render_template("cleanpage1.html",username = "wrong pwd")
		
@app.route('/logout')
def logout():
	global login
	login= ''

	session.pop('username', None)
	return redirect_template("cleanpage1.html")

@app.route('/video/<vidID>')
def video(vidID):
	global login
	vid = list(mongo.db.videos.find({"videoInfo.id":vidID}).limit(1))
	#print vid
	related = graph.run("match(n:Youtube)-[r]-(n2) where n.name= {n} return n2 order by r.weight desc limit 10",n = vidID)
	out=[]
	for i in related:
		out.append(mongo.db.videos.find_one({'videoInfo.id':i['n2']['name']}))
	if login=='':
		return render_template("cleanpage3.html",username = "Guest user : You have not logged in.", result=vid, search = out)
	else : 
		return render_template("cleanpage3.html",username = login, result=vid, search = out)
	


@app.route('/refresh',methods = ['POST', 'GET'])
def search():
   global login
   if request.method == 'POST':
      result = request.form['Searched for : ']
      print result
      search1 = list(mongo.db.videos.find({'$text':{'$search':str(result)}}).limit(10))
      out=[]
      #print search1
      #for doc in search1
	 #out.append([doc['videoInfo']['snippet']['title']],)
   if login=='':
   	return render_template("cleanpage2.html",username = "Guest user : You have not logged in.",result=result,search = search1)
   else : 
   	return render_template("cleanpage2.html",username = login,result=result,search = search1)
   	

if __name__ == '__main__':
   app.secret_key = 'egg'
   app.run('172.16.68.19')
