"""
Johnlouis Dahhan and Nidhin Nishanth
CS-UY 3038 Databases
Final Project Part 3
Uses myplotlib, flask, pymysql, phpMyAdmin, HTML, (very little) CSS
"""
from flask import Flask, render_template, request, session, redirect, flash
import pymysql
import matplotlib
import matplotlib.pyplot as plt
import secrets
from hashlib import md5
from datetime import datetime, time, date, timedelta
import time
matplotlib.use('Agg')  # Avoids threading error

app = Flask(__name__)
# WANT NO CACHING BECAUSE WE WANT GRAPHS TO CONSTANTLY UPDATE
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',  # I didn't need a password
                       db='dbproject',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = secrets.token_urlsafe(16)


def gen_id(table, airline_name=None):
    # generates either a unique ticket, airplane or flight ID
    cursor = conn.cursor()
    if not airline_name:
        if table == 'ticket':
            data = True
            while data:
                table_id = secrets.token_urlsafe(5)
                query = "SELECT * FROM ticket WHERE ticket_id = %s"
                cursor.execute(query, table_id)
                data = cursor.fetchone()
        if table == 'airplane':
            data = True
            while data:
                table_id = secrets.token_urlsafe(5)
                query = "SELECT * FROM airplane WHERE ID = %s"
                cursor.execute(query, table_id)
                data = cursor.fetchone()
    else:
        data = True
        while data:
            table_id = secrets.token_urlsafe(6)
            query = "SELECT * FROM flight WHERE flight_num = %s AND airline_name = %s"
            cursor.execute(query, (table_id, airline_name))
            data = cursor.fetchone()
    cursor.close()
    return table_id[:6]


# GRAPHS
def graphs(plot, start_date=None, end_date=None):
    # produces all graphs, saves them to pngs in /static
    cursor = conn.cursor()
    if plot == "Cust":
        if VerifyCustomer():
            # Want spending graph, default should be past 6 months
            if start_date and end_date:
                # get every ticket in purchase range for current customer
                query = "SELECT * FROM ticket natural join purchase natural join flight WHERE purchase_date >= %s and purchase_date <= %s AND customer_email = %s " \
                        "ORDER BY purchase_date ASC"
                cursor.execute(query, (start_date, end_date, session['email']))
            else:
                if start_date:
                    # query slightly changes if start/end dates are not specified
                    query = "SELECT * FROM ticket natural join purchase natural join flight WHERE purchase_date >= %s AND  " \
                            "purchase_date <= CURDATE() AND customer_email = %s AND flight_airline_name = airline_name " \
                            "ORDER BY purchase_date ASC"
                    cursor.execute(query, (start_date, session['email']))
                else:
                    end_date = end_date if end_date else str(date.today())
                    query = "SELECT * FROM ticket natural join purchase natural join flight WHERE purchase_date >=  " \
                            "DATE_SUB(%s, INTERVAL 6 MONTH) AND purchase_date <= %s AND customer_email = %s " \
                            "AND flight_airline_name = airline_name ORDER BY purchase_date ASC"
                    cursor.execute(query, (end_date, end_date, session['email']))
            data = cursor.fetchall()
            graphdata = {}
            for line in data:
                curr_month = line['purchase_date'].strftime('%Y-%m')
                curr_price = int(line['sold_price'])
                graphdata[curr_month] = graphdata[curr_month] + curr_price if curr_month in graphdata else curr_price
            plt.bar(list(graphdata.keys()), list(graphdata.values()))
            plt.title('Amount of Money Spent per Month')
            plt.savefig("static/CustSpendingGraph.png")
            plt.clf()
        else:
            return redirect('/logout')
    elif plot == "BookingAgent":
        if VerifyBookingAgent():
            # Top customers by commission, last year
            query = "SElECT SUM(sold_price)*0.1 as commission, first_name, last_name, customer.email FROM ticket NATURAL JOIN purchase, customer WHERE customer.email = customer_email " \
                    " AND purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND booking_agent_email = %s GROUP BY customer.email ORDER BY commission DESC"
            cursor = conn.cursor()
            cursor.execute(query, session['email'])
            data = cursor.fetchall()
            if len(data) > 5:
                data = data[:5]
            x = [line['first_name'] + ' ' + line['last_name'] for line in data]
            y = [int(line['commission']) for line in data]
            plt.bar(x, y)
            plt.title('Top 5 Customers by Commission (past year)')
            plt.savefig("static/BookingAgentCommissionGraph.png")
            plt.clf()
            # top customers by ticket sales, last 6 mo
            query = "SElECT COUNT(ticket_id) as ticket_sales, customer.email, first_name, last_name FROM ticket NATURAL JOIN purchase, customer WHERE customer.email = customer_email " \
                    " AND purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) AND booking_agent_email = %s GROUP BY customer.email ORDER BY ticket_sales DESC"
            cursor.execute(query, session['email'])
            data = cursor.fetchall()
            if len(data) > 5:
                data = data[:5]
            x = [line['first_name'] + ' ' + line['last_name'] for line in data]
            y = [int(line['ticket_sales']) for line in data]
            plt.bar(x, y)
            plt.title('Top 5 Customers by Tickets Sold (past 6 mo.)')
            plt.savefig("static/BookingAgentTicketGraph.png")
            plt.clf()
            cursor.close()
        else:
            return redirect('/logout')
    elif plot == "AirlineStaff":
        if VerifyAirlineStaff():
            # ticket sales by month
            if start_date and end_date:
                # getting all tickets for this airline in date range
                query = "SELECT * FROM ticket NATURAL JOIN purchase WHERE flight_airline_name = %s AND purchase_date >= " \
                        "%s AND purchase_date <= %s ORDER BY purchase_date ASC"
                cursor.execute(query, (get_airline(), start_date, end_date))
            else:
                # slightly modify depending on presence of parameters
                if start_date:
                    query = "SELECT * FROM ticket NATURAL JOIN purchase WHERE flight_airline_name = %s AND purchase_date >= %s " \
                            " AND purchase_date <= CURDATE() ORDER BY purchase_date ASC"
                    cursor.execute(query, (get_airline(), start_date))
                else:
                    end_date = str(date.today()) if not end_date else end_date
                    query = "SELECT * FROM ticket NATURAL JOIN purchase WHERE flight_airline_name = %s AND purchase_date >= " \
                            " DATE_SUB(%s, INTERVAL 1 YEAR) AND purchase_date <= %s ORDER BY purchase_date ASC"
                    cursor.execute(query, (get_airline(), end_date, end_date))
            ticket_count = cursor.fetchall()
            graphdata = {}
            for line in ticket_count:
                curr_month = line['purchase_date'].strftime('%Y-%m')
                graphdata[curr_month] = graphdata[curr_month] + 1 if curr_month in graphdata else 1
            plt.bar(list(graphdata.keys()), list(graphdata.values()))
            plt.title('Ticket Sales for %s by Month' % get_airline())
            plt.savefig('static/AirlineStaffTicketCount.png')
            plt.clf()
            # PIE CHART FOR BA VS CUST PURCHASES
            query = "SELECT COUNT(ticket_id) as count FROM purchase NATURAL JOIN ticket WHERE flight_airline_name = %s AND booking_agent_email {} NULL"
            cursor.execute(query.format('IS NOT'), get_airline())
            ba_count = int(cursor.fetchone()['count'])
            cursor.execute(query.format('IS'), get_airline())
            cust_count = int(cursor.fetchone()['count'])
            plt.pie((ba_count, cust_count), labels=("Booking Agent Sales", "Customer Sales"), autopct='%1.1f%%')
            plt.title('Booking Agent vs Customer Ticket Purchases')
            plt.savefig('static/AirlineStaffBAvCustSales.png')
            plt.clf()
        else:
            return redirect('/logout')


