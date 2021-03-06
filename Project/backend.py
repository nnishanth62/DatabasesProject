from flask import Flask, render_template, request, session, redirect, flash
import pymysql
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import secrets
from hashlib import md5
from datetime import datetime, time, date
import time

app = Flask(__name__)
# WANT NO CACHING BECAUSE WE WANT GRAPHS TO CONSTANTLY UPDATE
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root', # I didn't need a password, so that's strange
                       db='dbproject',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = secrets.token_urlsafe(16)


def gen_id(table, airline_name=None):
    # generates either a unique ticket or flight ID
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
    return table_id[:7]

# GRAPHS
def graphs(plot, start_date=None, end_date=None):
    cursor = conn.cursor()
    if plot == "Cust":
        if VerifyCustomer():
            if start_date and end_date:
                query = "SELECT * FROM ticket natural join purchase natural join flight WHERE purchase_date > %s and purchase_date < %s AND customer_email = %s"
                cursor.execute(query, (start_date, end_date, session['email']))
            else:
                if start_date:
                    query = "SELECT * FROM ticket natural join purchase natural join flight WHERE purchase_date > %s AND " \
                            "customer_email = %s AND flight_airline_name = airline_name"
                    cursor.execute(query, (start_date, session['email']))
                else:
                    query = "SELECT * FROM ticket natural join purchase natural join flight WHERE purchase_date > DATE_SUB(CURDATE(), INTERVAL 6 MONTH) AND customer_email = %s" \
                            "AND flight_airline_name = airline_name"
                    cursor.execute(query, session['email'])
            data = cursor.fetchall()
            graphdata = {}
            for line in data:
                curr_month = line['purchase_date'].strftime('%Y-%m')
                curr_price = int(line['sold_price'])
                graphdata[curr_month] = graphdata[curr_month] + curr_price if curr_month in graphdata else curr_price
            plt.bar(list(graphdata.keys()), list(graphdata.values()))
            plt.title('Amount of Money Spent per Month')
            plt.savefig("templates/graphs/CustSpendingGraph.png")
        else:
            return redirect('/logout')
    elif plot == "BookingAgent":
        if VerifyBookingAgent():
            query = "SElECT SUM(sold_price)*0.1 as commission, first_name, last_name, customer.email FROM ticket NATURAL JOIN purchase, customer WHERE customer.email = customer_email" \
                    " AND booking_agent_email = %s GROUP BY customer.email ORDER BY commission DESC"
            cursor = conn.cursor()
            cursor.execute(query, session['email'])
            data = cursor.fetchall()
            if len(data) > 5:
                data = data[:5]
            x = [line['first_name'] + ' ' + line['last_name'] for line in data]
            y = [int(line['commission']) for line in data]
            plt.bar(x, y)
            plt.title('Top 5 Customers by Commission')
            plt.savefig("templates/graphs/BookingAgentCommissionGraph.png")
            query = "SElECT COUNT(ticket_id) as ticket_sales, customer.email, first_name, last_name FROM ticket NATURAL JOIN purchase, customer WHERE customer.email = customer_email" \
                    " AND booking_agent_email = %s GROUP BY customer.email ORDER BY ticket_sales DESC"
            cursor.execute(query, session['email'])
            data = cursor.fetchall()
            if len(data) > 5:
                data = data[:5]
            x = [line['first_name'] + ' ' + line['last_name'] for line in data]
            y = [int(line['ticket_sales']) for line in data]
            plt.bar(x, y)
            plt.title('Top 5 Customers by Tickets Sold')
            plt.savefig("templates/graphs/BookingAgentTicketGraph.png")
            cursor.close()
        else:
            return redirect('/logout')
    elif plot == "AirlineStaff":
        if VerifyAirlineStaff():
            if start_date and end_date:
                query = "SELECT * FROM ticket NATURAL JOIN purchase WHERE flight_airline_name = %s AND purchase_date >= %s AND purchase_date <= %s"
                cursor.execute(query, (get_airline(), start_date, end_date))
            else:
                if start_date:
                    query = "SELECT * FROM ticket NATURAL JOIN purchase WHERE flight_airline_name = %s AND purchase_date >= %s"
                    cursor.execute(query, (get_airline(), start_date))
                else:
                    query = "SELECT * FROM ticket NATURAL JOIN purchase WHERE flight_airline_name = %s AND purchase_date >=" \
                            " DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
                    cursor.execute(query, get_airline())
            ticket_count = cursor.fetchall()
            graphdata = {}
            for line in ticket_count:
                curr_month = line['purchase_date'].strftime('%Y-%m')
                graphdata[curr_month] = graphdata[curr_month] + 1 if curr_month in graphdata else 1
            plt.bar(list(graphdata.keys()), list(graphdata.values()))
            plt.title('Ticket Sales for %s by Month' % get_airline())
            plt.savefig('templates/graphs/AirlineStaffTicketCount.png')
            # PIE CHART FOR BA VS CUST PURCHASES
            query = "SELECT COUNT(ticket_id) as count FROM purchase NATURAL JOIN ticket WHERE flight_airline_name = %s AND booking_agent_email {} NULL"
            cursor.execute(query.format('<>'), get_airline())
            ba_count = int(cursor.fetchone()['count'])
            cursor.execute(query.format('='), get_airline())
            cust_count = int(cursor.fetchone()['count'])
            plt.pie((ba_count, cust_count), labels=("Booking Agent Sales", "Customer Sales"))
            plt.title('Booking Agent vs Customer Ticket Purchases')
            plt.savefig('templates/graphs/AirlineStaffBAvCustSales.png')
        else:
            return redirect('/logout')


