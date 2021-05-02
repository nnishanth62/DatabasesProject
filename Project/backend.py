from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql
import secrets
from hashlib import md5
from datetime import datetime, time, date
import time

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = secrets.token_urlsafe(16)


def format_address(address):
    """
    splits address into number, street, city and state
    :param address:
    :return addresslist:
    """
    address = address.split(", ")
    ind = address[0].find(" ")
    address.insert(0, address[0][0:ind])
    address[0] = address[0][ind + 1:]
    return address


@app.route('/')
def index():
    return render_template("index.html")


# LOGIN METHODS
@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/loginCustomer')
def loginCustomer():
    return render_template("loginCustomer.html")


@app.route('/loginBookingAgent')
def loginBookingAgent():
    return render_template("loginBookingAgent.html")


@app.route('/loginAirlineStaff')
def loginAirlineStaff():
    return render_template("loginAirlineStaff.html")


# LOGINAUTH METHODS
@app.route('/loginAuthCustomer', methods=['GET', 'POST'])
def loginAuthCustomer():
    email = request.form['email']
    password = md5(request.form['password'].encode()).hexdigest()
    cursor = conn.cursor()
    query = "SELECT * FROM customer WHERE email = '{}' and cust_password = '{}'".format(email, password)
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    if data:
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return render_template('loginCustomer.html', error="INVALID LOGIN!")


@app.route('/loginAuthBookingAgent', methods=['GET', 'POST'])
def loginAuthBookingAgent():
    email = request.form['email']
    password = md5(request.form['password'].encode()).hexdigest()
    booking_agent_id = request.form['booking_agent_id']
    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = '{}' and password = '{}' and booking_agent_id = '{}'".format(
        email, password, booking_agent_id)
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    if data:
        session['username'] = email
        return redirect(url_for('home'))
    else:
        return render_template('loginBookingAgent.html', error="INVALID LOGIN!")


@app.route('/loginAuthAirlineStaff', methods=['GET', 'POST'])
def loginAuthAirlineStaff():
    email = request.form['email']
    password = md5(request.form['password'].encode()).hexdigest()

    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE email = '{}' and password = '{}'".format(email, password)
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    if data:
        session['username'] = email
        return redirect(url_for('home'))
    else:
        return render_template('loginAirlineStaff.html', error="INVALID LOGIN!")


# REGISTER METHODS
@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/registerAirlineStaff')
def registerAirlineStaff():
    return render_template('registerAirlineStaff.html')


@app.route('/registerCustomer')
def registerCustomer():
    return render_template('registerCustomer.html')


@app.route('/registerBookingAgent')
def registerBookingAgent():
    return render_template('registerBookingAgent.html')


# REGISTER AUTH METHODS
@app.route('/registerAuth', methods=["GET", "POST"])
def registerAuth():
    username = request.form['username']
    password = md5(request.form['password'].encode()).hexdigest()
    cursor = conn.cursor()
    query = "SELECT * FROM user WHERE username = '{}'".format(username, password)
    cursor.execute(query)
    data = cursor.fetchone()
    if data:
        cursor.close()
        return render_template('register.html', error="USER ALREADY EXISTS")
    else:
        ins = "INSERT INTO user VALUES('{}','{}')".format(username, password)
        cursor.execute(ins)
        conn.commit()
        cursor.close()
        return render_template('index.html', error="Successfully registered, please log in to access your account!")


@app.route('/registerAuthCustomer', methods=["GET", "POST"])
def registerAuthCustomer():
    email = request.form['email']
    cursor = conn.cursor()
    query = "SELECT * FROM customer WHERE email = '{}'".format(email)
    cursor.execute(query)
    data = cursor.fetchone()
    if data:
        cursor.close()
        return render_template('registerCustomer.html', error="USER ALREADY EXISTS")
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cust_password = md5(request.form['password'].encode()).hexdigest()
        phone = "".join(request.form['phone'].split('-'))
        address = request.form['address'].split(', ')
        passport_no = request.form['passport_number']
        passport_country = request.form['passport_country']
        passport_exp = request.form['passport_expiration']
        dob = request.form['DOB']
        ins = "INSERT INTO customer values ('{}', '{}', '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, {})".format(
            email, first_name, last_name, cust_password, phone, address[0], address[1], address[2], address[3],
            passport_no, passport_country, passport_exp, dob)
        cursor.execute(ins)
        conn.commit()
        cursor.close()
        return render_template('index.html', error="Successfully registered, please log in to access your account!")