# VERIFICATION

def VerifyCustomer():
    # verifies that a customer exists with this email
    if session.get('type') == 'Cust':
        verify = "SELECT * FROM customer WHERE email = %s" # checking if customer exists
        try:
            cursor = conn.cursor()
            cursor.execute(verify, session['email'])
            data = cursor.fetchone()
            cursor.close()
            return len(data) > 0
        except:
            return False
    return False


def VerifyAirlineStaff():
    # verifies valid Airline staff session
    if session.get('type') == 'AirlineStaff':
        verify = "SELECT * FROM airline_staff WHERE username = %s"
        try:
            cursor = conn.cursor()
            cursor.execute(verify, session['email'])
            data = cursor.fetchone()
            cursor.close()
            return len(data) > 0
        except:
            return False
    return False


def VerifyBookingAgent():
    # verifies valid Airline staff session
    if session.get('type') == 'BookingAgent':
        verify = "SELECT * FROM booking_agent WHERE email = %s"
        try:
            cursor = conn.cursor()
            cursor.execute(verify, session['email'])
            data = cursor.fetchone()
            cursor.close()
            return len(data) > 0
        except:
            return False
    return False


@app.route('/')  # main page, allows login, registration, public views
def index():
    if not VerifyCustomer() and not VerifyBookingAgent() and not VerifyAirlineStaff():
        return render_template("index.html")
    else:
        return redirect('/Home')  # if a logged in user finds this page, we send them to their respective home


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
    query = "SELECT * FROM customer WHERE email = %s and cust_password = %s"  # check if accurate login info
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    if data:  # create session variables
        session['email'] = email
        session['username'] = data['first_name']
        session['type'] = 'Cust'
        return redirect('/CustHome')
    else:
        flash("INVALID LOGIN!")
        return redirect('/loginCustomer')