@app.route('/CustSpendingGraph')
def CustSpendingGraph():
    if VerifyCustomer():
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        graphs("Cust", start_date, end_date)
        return redirect('/CustHome')
    else:
        return redirect('/logout')


# VERIFICATION

def VerifyCustomer():
    """
    verifies if there is a customer with the current session's email
    should be used to check whether the user is trying to inappropriately access a customer method
    :return data: tuple of query result, can use "if VerifyCustomer():" to check whether or not it's empty.
    EXAMPLE USE IN CUSTHOME() FUNCTION
    """
    if session.get('type') == 'Cust':
        verify = "SELECT * FROM customer WHERE email = %s"
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
    """
    almost identical to VerifyCustomer(), should be used identically in airline staff functions
    """
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
    query = "SELECT * FROM customer WHERE email = %s and cust_password = %s"
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    if data:
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
    query = "SELECT * FROM booking_agent WHERE email = %s and agent_password = %s and booking_agent_id = %s"
    cursor.execute(query, (email, password, booking_agent_id))
    data = cursor.fetchone()
    cursor.close()
    if data:
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
    query = "SELECT * FROM airline_staff WHERE username  = %s and staff_password = %s"
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    if data:
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
    query = "SELECT * FROM customer WHERE email = %s"
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
        address = request.form['address'].split(', ')
        ind = address[0].find(' ')
        num_name = address[0]
        address.insert(0, num_name)
        address[0] = address[0][:ind].strip()
        address[1] = address[1][ind:].strip()
        passport_no = request.form['passport_number']
        passport_country = request.form['passport_country']
        passport_exp = request.form['passport_expiration']
        dob = request.form['DOB']
        ins = "INSERT INTO customer values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
    query = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query, username)
    data = cursor.fetchone()
    if data:
        cursor.close()
        flash("USER ALREADY EXISTS")
        return render_template('registerAirlineStaff.html')
    else:
        fname = request.form['first_name']
        lname = request.form['last_name']
        password = md5(request.form['password'].encode()).hexdigest()
        dob = request.form['DOB']
        airline = request.form['airline_name']
        ins = "INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)"
        cursor.execute(ins, (username, fname, lname, password, dob, airline))
        conn.commit()
        cursor.close()
        flash("SUCCESSFULLY REGISTERED AIRLINE STAFF")
        return redirect('/')


@app.route('/registerAuthBookingAgent', methods=["GET", "POST"])
def registerAuthBookingAgent():
    email = request.form['email']
    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = %s"
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
        ins = "INSERT INTO booking_agent VALUES(%s, %s, %s, %s)"
        cursor.execute(ins, (email, agent_id, password, commission))
        conn.commit()
        cursor.close()
        flash("SUCCESSFULLY REGISTERED AIRLINE STAFF")
        return redirect('/')


@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        session.pop('email', None)
        session.pop('type', None)
    except KeyError:
        pass
    return redirect('/')


# PUBLIC VIEWS

@app.route('/publicviewSearch')
def publicviewSearch():
    return render_template("publicviewSearch.html")


