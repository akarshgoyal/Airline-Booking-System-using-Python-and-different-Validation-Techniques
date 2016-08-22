import os , random
from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL
import sys
app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'saurabh'
app.config['MYSQL_DATABASE_PASSWORD'] = 'saurabh'
app.config['MYSQL_DATABASE_DB'] = 'Flight_Management_System'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
c = conn.cursor()

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/flights",methods=['GET','POST'])
def flights():
    _from = request.form['airport_from']
    _to   = request.form['airport_to']
    _date = request.form['date']
    
    print "Form Data as follows:-"
    print "From:",_from ,"To:" , _to ,"Date:" ,_date
    print "Query Executed:SELECT flight_no,arrival,departure,no_of_stoppages FROM route JOIN flight_details ON flight_no = fno WHERE source=(SELECT port_id FROM Airport WHERE city='%s') AND destination=(SELECT port_id FROM Airport WHERE city='%s')"%(_from,_to)
    c.execute ("SELECT flight_no,airlines,arrival,departure,no_of_stoppages,price,route_id FROM route JOIN flight_details ON flight_no = fno WHERE source=(SELECT port_id FROM Airport WHERE city='%s') AND destination=(SELECT port_id FROM Airport WHERE city='%s')"%(_from,_to))
    entries = []
    entries = [dict(Flight_no=row[0], Airlines=row[1],arrive_time = row[2],depart_time = row[3],stops = row[4],price = row[5],rid = row[6],date=_date) for row in c.fetchall()]
    
    print "Results obtained:"
    print entries
    #Here route id is hidden in html and will be sent as post request
    return render_template("flights.html",entries=entries)


@app.route("/book",methods=['GET','POST'])
def book():
    print "Form data:-"
    _rid = request.args.get('rid')
    _date = request.args.get('date')
    entries = dict(rid = _rid,date=_date)
    print entries
    return render_template("user_details.html",entries=entries)

@app.route("/payment",methods=['GET','POST'])
def payment():
    print "HERE"
    _fn = request.form['firstname']
    _ln = request.form['lastname']
    _age = int(request.form['age'])
    _sex = request.form['sex']
    _email = request.form['email']
    _phone = int(request.form['phone'])
    _rid = int(request.form['rid'])
    _date = request.form['date']
    _meal = request.form['meal']
    _seats = int(request.form['seats'])
    _insuarance = request.form['insuarance']

    
    _pid = random.randint(1000,99999)
    _pnr = random.randint(10000,999999)

    try:
        print "INSERT IGNORE INTO PASSENGER VALUES (%s,'%s','%s',%s,'%s','%s',%s)"%(_pid,_fn,_ln,_age,_sex,_email,_phone)
        c.execute("INSERT INTO PASSENGER VALUES (%s,'%s','%s',%s,'%s','%s',%s)"%(_pid,_fn,_ln,_age,_sex,_email,_phone))
        c.execute("INSERT INTO CHOOSES VALUES (%s,%s,'%s','%s','%s',%s,%s)"%(_pnr,_pid,_date,_meal,_insuarance,_seats,_rid))
    except _mysql_exceptions.IntegrityError:
        pass


    c.execute('Select * from route where route_id=%s'%(_rid))
    price1 = int(c.fetchall()[0][6])
    price1= int(price1)
    price = price1
    price = price*int(_seats)
    add = 0
    #Discount Calculation:
    discount = 0
    c.execute("Select * from discount where dis_day='%s'"%(_date))
    try:
        discount = int(c.fetchall()[0][2])
    except IndexError:
        discount = 0
    if _meal == 'Y':
        add = add + 0.05*price
    if _insuarance == 'Y':
        add = add +  0.05*price
    price = price + add
    dis_price = price - (price*discount)/100
    entries = dict(flight_price=price1,pnr = _pnr,rid = _rid,date=_date,meal=_meal,insuarance = _insuarance,total_amount = price,dis_percent = discount,discounted=dis_price,seat=_seats)
    conn.commit()
    return render_template("Payment_gateway.html",entries=entries)

    
    

if __name__=="__main__":
    app.run(debug=True)