@app.route('/loginAuthBookingAgent', methods=['GET', 'POST'])
def loginAuthBookingAgent():
    email = request.form['email']
    password = md5(request.form['password'].encode()).hexdigest()
    booking_agent_id = request.form['booking_agent_id']
    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = %s and agent_password = %s and booking_agent_id = %s"  # check for valid login
    cursor.execute(query, (email, password, booking_agent_id))
    data = cursor.fetchone()
    cursor.close()
    if data:  # create session variables
        session['email'] = email
        session['username'] = data['email']
        session['type'] = 'BookingAgent'
        return redirect('/BookingAgentHome')
    else:
        flash("INVALID LOGIN!")
        return render_template('loginBookingAgent.html')


@app.route('/loginAuthAirlineStaff', methods=['GET', 'POST'])
def loginAuthAirlineStaff():
    username = request.form['username']
    password = md5(request.form['password'].encode()).hexdigest()
    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE username  = %s and staff_password = %s"  # check for valid login
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    if data:  # create session variables
        session['email'] = username
        session['username'] = data['first_name']
        session['type'] = 'AirlineStaff'
        return redirect('/AirlineStaffHome')
    else:
        flash("INVALID LOGIN")
        return render_template('loginAirlineStaff.html')


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
@app.route('/registerAuthCustomer', methods=["GET", "POST"])
def registerAuthCustomer():
    email = request.form['email']
    cursor = conn.cursor()
    query = "SELECT * FROM customer WHERE email = %s"  # check for existing customer
    cursor.execute(query, email)
    data = cursor.fetchone()
    if data:
        cursor.close()
        flash("USER ALREADY EXISTS")
        return render_template('registerCustomer.html')
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cust_password = md5(request.form['password'].encode()).hexdigest()
        phone = request.form['phone']
        address = request.form['address'].split(',')  # breaking up address into table columns
        ind = address[0].find(' ')
        num_name = address[0]
        address.insert(0, num_name)
        address[0] = address[0][:ind]
        address[1] = address[1][ind:]
        address = [item.strip() for item in address]
        passport_no = request.form['passport_number']
        passport_country = request.form['passport_country']
        passport_exp = request.form['passport_expiration']
        dob = request.form['DOB']
        ins = "INSERT INTO customer values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"  # create new customer
        cursor.execute(ins, (email, first_name, last_name, cust_password, phone, address[0], address[1], address[2],
                             address[3], passport_no, passport_country, passport_exp, dob))
        conn.commit()
        cursor.close()
        flash("SUCCESSFULLY REGISTERED CUSTOMER")
        return redirect('/')


@app.route('/registerAuthAirlineStaff', methods=["GET", "POST"])
def registerAuthAirlineStaff():
    username = request.form['username']
    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE username = %s"  # check if staff member exists
    cursor.execute(query, username)
    data = cursor.fetchone()
    airline_query = "SELECT * FROM airline WHERE name = %s"  # check if airline exists
    cursor.execute(airline_query, request.form.get('airline_name'))
    al_data = cursor.fetchone()
    if data:
        cursor.close()
        flash("USER ALREADY EXISTS")
        return redirect('/registerAirlineStaff')
    if not al_data:
        cursor.close()
        flash("AIRLINE DOES NOT EXIST")
        return redirect('/registerAirlineStaff')
    else:
        fname = request.form['first_name']
        lname = request.form['last_name']
        password = md5(request.form['password'].encode()).hexdigest()
        dob = request.form['DOB']
        airline = request.form['airline_name']
        ins = "INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)"  # create new staffer
        cursor.execute(ins, (username, fname, lname, password, dob, airline))
        conn.commit()
        cursor.close()
        flash("SUCCESSFULLY REGISTERED AIRLINE STAFF")
        return redirect('/')


@app.route('/registerAuthBookingAgent', methods=["GET", "POST"])
def registerAuthBookingAgent():
    email = request.form['email']
    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = %s"  # check if agent exists
    cursor.execute(query, email)
    data = cursor.fetchone()
    if data:
        cursor.close()
        flash("USER ALREADY EXISTS")
        return render_template('registerBookingAgent.html')
    else:
        password = md5(request.form['password'].encode()).hexdigest()
        agent_id = request.form['booking_agent_id']
        commission = 0
        ins = "INSERT INTO booking_agent VALUES(%s, %s, %s, %s)"  # create agent
        cursor.execute(ins, (email, agent_id, password, commission))
        conn.commit()
        cursor.close()
        flash("SUCCESSFULLY REGISTERED BOOKING AGENT")
        return redirect('/')


@app.route('/logout')
def logout():
    session.pop('username', None)  # remove all session variables if possible
    session.pop('email', None)
    session.pop('type', None)
    return redirect('/')


# PUBLIC VIEWS

@app.route('/publicview')
def publicview():
    return render_template("publicviewSearch.html", current_date=date.today())