@app.route('/publicviewDisplay', methods=["GET", "POST"])
def publicviewDisplay():
    query = "SELECT * FROM purchasable_tickets WHERE departure_date >= CURDATE() AND tickets_sold < capacity"
    query_addition = []
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    ### NEED TO REWORK THIS SO WE USE EXECUTE() SQL INJECTION PROTECTION
    if departure_airport != '':
        query_addition.append("departure_airport_name = '%s'" % departure_airport)
    if arrival_airport != '':
        query_addition.append("arrival_airport_name = '%s'" % arrival_airport)
    if departure_date != '':
        query_addition.append("departure_date = '%s'" % departure_date)
    if arrival_date != '':
        query_addition.append("arrival_date = '%s'" % arrival_date)
    if departure_city != '':
        query_addition.append("departure_city = '%s'" % departure_city)
    if arrival_city != '':
        query_addition.append("arrival_city = '%s'" % arrival_city)
    if query_addition:
        query += " and " + " and ".join(query_addition)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('publicviewDisplay.html', data=data)


@app.route('/Home')
def Home():
    if VerifyAirlineStaff():
        return redirect('/AirlineStaffHome')
    elif VerifyBookingAgent():
        return redirect('/BookingAgentHome')
    elif VerifyCustomer():
        return redirect('/CustHome')
    else:
        return redirect('/')


# CUSTOMER VIEWS
@app.route('/CustHome')
def CustHome():
    if VerifyCustomer():  # if looking for their name has a result, send them to home
        graphs("Cust")
        current_date = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()[0]
        name = session['username']
        return render_template("CustHome.html", current_date=current_date, name=name)
    else:  # otherwise we just kill their session
        return redirect('/logout')

@app.route('/CustViewMyFlights')
def CustViewMyFlights():
    if VerifyCustomer():
        query = "SELECT * FROM purchase natural join ticket natural join purchasable_tickets WHERE airline_name = flight_airline_name " \
                "AND purchase.customer_email = %s and departure_date >= CURDATE()"
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
        return render_template("CustSearchForFlights.html")
    else:
        return redirect('/logout')


@app.route('/CustSearchForFlightsDisplay', methods=["GET", "POST"])
def CustSearchForFlightsDisplay():
    if VerifyCustomer():
        query = "SELECT * FROM purchasable_tickets WHERE tickets_sold < capacity"
        query_addition = []
        departure_airport = request.form['departure_airport']
        arrival_airport = request.form['arrival_airport']
        departure_date = request.form['departure_date']
        arrival_date = request.form['arrival_date']
        departure_city = request.form['departure_city']
        arrival_city = request.form['arrival_city']
        # REWORK THIS FOR SQL INJECTION PROTECTION
        if departure_airport != '':
            query_addition.append("departure_airport_name = '%s'" % departure_airport)
        if arrival_airport != '':
            query_addition.append("arrival_airport_name = '%s'" % arrival_airport)
        if departure_date != '':
            query_addition.append("departure_date = '%s'" % departure_date)
        if arrival_date != '':
            query_addition.append("arrival_date = '%s'" % arrival_date)
        if departure_city != '':
            query_addition.append("departure_city = '%s'" % departure_city)
        if arrival_city != '':
            query_addition.append("arrival_city = '%s'" % arrival_city)
        if query_addition:
            query += " and " + " and ".join(query_addition)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        for line in data:
            start_price = float(line['price'])
            line['price'] = start_price if line['capacity']*.7 > line['tickets_sold'] else start_price*1.2
            line['price'] = str(line['price'])
        return render_template('CustSearchForFlightsDisplay.html', data=data)
    else:
        return redirect('/logout')