@app.route('/registerAuthAirlineStaff', methods=["GET", "POST"])
def registerAuthAirlineStaff():
    username = request.form['username']
    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE username = '{}'".format(username)
    cursor.execute(query)
    data = cursor.fetchone()
    if data:
        cursor.close()
        return render_template('registerAirlineStaff.html', error="USER ALREADY EXISTS")
    else:
        fname = request.form['first_name']
        lname = request.form['last_name']
        password = md5(request.form['password'].encode()).hexdigest()
        dob = request.form['DOB']
        airline = request.form['airline_name']
        ins = "INSERT INTO airline_staff VALUES('{}','{}','{}','{}',{},'{}')".format(username, fname, lname, password,
                                                                                     dob, airline)
        cursor.execute(ins)
        conn.commit()
        cursor.close()
        return render_template('index.html', error="Successfully registered, please log in to access your account!")


@app.route('/registerAuthBookingAgent', methods=["GET", "POST"])
def registerAuthBookingAgent():
    email = request.form['email']
    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = '{}'".format(email)
    cursor.execute(query)
    data = cursor.fetchone()
    if data:
        cursor.close()
        return render_template('registerBookingAgent.html', error="USER ALREADY EXISTS")
    else:
        password = md5(request.form['password'].encode()).hexdigest()
        agent_id = request.form['booking_agent_id']
        commission = 0
        ins = "INSERT INTO booking_agent VALUES('{}','{}','{}',{})".format(email, agent_id, password, commission)
        cursor.execute(ins)
        conn.commit()
        cursor.close()
        return render_template('index.html', error="Successfully registered, please log in to access your account!")


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


@app.route('/home')
def home():
    username = session['username']
    return render_template('home.html', name=username)


# PUBLIC VIEWS

@app.route('/publicviewSearch')
def publicviewSearch():
    return render_template("publicviewSearch.html")


@app.route('/publicviewSearchAuth', methods=["GET", "POST"])
def publicviewSearchAuth():
    date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
    query = "SELECT airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, departure_airport_name, dep_port.city, arrival_airport_name, ar_port.city FROM flight, " \
            "airport as dep_port, airport as ar_port WHERE dep_port.name = departure_airport_name and ar_port.name = arrival_airport_name and departure_date > '{}' and departure_time > '{}'".format(
        date_time[0], date_time[1])
    query_addition = []
    departure_airport = request.form['departure_airport']
    arrival_airport = request.form['arrival_airport']
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']
    departure_city = request.form['departure_city']
    arrival_city = request.form['arrival_city']
    if departure_airport != '':
        query_addition.append("departure_airport_name = '%s'" % departure_airport)
    if arrival_airport != '':
        query_addition.append("arrival_airport_name = '%s'" % arrival_airport)
    if departure_date != '':
        query_addition.append("departure_date = '%s'" % departure_date)
    if arrival_date != '':
        query_addition.append("arrival_date = '%s'" % arrival_date)
    if departure_city != '':
        query_addition.append("dep_port.city = '%s'" % departure_city)
    if arrival_city != '':
        query_addition.append("ar_port.city = '%s'" % arrival_city)
    if query_addition:
        query += " and " + " and ".join(query_addition)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('/publicviewDisplay.html', data=data)


# CUSTOMER VIEWS

@app.route('/CustHome')
def CustHome():
    return render_template("CustHome.html")


@app.route('/CustViewMyFlights')
def CustViewMyFlights():
    date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
    query = "SELECT * FROM flight, purchase, ticket WHERE flight.flight_status = 'upcoming' AND flight.flight_num =" \
            " ticket.flight_num AND ticket.ticket_id = purchase.ticket_id AND purchase.customer_email = '{}' and departure_date > '{}' and departure_time > '{}'" \
        .format(session['email'], date_time[0], date_time[1])
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('CustViewMyFlights.html', data=data)


@app.route('CustSearchForFlights')
def CustSearchForFlights():
    return render_template("CustSearchForFlights.html")


@app.route('/CustSearchForFlightsAuth', methods=["GET", "POST"])
def CustSearchForFlightsAuth():
    date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
    query = "SELECT * FROM purchaseable_tickets WHERE departure_date > '{}' and departure_time > '{}'".format(date_time[0], date_time[1])
    query_addition = []
    departure_airport = request.form['departure_airport']
    arrival_airport = request.form['arrival_airport']
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']
    departure_city = request.form['departure_city']
    arrival_city = request.form['arrival_city']
    if departure_airport != '':
        query_addition.append("departure_airport_name = '%s'" % departure_airport)
    if arrival_airport != '':
        query_addition.append("arrival_airport_name = '%s'" % arrival_airport)
    if departure_date != '':
        query_addition.append("departure_date = '%s'" % departure_date)
    if arrival_date != '':
        query_addition.append("arrival_date = '%s'" % arrival_date)
    if departure_city != '':
        query_addition.append("dep_port.city = '%s'" % departure_city)
    if arrival_city != '':
        query_addition.append("ar_port.city = '%s'" % arrival_city)
    if query_addition:
        query += " and " + " and ".join(query_addition)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('/CustSearchForFlightsDisplay.html', data=data)