@app.route('/publicviewDisplay', methods=["GET", "POST"])
def publicviewDisplay():
    query = "SELECT * FROM purchasable_tickets WHERE departure_date >= CURDATE() AND tickets_sold < capacity"
    # select future flights where there are still tickets to be sold
    query_addition = []
    parameters = []
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    # add query segments and parameters if user fills out optional parameters
    if departure_airport:
        query_addition.append("departure_airport_name = %s")
        parameters.append(departure_airport)
    if arrival_airport:
        query_addition.append("arrival_airport_name = %s")
        parameters.append(arrival_airport)
    if departure_date:
        query_addition.append("departure_date = %s")
        parameters.append(departure_date)
    if arrival_date:
        query_addition.append("arrival_date = %s")
        parameters.append(arrival_date)
    if departure_city:
        query_addition.append("departure_city = %s")
        parameters.append(departure_city)
    if arrival_city:
        query_addition.append("arrival_city = %s")
        parameters.append(arrival_city)
    query = query + " AND " + " AND ".join(query_addition) if query_addition else query
    query += " ORDER BY departure_date DESC"  # show them the soonest flights first
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    data = cursor.fetchall()
    cursor.close()
    return render_template('publicviewDisplay.html', data=data)


@app.route('/Home')
def Home():
    # sends logged in users to their respective homes, not logged in users sent to index
    if VerifyAirlineStaff():
        return redirect('/AirlineStaffHome')
    elif VerifyBookingAgent():
        return redirect('/BookingAgentHome')
    elif VerifyCustomer():
        return redirect('/CustHome')
    else:
        return redirect('/')


# CUSTOMER VIEWS
@app.route('/CustHome', methods=["GET", "POST"])
def CustHome():
    if VerifyCustomer():  # if looking for their name has a result, send them to home
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        graphs("Cust", start_date, end_date)
        current_date = str(date.today())
        name = session['username']
        return render_template("CustHome.html", current_date=current_date, name=name)
    else:  # otherwise we just kill their session
        return redirect('/logout')


@app.route('/CustViewMyFlights')
def CustViewMyFlights():
    if VerifyCustomer():
        query = "SELECT * FROM purchase natural join ticket natural join purchasable_tickets WHERE airline_name = flight_airline_name  " \
                "AND purchase.customer_email = %s and departure_date >= CURDATE() ORDER BY departure_date ASC"
        # show them any future flights they purchased
        cursor = conn.cursor()
        cursor.execute(query, (session['email']))
        data = cursor.fetchall()
        cursor.close()
        return render_template('CustViewMyFlights.html', data=data)
    else:
        return redirect('/logout')


@app.route('/CustSearchForFlights')
def CustSearchForFlights():
    if VerifyCustomer():
        return render_template("CustSearchForFlights.html", current_date=date.today())
    else:
        return redirect('/logout')


@app.route('/CustSearchForFlightsDisplay', methods=["GET", "POST"])
def CustSearchForFlightsDisplay():
    if VerifyCustomer():
        query = "SELECT * FROM purchasable_tickets WHERE tickets_sold < capacity"  # showing purchasable flights with seats left
        query_addition = []
        parameters = []
        departure_airport = request.form['departure_airport']
        arrival_airport = request.form['arrival_airport']
        departure_date = request.form['departure_date']
        arrival_date = request.form['arrival_date']
        departure_city = request.form['departure_city']
        arrival_city = request.form['arrival_city']
        # add optional parameters and query qualifiers if need be
        if departure_airport:
            query_addition.append("departure_airport_name = %s")
            parameters.append(departure_airport)
        if arrival_airport:
            query_addition.append("arrival_airport_name = %s")
            parameters.append(arrival_airport)
        if departure_date:
            query_addition.append("departure_date = %s")
            parameters.append(departure_date)
        if arrival_date:
            query_addition.append("arrival_date = %s")
            parameters.append(arrival_date)
        if departure_city:
            query_addition.append("departure_city = %s")
            parameters.append(departure_city)
        if arrival_city:
            query_addition.append("arrival_city = %s")
            parameters.append(arrival_city)
        query = query + " AND " + " AND ".join(query_addition) if query_addition else query
        query += " ORDER BY departure_date DESC"  # soonest flights first
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        data = cursor.fetchall()
        cursor.close()
        for line in data:
            start_price = float(line['price'])
            line['price'] = start_price if line['capacity'] * .7 > line['tickets_sold'] else start_price * 1.2
            line['price'] = str(line['price'])
        return render_template('CustSearchForFlightsDisplay.html', data=data, current_date=date.today())
    else:
        return redirect('/logout')