@app.route('/CustPurchaseFlightAuth', methods=["GET", "POST"])
def CustPurchaseFlightAuth():
    if VerifyCustomer():
        get = "SELECT * from purchasable_tickets where flight_num = %s and airline_name = %s and  tickets_sold < capacity" \
              "and departure_time = %s and departure_date = %s"
        cursor = conn.cursor()
        cursor.execute(get, (request.form['flight_num'], request.form['airline_name'], request.form['departure_time'], #deleted :00
                             request.form['departure_date']))
        flight = cursor.fetchone()
        if flight:
            price = float(flight['price']) if float(flight['capacity'])*.7 > float(flight['tickets_sold']) else float(flight['price'])*1.2
            date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
            ticket_id = gen_id('ticket')
            # first gonna create the ticket
            ins_ticket = "INSERT into ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(ins_ticket, (ticket_id, flight['airline_name'], flight['flight_num'], price, session['email'],
                                        request.form['debit_credit'], request.form['card_no'],
                                        request.form['cardholder'],
                                        request.form['card_exp']))
            # then i wanna create the purchase record (NULL value is booking agent email)
            ins_purchase = "INSERT into purchase VALUES (%s, %s, NULL, %s, %s)"
            cursor.execute(ins_purchase, (ticket_id, session['email'], date_time[0], date_time[1]))
            # then i wanna update the seats sold on the flight
            update = "UPDATE flight SET tickets_sold = tickets_sold + 1 WHERE flight_num = %s AND airline_name = %s AND departure_date = %s" \
                     "AND departure_time = %s"
            cursor.execute(update, (flight['flight_num'], flight['airline_name'], flight['departure_date'], flight['departure_time']))
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
        date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
        cursor = conn.cursor()
        query = "SELECT * FROM flight natural join ticket natural join customer WHERE ticket.customer_email = customer.email" \
                " AND customer_email = %s and flight.arrival_date < %s AND flight.airline_name = ticket.flight_airline_name"
        cursor.execute(query, (session['email'], date_time[0]))
        allflights = cursor.fetchall()
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
        date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
        cursor = conn.cursor()
        query = "SELECT * FROM flight natural join ticket LEFT OUTER JOIN ratings WHERE flight.airline_name" \
                " = ticket.flight_airline_name AND ticket.customer_email != ratings.email and ticket.customer_email = %s" \
                "flight.arrival_date < %s AND flight_num = %s AND airline_name = %s"
        cursor.execute(query,
                       (session['email'], date_time[0], request.form['flight_num'], request.form['airline_name']))
        data = cursor.fetchall()
        if data:
            ins = "INSERT INTO ratings VALUES(%s, %s, %s, %s, %s)"
            cursor.execute(ins, (session['email'], request.form['flight_num'], request.form['airline_name'],
                                 request.form['comments'], request.form['rating']))
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
        days = request.form.get('days', 30)
        name = session['username']
        query = "SELECT * FROM ticket natural join purchase WHERE booking_agent_email = %s AND purchase_date > DATE_SUB(CURDATE(), INTERVAL %s DAY)"
        cursor = conn.cursor()
        cursor.execute(query, (name, days))
        data = cursor.fetchall()
        cursor.close()
        commission = sum([int(line['sold_price']) for line in data]) * 0.1
        tickets = len(data)
        avg = 0 if tickets == 0 else round(commission/tickets, 2)
        return render_template("BookingAgentHome.html", commission=commission, tickets=tickets, avg=avg)
    else:
        return redirect('/logout')


@app.route('/BookingAgentViewFlights')
def BookingAgentViewFlights():
    if VerifyBookingAgent():
        query = "SELECT * FROM flight, purchase, booking_agent, ticket, customer, airport as dep_port, airport as ar_port WHERE flight.flight_num = ticket.flight_num " \
                "AND ticket.ticket_id = purchase.ticket_id AND purchase.booking_agent_email = booking_agent.email " \
                "AND flight.airline_name = ticket.flight_airline_name AND customer.email = purchase.customer_email " \
                "AND booking_agent.email = %s AND departure_date > CURDATE() AND ar_port.name = flight.arrival_airport_name " \
                "AND dep_port.name = flight.departure_airport_name"
        cursor = conn.cursor()
        cursor.execute(query, (session['email']))
        data = cursor.fetchall()
        print(data)
        cursor.close()
        return render_template('BookingAgentViewFlights.html', data=data)
    else:
        return redirect('/logout')


@app.route('/BookingAgentSearchForFlights')
def BookingAgentSearchForFlights():
    if VerifyBookingAgent():
        return render_template("BookingAgentSearchForFlights.html")
    else:
        return redirect('/logout')


@app.route('/BookingAgentSearchForFlightsDisplay', methods=["GET", "POST"])
def BookingAgentSearchForFlightsDisplay():
    if VerifyBookingAgent():
        query = "SELECT * FROM purchasable_tickets WHERE tickets_sold < capacity"
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
            query_addition.append("departure_city = '%s'" % departure_city)
        if arrival_city != '':
            query_addition.append("arrival_city = '%s'" % arrival_city)
        if query_addition:
            query += " and " + " and ".join(query_addition)
        cursor = conn.cursor()
        print(query)
        cursor.execute(query)
        data = cursor.fetchall()
        print(data)
        cursor.close()
        return render_template('BookingAgentSearchForFlightsDisplay.html', data=data)
    else:
        return redirect('/logout')