@app.route('/CustPurchaseFlightsAuth', methods=["GET", "POST"])
def CustPurchaseFlightAuth():
    get = "SELECT * from purchaseable_tickets where flight_num = '{}' and airline_name = '{}' " \
          "and departure_time = {} and departure_date = {}" \
          .format(request.form['flight_num'], request.form['airline_name'], request.form['departure_time'], request.form['departure_date'])
    cursor = conn.cursor()
    cursor.execute(get)
    flight = cursor.fetchone()
    if flight:
        ins = "INSERT into ticket VALUES ('{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', {})".format(secrets.token_urlsafe(5), flight[1], flight[0], request.form['price'], session['email'], request.form['debit_credit'], request.form['card_no'], request.form['cardholder'], request.form['card_exp'])
        cursor.execute(ins)
        cursor.commit()
        error = 'TICKET PURCHASED'
    else:
        error = 'TICKET FAILED TO PURCHASE: FLIGHT NOT FOUND'
    cursor.close()
    return render_template('/CustHome', error=error)

# BOOKING AGENT VIEWS

@app.route('/CustHome')
def BookingAgentHome():
    return render_template("BookingAgentHome.html")


@app.route('/BookingAgentViewFlights')
def BookingAgentViewFlights():
    date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
    query = "SELECT * FROM flight, purchase, booking_agent, ticket WHERE flight.flight_num = ticket.flight_num" \
            "AND ticket.ticket_id = purchase.ticket_id AND purchase.booking_agent_email = booking_agent.email" \
            "AND booking_agent.email = '{}' " \
            .format(session['email'], date_time[0], date_time[1])
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('BookingAgentViewFlights.html', data=data)


@app.route('BookingAgentSearchForFlights')
def BookingAgentSearchForFlights():
    return render_template("BookingAgentSearchForFlights.html")


@app.route('/BookingAgentSearchForFlightsAuth', methods=["GET", "POST"])
def BookingAgentSearchForFlightsAuth():
    date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
    query = "SELECT * FROM flight, purchase, ticket WHERE purchase.customer_email = '{}'" \
            "AND purchase.ticket_id = ticket.ticket_id AND ticket.flight_num = flight.flight_num".format(date_time[0], date_time[1])
    query_addition = []
    departure_airport = request.form['departure_airport']
    arrival_airport = request.form['arrival_airport']
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']
    departure_city = request.form['departure_city']
    arrival_city = request.form['arrival_city']
    if departure_airport != '':
        query_addition.append("departure_airport_name = '%s'" % departure_airport)
    if arrival_airport != '':
        query_addition.append("arrival_airport_name = '%s'" % arrival_airport)
    if departure_date != '':
        query_addition.append("departure_date = '%s'" % departure_date)
    if arrival_date != '':
        query_addition.append("arrival_date = '%s'" % arrival_date)
    if departure_city != '':
        query_addition.append("dep_port.city = '%s'" % departure_city)
    if arrival_city != '':
        query_addition.append("ar_port.city = '%s'" % arrival_city)
    if query_addition:
        query += " and " + " and ".join(query_addition)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('/BookingAgentSearchForFlightsAuth.html', data=data)


@app.route('/BookingAgentPurchaseAuth', methods=["GET", "POST"])
def BookingAgentPurchaseAuth():
    get = "SELECT * from purchaseable_tickets where flight_num = '{}' and airline_name = '{}' " \
          "and departure_time = {} and departure_date = {}" \
          .format(request.form['flight_num'], request.form['airline_name'], request.form['departure_time'], request.form['departure_date'])
    
    cursor = conn.cursor()
    cursor.execute(get)
    flight = cursor.fetchone()
    if flight:
        ins = "INSERT into purchases VALUES ('{}', '{}', '{}', '{}')" \
              .format(request_form['ticket_id', request_form['customer_username'], request_form['booking_agent_id'], request_form['departure_date'])
        cursor.execute(ins)
        cursor.commit()
        error = 'TICKET PURCHASED'
    else:
        error = 'TICKET FAILED TO PURCHASE: FLIGHT NOT FOUND'
    cursor.close()
    return render_template('/BookingAgentHome', error=error)"


if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