@app.route('/CustPurchaseFlightAuth', methods=["GET", "POST"])
def CustPurchaseFlightAuth():
    if VerifyCustomer():
        get = "SELECT * FROM purchasable_tickets WHERE flight_num = %s AND airline_name = %s AND tickets_sold < capacity  " \
              "AND departure_time = %s AND departure_date = %s"  # check if requested flight is a future flight that still has tickets
        cursor = conn.cursor()
        cursor.execute(get, (
            request.form['flight_num'], request.form['airline_name'], request.form['departure_time'] + ':00',
            request.form['departure_date']))
        flight = cursor.fetchone()
        if flight:
            price = float(flight['price']) if float(flight['capacity']) * .7 > float(flight['tickets_sold']) else float(
                flight['price']) * 1.2
            date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
            ticket_id = gen_id('ticket')
            # first gonna create the ticket
            ins_ticket = "INSERT into ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(ins_ticket,
                           (ticket_id, flight['airline_name'], flight['flight_num'], price, session['email'],
                            request.form['debit_credit'], request.form['card_no'],
                            request.form['cardholder'],
                            request.form['card_exp']))
            # then create the purchase record (NULL value is booking agent email)
            ins_purchase = "INSERT into purchase VALUES (%s, %s, NULL, %s, %s)"
            cursor.execute(ins_purchase, (ticket_id, session['email'], date_time[0], date_time[1]))
            # then update the seats sold on the flight
            update = "UPDATE flight SET tickets_sold = tickets_sold + 1 WHERE flight_num = %s AND airline_name = %s AND departure_date = %s " \
                     "AND departure_time = %s"
            cursor.execute(update, (
                flight['flight_num'], flight['airline_name'], flight['departure_date'], flight['departure_time']))
            conn.commit()
            flash('PURCHASE SUCCESSFUL')
            return redirect('/CustHome')
        else:
            error = 'TICKET FAILED TO PURCHASE: FLIGHT NOT FOUND'
            flash(error)
            cursor.close()
            return redirect('/CustHome')
    else:
        return redirect('/logout')


@app.route('/CustGiveRatings')
def CustGiveRatings():
    if VerifyCustomer():
        cursor = conn.cursor()
        # find previous flights that user has flown on
        query = "SELECT * FROM flight natural join ticket natural join customer WHERE ticket.customer_email = customer.email " \
                " AND customer_email = %s and flight.arrival_date < CURDATE() AND flight.airline_name = ticket.flight_airline_name"
        cursor.execute(query, (session['email']))
        allflights = cursor.fetchall()
        # find all user ratings
        query = "SELECT * FROM ratings WHERE email = %s"
        cursor.execute(query, session['email'])
        prevratings = cursor.fetchall()
        cursor.close()
        return render_template("CustGiveRatings.html", allflights=allflights, prevratings=prevratings)
    else:
        return redirect('/logout')


@app.route('/CustRatingAuth', methods=["GET", "POST"])
def CustRatingAuth():
    if VerifyCustomer():
        cursor = conn.cursor()
        # find if flight is a legitimate flight that the user has flown on in the past
        query = "SELECT * FROM flight natural join ticket natural join purchase WHERE ticket.flight_airline_name = flight.airline_name AND " \
                "customer_email = %s AND arrival_date < CURDATE() AND flight_num = %s and airline_name = %s"
        cursor.execute(query,
                       (session['email'], request.form['flight_num'], request.form['airline_name']))
        flight_exists = cursor.fetchall()
        # check if user has previously rated that flight
        query = "SELECT * FROM ratings WHERE email = %s and flight_num = %s and airline_name = %s"
        cursor.execute(query,
                       (session['email'], request.form['flight_num'], request.form['airline_name']))
        already_rated = cursor.fetchall()
        if flight_exists and not already_rated:
            # insert user values into ratings table
            ins = "INSERT INTO ratings VALUES(%s, %s, %s, %s, %s)"
            cursor.execute(ins, (session['email'], request.form['flight_num'], request.form['airline_name'],
                                 request.form['comment'], request.form['rating']))
            conn.commit()
            flash('Rating Successfully Posted')
            return redirect('/CustHome')
        else:
            cursor.close()
            flash('Submission Failed: check if the flight exists or if you have already reviewed it')
            return redirect('/CustGiveRatings')
    else:
        return redirect('/logout')


# BOOKING AGENT VIEWS
@app.route('/BookingAgentHome', methods=["GET", "POST"])
def BookingAgentHome():
    if VerifyBookingAgent():
        graphs("BookingAgent")
        days = int(request.form.get('days', 30))
        name = session['username']
        # look for previously sold tickets where booking agent is present
        query = "SELECT * FROM ticket natural join purchase WHERE booking_agent_email = %s AND purchase_date > DATE_SUB(CURDATE(), INTERVAL %s DAY)"
        cursor = conn.cursor()
        cursor.execute(query, (name, days))
        data = cursor.fetchall()
        cursor.close()
        commission = sum(
            [int(line['sold_price']) for line in data]) * 0.1  # much much easier to calculate commission in python
        tickets = len(data)  # easier than doing another query
        avg = 0 if tickets == 0 else round(commission / tickets, 2)  # same here
        return render_template("BookingAgentHome.html", commission=commission, tickets=tickets, avg=avg, days=days)
    else:
        return redirect('/logout')