@app.route('/BookingAgentPurchaseAuth', methods=["GET", "POST"])
def BookingAgentPurchaseAuth():
    if VerifyBookingAgent():
        get = "SELECT * from purchasable_tickets where flight_num = %s and airline_name = %s and  tickets_sold < capacity " \
              "and departure_time = %s and departure_date = %s"
        cursor = conn.cursor()
        cursor.execute(get, (request.form['flight_num'], request.form['airline_name'], request.form['departure_time']+':00',
                             request.form['departure_date']))
        flight = cursor.fetchone()
        if flight:
            date_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()
            ticket_id = gen_id('ticket')
            # first gonna create the ticket
            ins_ticket = "INSERT into ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(ins_ticket, (ticket_id, flight['airline_name'], flight['flight_num'], request.form['price'], request.form['email'],
                                        request.form['debit_credit'], request.form['card_no'],
                                        request.form['cardholder'],
                                        request.form['card_exp']))
            # then i wanna create the purchase record
            ins_purchase = "INSERT into purchase VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(ins_purchase,
                           (ticket_id, request.form['email'], session['email'], date_time[0], date_time[1]))
            # then i wanna update the seats sold on the flight
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
        name = session['username']
        return render_template("AirlineStaffHome.html", name=name)
    else:
        return redirect('/logout')


@app.route('/AirlineStaffViewFlights')
def AirlineStaffViewFlights():
    if VerifyAirlineStaff():
        return render_template("AirlineStaffViewFlights.html")
    return redirect('/logout')


@app.route('/AirlineStaffViewFlightsDisplay', methods=['GET', 'POST'])
def AirlineStaffViewFlightsDisplay():
    if VerifyAirlineStaff():
        query = "SELECT flight_status, airline_name, flight_num, departure_date, departure_time, arrival_date, arrival_time, " \
                "departure_airport_name, dep_port.city, arrival_airport_name, ar_port.city FROM flight, " \
                "airport as dep_port, airport as ar_port WHERE dep_port.name = departure_airport_name and ar_port.name = " \
                "arrival_airport_name AND departure_date >= {} AND departure_date <= {} AND airline_name = %s"
        query_addition = []
        departure_airport = request.form.get('departure_airport')
        arrival_airport = request.form.get('arrival_airport')
        first_departure_date = request.form.get('first_departure_date')
        first_departure_date = first_departure_date if first_departure_date else "CURDATE()"
        second_departure_date = request.form.get('second_departure_date')
        second_departure_date = second_departure_date if second_departure_date else "DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
        departure_city = request.form.get('departure_city')
        arrival_city = request.form.get('arrival_city')
        ### NEED TO REWORK THIS SO WE USE EXECUTE() SQL INJECTION PROTECTION
        if departure_airport != '':
            query_addition.append("departure_airport_name = '%s'" % departure_airport)
        if arrival_airport != '':
            query_addition.append("arrival_airport_name = '%s'" % arrival_airport)
        if departure_city != '':
            query_addition.append("dep_port.city = '%s'" % departure_city)
        if arrival_city != '':
            query_addition.append("ar_port.city = '%s'" % arrival_city)
        query = query + " AND " + " AND ".join(query_addition) if query_addition else query
        cursor = conn.cursor()
        cursor.execute(query.format(first_departure_date, second_departure_date), (get_airline()))
        print((query.format(first_departure_date, second_departure_date), (get_airline())))
        data = cursor.fetchall()
        print(data)
        cursor.close()
        return render_template('AirlineStaffViewFlightsDisplay.html', data=data)
    else:
        return redirect('/logout')