@app.route('/BookingAgentViewFlights')
def BookingAgentViewFlights():
    if VerifyBookingAgent():
        # checking for flights with booking agent attached before and after current flight
        query = "SELECT * FROM flight, purchase, booking_agent, ticket, customer, airport as dep_port, airport as ar_port " \
                "WHERE flight.flight_num = ticket.flight_num  " \
                "AND ticket.ticket_id = purchase.ticket_id AND purchase.booking_agent_email = booking_agent.email  " \
                "AND flight.airline_name = ticket.flight_airline_name AND customer.email = purchase.customer_email  " \
                "AND booking_agent.email = %s AND departure_date {} CURDATE() AND ar_port.name = flight.arrival_airport_name  " \
                "AND dep_port.name = flight.departure_airport_name"
        cursor = conn.cursor()
        cursor.execute(query.format(">="), (session['email']))
        upcoming = cursor.fetchall()
        cursor.execute(query.format("<"), (session['email']))
        previous = cursor.fetchall()
        cursor.close()
        return render_template('BookingAgentViewFlights.html', upcoming=upcoming, previous=previous)
    else:
        return redirect('/logout')


@app.route('/BookingAgentSearchForFlights')
def BookingAgentSearchForFlights():
    if VerifyBookingAgent():
        return render_template("BookingAgentSearchForFlights.html", current_date=date.today())
    else:
        return redirect('/logout')


@app.route('/BookingAgentSearchForFlightsDisplay', methods=["GET", "POST"])
def BookingAgentSearchForFlightsDisplay():
    if VerifyBookingAgent():
        # looking for flights with capacity
        query = "SELECT * FROM purchasable_tickets WHERE tickets_sold < capacity"
        query_addition = []
        parameters = []
        departure_airport = request.form['departure_airport']
        arrival_airport = request.form['arrival_airport']
        departure_date = request.form['departure_date']
        arrival_date = request.form['arrival_date']
        departure_city = request.form['departure_city']
        arrival_city = request.form['arrival_city']
        # adding in optional query parameters
        if departure_airport:
            query_addition.append("departure_airport_name = %s")
            parameters.append(departure_airport)
        if arrival_airport:
            query_addition.append("arrival_airport_name = %s")
            parameters.append(arrival_airport)
        if departure_date:
            query_addition.append("departure_date = %s")
            parameters.append(departure_date)
        if arrival_date:
            query_addition.append("arrival_date = %s")
            parameters.append(arrival_date)
        if departure_city:
            query_addition.append("departure_city = %s")
            parameters.append(departure_city)
        if arrival_city:
            query_addition.append("arrival_city = %s")
            parameters.append(arrival_city)
        query = query + " AND " + " AND ".join(query_addition) if query_addition else query
        query += " ORDER BY departure_date DESC"  # want to show soonest flights first
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        data = cursor.fetchall()
        cursor.close()
        return render_template('BookingAgentSearchForFlightsDisplay.html', data=data, current_date=date.today())
    else:
        return redirect('/logout')


@app.route('/BookingAgentPurchaseAuth', methods=["GET", "POST"])
def BookingAgentPurchaseAuth():
    if VerifyBookingAgent():
        get = "SELECT * from purchasable_tickets where flight_num = %s and airline_name = %s and  tickets_sold < capacity  " \
              "and departure_time = %s and departure_date = %s"  # checking if requested flight is a valid future flight
        cursor = conn.cursor()
        cursor.execute(get, (
            request.form['flight_num'], request.form['airline_name'], request.form['departure_time'] + ':00',
            request.form['departure_date']))
        flight = cursor.fetchone()
        if flight:
            date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
            ticket_id = gen_id('ticket')
            # first gonna create the ticket
            ins_ticket = "INSERT into ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(ins_ticket, (
                ticket_id, flight['airline_name'], flight['flight_num'], request.form['price'], request.form['email'],
                request.form['debit_credit'], request.form['card_no'],
                request.form['cardholder'],
                request.form['card_exp']))
            # then create the purchase record
            ins_purchase = "INSERT into purchase VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(ins_purchase,
                           (ticket_id, request.form['email'], session['email'], date_time[0], date_time[1]))
            # then update the seats sold on the flight
            update = "UPDATE flight SET tickets_sold = tickets_sold + 1 WHERE flight_num = %s"
            cursor.execute(update, flight['flight_num'])
            commission_update = "UPDATE booking_agent SET commission = commission + %s * 0.10"
            cursor.execute(commission_update, request.form['price'])
            conn.commit()
            cursor.close()
            return redirect('/BookingAgentHome')
        flash('TICKET FAILED TO PURCHASE: FLIGHT NOT FOUND')
        cursor.close()
        return redirect('/BookingAgentHome')
    else:
        return redirect('/logout')


# AIRLINE STAFF VIEWS

def get_airline():
    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query, session['email'])
    data = cursor.fetchone()
    cursor.close()
    return data['airline_name']


@app.route('/AirlineStaffHome')
def AirlineStaffHome():
    if VerifyAirlineStaff():
        return render_template("AirlineStaffHome.html", name=session['username'], airline=get_airline())
    else:
        return redirect('/logout')


@app.route('/AirlineStaffViewFlights')
def AirlineStaffViewFlights():
    if VerifyAirlineStaff():
        return render_template("AirlineStaffViewFlights.html", airline=get_airline())
    return redirect('/logout')


@app.route('/AirlineStaffViewFlightsDisplay', methods=['GET', 'POST'])
def AirlineStaffViewFlightsDisplay():
    if VerifyAirlineStaff():
        # looking for flights run by this airline in specific range of departure dates
        query = "SELECT flight_status, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time,  " \
                "departure_airport_name, dep_port.city, arrival_airport_name, ar_port.city FROM flight,  " \
                "airport as dep_port, airport as ar_port WHERE dep_port.name = departure_airport_name and ar_port.name =  " \
                "arrival_airport_name AND departure_date >= %s AND departure_date <= %s AND airline_name = %s"
        query_addition = []
        departure_airport = request.form.get('departure_airport')
        arrival_airport = request.form.get('arrival_airport')
        first_departure_date = request.form.get('first_departure_date')
        first_departure_date = first_departure_date if first_departure_date else str(date.today())
        second_departure_date = request.form.get('second_departure_date')
        second_departure_date = second_departure_date if second_departure_date else str(
            datetime.strptime(first_departure_date, "%Y-%d-%m").date() + timedelta(days=30))
        departure_city = request.form.get('departure_city')
        arrival_city = request.form.get('arrival_city')
        parameters = [first_departure_date, second_departure_date, get_airline()]
        # optional filter parameters
        if departure_airport:
            query_addition.append("departure_airport_name = %s")
            parameters.append(departure_airport)
        if arrival_airport:
            query_addition.append("arrival_airport_name = %s")
            parameters.append(arrival_airport)
        if departure_city:
            query_addition.append("dep_port.city = %s")
            parameters.append(departure_city)
        if arrival_city:
            query_addition.append("ar_port.city = %s")
            parameters.append(arrival_city)
        query = query + " AND " + " AND ".join(query_addition) if query_addition else query
        query += " ORDER BY departure_date DESC"  # show soonest flights first
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        data = cursor.fetchall()
        cursor.close()
        return render_template('AirlineStaffViewFlightsDisplay.html', data=data, current_date=date.today())
    else:
        return redirect('/logout')


@app.route('/AirlineStaffCreateFlights', methods=["GET", "POST"])
def AirlineStaffCreateFlights():
    if VerifyAirlineStaff():
        airline = get_airline()
        cursor = conn.cursor()
        airport_exists = "SELECT * FROM airport WHERE name = %s"  # checking if airports exists
        cursor.execute(airport_exists, request.form['departure_airport_name'])
        d_airport_exists = cursor.fetchall()
        cursor.execute(airport_exists, request.form['arrival_airport_name'])
        a_airport_exists = cursor.fetchall()
        plane_exists = "SELECT * FROM airplane where ID = %s AND airline_name = %s"  # checking if plane exists and is owned by airline
        cursor.execute(plane_exists, (request.form['airplane_id'], get_airline()))
        # checking if departure date/time is before arrival date/time
        timevalid = True if request.form.get('departure_date') < request.form.get('arrival_date') else False
        if not timevalid:
            if request.form.get('departure_date') == request.form.get('arrival_date'):
                if request.form.get('departure_time') < request.form.get('arrival_time'):
                    timevalid = True
        if d_airport_exists and a_airport_exists and plane_exists and timevalid:
            # creating flight
            insert = "INSERT INTO flight VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(insert, (gen_id('plane', airline), airline, request.form['airplane_id'],
                                    request.form['departure_time'], request.form['departure_date'],
                                    request.form['departure_airport_name'],
                                    request.form['arrival_time'], request.form['arrival_date'],
                                    request.form['arrival_airport_name'],
                                    request.form['price'], 'on-time', 0))
            conn.commit()
            cursor.close()
            flash("Flight Created!")
            return redirect('/AirlineStaffHome')
        else:
            cursor.close()
            flash("INVALID INFORMATION")
            return redirect('/AirlineStaffViewFlightsDisplay')
    else:
        return redirect('/logout')


@app.route('/AirlineStaffChangeFlightStatus', methods=["GET", "POST"])
def AirlineStaffChangeFlightStatus():
    if VerifyAirlineStaff():
        query = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
        cursor = conn.cursor()
        cursor.execute(query, (get_airline(), request.form['flight_num']))
        data = cursor.fetchall()
        if data:
            query = "UPDATE flight SET flight.flight_status = %s WHERE flight_num = %s AND airline_name = %s"  # change flight status
            cursor.execute(query, (request.form['flight_status'], request.form['flight_num'], get_airline()))
            conn.commit()
            cursor.close()
            flash("Flight Status Changed")
            return redirect('/AirlineStaffHome')
        else:
            flash("No Such Flight Found")
            return redirect('/AirlineStaffHome')
    else:
        return redirect('/logout')