@app.route('/AirlineStaffCreateFlights', methods=["GET", "POST"])
def AirlineStaffCreateFlights():
    if VerifyAirlineStaff():
        airline = get_airline()
        cursor = conn.cursor()
        airport_exists = "SELECT * FROM airport WHERE name = %s"
        cursor.execute(airport_exists, request.form['departure_airport_name'])
        d_airport_exists = cursor.fetchall()
        airport_exists = "SELECT * FROM airport WHERE name = %s"
        cursor.execute(airport_exists, request.form['arrival_airport_name'])
        a_airport_exists = cursor.fetchall()
        plane_exists = "SELECT * FROM airplane where ID = %s AND airline_name = %s"
        cursor.execute(plane_exists, (request.form['airplane_id'], get_airline()))
        if d_airport_exists and a_airport_exists and plane_exists:
            insert = "INSERT INTO flight VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(insert, (gen_id('plane', airline), airline, request.form['airplane_id'],
                                    request.form['departure_time']+":00", request.form['departure_date'],
                                    request.form['departure_airport_name'],
                                    request.form['arrival_time']+":00", request.form['arrival_date'],
                                    request.form['arrival_airport_name'],
                                    request.form['price'], 'on-time', 0))
        conn.commit()
        cursor.close()
        flash("Flight Created!")
        return redirect('/AirlineStaffHome')
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
            query = "UPDATE flight SET flight.flight_status = %s WHERE flight_num = %s AND airline_name = %s"
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
        query = "SELECT * FROM airport"
        cursor.execute(query)
        ports = cursor.fetchall()
        query = "SELECT * FROM airplane WHERE airline_name = %s"
        cursor.execute(query, get_airline())
        planes = cursor.fetchall()
        return render_template("AirlineStaffCreate.html", ports=ports, planes=planes)
    return redirect('/logout')


@app.route('/AirlineStaffAddAirplane', methods=["GET", "POST"])
def AirlineStaffAddAirplane():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
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
        insert = "INSERT INTO airport VALUES(%s,%s)"
        cursor.execute(insert, (request.form['name'], request.form['city']))
        conn.commit()
        cursor.close()
        flash("Airport Successfully Added!")
        return redirect('/AirlineStaffHome')
    else:
        return redirect('/logout')


@app.route('/AirlineStaffViewTopDestinations', methods=["GET", "POST"])
def AirlineStaffViewTopDestinations():
    if VerifyAirlineStaff():
        query = "SELECT arrival_airport_name, count(t.ticket_id) FROM flight f JOIN ticket t ON f.flight_num = t.flight_num " \
                "JOIN purchase p ON t.ticket_id = p.ticket_id AND p.purchase_date >= %s " \
                "GROUP BY arrival_airport_name ORDER BY count(t.ticket_id) desc LIMIT 5"
        cursor = conn.cursor()
        cursor.execute(query, request.form['purchase_date'])
        data = cursor.fetchall()
        cursor.close()
        return render_template('AirlineStaffViewTopDestinations.html', data=data)
    else:
        return redirect('/logout')


@app.route('/AirlineStaffStats', methods=['GET', 'POST'])
def AirlineStaffStats():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        get_avg_ratings = "SELECT AVG(rating) as avg, flight_num FROM ratings NATURAL JOIN flight NATURAL JOIN customer " \
                          "WHERE airline_name = %s GROUP BY flight_num"
        cursor.execute(get_avg_ratings, get_airline())
        avg_ratings = cursor.fetchall()
        get_top_agents = "SELECT COUNT(ticket_id) as tickets_sold, booking_agent_email FROM purchase WHERE " \
                         "booking_agent_email <> NULL GROUP BY booking_agent_email ORDER BY tickets_sold DESC"
        cursor.execute(get_top_agents)
        top_agents = cursor.fetchall()
        top_agents = top_agents[:5] if len(top_agents) > 5 else top_agents
        get_top_dest = "SELECT COUNT(ticket_id) AS trips_made, airport.city as arrival_city FROM flight, airport, ticket NATURAL JOIN purchase WHERE " \
                       "ticket.flight_num = flight.flight_num AND ticket.flight_airline_name = flight.airline_name " \
                       "AND flight.arrival_airport_name = airport.name AND purchase.purchase_date > DATE_SUB(CURDATE(), INTERVAL {})"
        dest_three_months = get_top_dest.format("3 MONTH")
        dest_year = get_top_dest.format("1 YEAR")
        cursor.execute(dest_three_months)
        dest_three_months = cursor.fetchall()
        cursor.execute(dest_year)
        dest_year = cursor.fetchall()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        graphs('AirlineStaff', start_date, end_date)
        current_date = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S').split()[0]
        return render_template('AirlineStaffStats.html', airline=get_airline(), avg_ratings=avg_ratings,
                               current_date=current_date,
                               top_agents=top_agents, dest_three_months=dest_three_months, dest_year=dest_year)
    else:
        return redirect('/logout')


@app.route('/AirlineStaffReview', methods=['GET', 'POST'])
def AirlineStaffReview():
    if VerifyAirlineStaff():
        cursor = conn.cursor()
        check_flight = "SELECT * FROM flight WHERE flight_num = %s and airline_name = %s"
        cursor.execute(check_flight, (request.form.get('flight_num'), get_airline()))
        data = cursor.fetchone()
        if data:
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