@app.route('/AirlineStaffCreate')
def AirlineStaffCreate():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        query = "SELECT * FROM airport"  # find existing airports
        cursor.execute(query)
        ports = cursor.fetchall()
        query = "SELECT * FROM airplane WHERE airline_name = %s"  # find existing airplanes
        cursor.execute(query, get_airline())
        planes = cursor.fetchall()
        return render_template("AirlineStaffCreate.html", ports=ports, planes=planes, airline=get_airline())
    return redirect('/logout')


@app.route('/AirlineStaffAddAirplane', methods=["GET", "POST"])
def AirlineStaffAddAirplane():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        # create airplane owned by airline with randomly generated ID
        insert = "INSERT INTO airplane VALUES(%s, %s, %s)"
        cursor.execute(insert, (gen_id('airplane'), get_airline(), request.form['seats']))
        conn.commit()
        cursor.close()
        flash('Airplane Successfully Added!')
        return redirect('/AirlineStaffHome')
    else:
        return redirect('/logout')


@app.route('/AirlineStaffAddAirport', methods=["GET", "POST"])
def AirlineStaffAddAirport():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        # check if user is erroneously adding an existing airport
        cursor.execute("SELECT * FROM airport WHERE name = %s", request.form['name'])
        port_exists = cursor.fetchall()
        if not port_exists:
            insert = "INSERT INTO airport VALUES(%s,%s)"  # create airport with user input
            cursor.execute(insert, (request.form['name'], request.form['city']))
            conn.commit()
            cursor.close()
            flash("Airport Successfully Added!")
            return redirect('/AirlineStaffHome')
        else:
            flash("Airport Already Exists!")
            return redirect('/AirlineStaffHome')
    else:
        return redirect('/logout')


@app.route('/AirlineStaffStats', methods=['GET', 'POST'])
def AirlineStaffStats():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        # getting average ratings for all flights run by this airline
        get_avg_ratings = "SELECT AVG(rating) as avg, flight_num FROM ratings NATURAL JOIN flight NATURAL JOIN customer  " \
                          "WHERE airline_name = %s GROUP BY flight_num ORDER BY avg DESC"
        cursor.execute(get_avg_ratings, get_airline())
        avg_ratings = cursor.fetchall()
        # getting tickets sold from all booking agents in database
        get_top_agents = "SELECT COUNT(ticket_id) as tickets_sold, booking_agent_email FROM purchase WHERE  " \
                         "booking_agent_email IS NOT NULL GROUP BY booking_agent_email ORDER BY tickets_sold DESC"
        cursor.execute(get_top_agents)
        top_agents = cursor.fetchall()
        top_agents = top_agents[:5] if len(top_agents) > 5 else top_agents
        # finding arrival city with most tickets purchased for it
        get_top_dest = "SELECT COUNT(ticket_id) AS trips_made, airport.city as arrival_city FROM flight, airport, ticket NATURAL JOIN purchase WHERE  " \
                       "ticket.flight_num = flight.flight_num AND ticket.flight_airline_name = flight.airline_name  " \
                       "AND flight.arrival_airport_name = airport.name AND purchase.purchase_date > DATE_SUB(CURDATE(), INTERVAL {})  " \
                       "GROUP BY arrival_city ORDER BY trips_made DESC"
        dest_three_months = get_top_dest.format("3 MONTH")
        dest_year = get_top_dest.format("1 YEAR")
        cursor.execute(dest_three_months)
        dest_three_months = cursor.fetchall()
        cursor.execute(dest_year)
        dest_year = cursor.fetchall()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        graphs('AirlineStaff', start_date, end_date)
        current_date = str(date.today())
        return render_template('AirlineStaffStats.html', airline=get_airline(), avg_ratings=avg_ratings,
                               current_date=current_date,
                               top_agents=top_agents, dest_three_months=dest_three_months, dest_year=dest_year)
    else:
        return redirect('/logout')


@app.route('/AirlineStaffReview', methods=['GET', 'POST'])
def AirlineStaffReview():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        # checking if requested flight exists
        check_flight = "SELECT * FROM flight WHERE flight_num = %s and airline_name = %s"
        cursor.execute(check_flight, (request.form.get('flight_num'), get_airline()))
        data = cursor.fetchone()
        if data:
            # fetching ratings for flight
            get_ratings = "SELECT * FROM ratings NATURAL JOIN customer WHERE airline_name = %s and flight_num = %s"
            cursor.execute(get_ratings, (get_airline(), request.form.get('flight_num')))
            ratings = cursor.fetchall()
            return render_template("AirlineStaffReview.html", ratings=ratings,
                                   flight_num=request.form.get('flight_num'))
        flash("ERROR: Flight specified does not exist")
        return redirect('/AirlineStaffStats')
    return redirect('/logout')


if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
