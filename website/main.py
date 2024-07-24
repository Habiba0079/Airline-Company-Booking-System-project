from flask import Flask, request, render_template, jsonify
import mysql.connector
import datetime


app = Flask(__name__)

# Establish MySQL database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="W7301@jqir#",  #MySQL password 
    database="airline"
)

# Initialize database schema if not exists
def initialize_database():
    cursor = mydb.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            FlightNumber VARCHAR(100) PRIMARY KEY,
            DepartureAirport VARCHAR(255),
            ArrivalAirport VARCHAR(255),
            DepartureDateTime DATETIME,
            ArrivalDateTime DATETIME,
            TotalSeats INT
        )
    ''')




    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            TicketID INT AUTO_INCREMENT PRIMARY KEY,
            PassengerID INT ,
            PassengerName VARCHAR(255),
            FlightNumber VARCHAR(100),   
            DepartureAirport VARCHAR(255),
            ArrivalAirport VARCHAR(255),
            DepartureDateTime DATETIME,
            NumberOfTickets INT,
            TicketClass VARCHAR(20),
            FOREIGN KEY (FlightNumber) REFERENCES flights(FlightNumber)
           
        )
    ''')

    mydb.commit()
    cursor.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check_booking", methods=["GET", "POST"])
def check_booking():
    if request.method == "POST":
        # Handle POST request to check bookings
        # Retrieve data from JSON request
        data = request.json
        passenger_name = data.get("passengerName")
        passenger_id = data.get("passengerID")
        flight_number = data.get("flightNumber")

        # Execute SQL query to search bookings
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets WHERE PassengerName = %s AND PassengerID = %s AND FlightNumber = %s", (passenger_name, passenger_id, flight_number))
        bookings = cursor.fetchall()
        cursor.close()

        if bookings:
            return jsonify({"success": True, "bookings": bookings})
        else:
            return jsonify({"success": False, "message": "No bookings found for the provided criteria."})
    else:
        # Handle GET request, render a template or return an error response
        return render_template("check_booking.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        # Retrieve data from JSON request
        data = request.json
        passenger_name = data.get("passengerName")
        passenger_id = data.get("passengerID")
        from_location = data.get("from")
        to_location = data.get("to")
        date = data.get("date")
        flight_number = data.get("flightNumber")
        num_tickets = int(data.get("numTickets"))  # Convert num_tickets to integer
        ticket_class = data.get("class")

        # Validate the date format
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"success": False, "message": "Invalid date format. Please use YYYY-MM-DD."})

        # Check if the flight exists in the flights table
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM flights WHERE FlightNumber = %s AND DepartureAirport = %s AND ArrivalAirport = %s", (flight_number, from_location, to_location))
        flight = cursor.fetchone()

        if not flight:
            cursor.close()
            return jsonify({"success": False, "message": "Flight not found for the provided details."})

        # Check if there are enough available seats on the flight
        cursor.execute("SELECT SUM(NumberOfTickets) FROM tickets WHERE FlightNumber = %s", (flight_number,))
        result = cursor.fetchone()
        print("Result:", result)
        if result and result['SUM(NumberOfTickets)'] is not None:
            total_booked_tickets = result['SUM(NumberOfTickets)']
        else:
            total_booked_tickets = 0

        available_seats = flight['TotalSeats'] - total_booked_tickets
        if num_tickets > available_seats:
            cursor.close()
            return jsonify({"success": False, "message": "Not enough available seats for the requested number of tickets."})

        # Extract departure time from the flight information
        departure_time = flight['DepartureDateTime'].strftime('%H:%M:%S')

        # Combine date and time to create the departure datetime
        departure_datetime = datetime.datetime.combine(date, datetime.datetime.strptime(departure_time, '%H:%M:%S').time())

        # If the flight exists and there are enough available seats, insert booking information into the tickets table
        cursor.execute("INSERT INTO tickets (PassengerID, PassengerName, FlightNumber, DepartureAirport, ArrivalAirport, DepartureDateTime, NumberOfTickets, TicketClass) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (passenger_id, passenger_name, flight_number, from_location, to_location, departure_datetime, num_tickets, ticket_class))
        mydb.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Booking successful!"})

    else:
        # Fetch the unique list of departure and arrival airports from the database
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT DepartureAirport FROM flights")
        departure_airports = cursor.fetchall()
        cursor.execute("SELECT DISTINCT ArrivalAirport FROM flights")
        arrival_airports = cursor.fetchall()
        cursor.close()

        # Render the book.html template with the flights data
        return render_template("book.html", departure_airports=departure_airports, arrival_airports=arrival_airports)





@app.route("/time_table", methods=["GET", "POST"])
def time_table():
    if request.method == "POST":
        # Retrieve data from JSON request
        data = request.json
        print(data)
        from_country = data.get("from")
        to_country = data.get("to")
        date_str = data.get("date")

        # Check if date is in the correct format (YYYY-MM-DD)
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

        # Check if date is in the past
        if date < datetime.datetime.now().date():
            return jsonify({"error": "Date cannot be in the past."}), 400

        # Execute SQL query to search flights
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM flights WHERE DepartureAirport = %s AND ArrivalAirport = %s AND DATE(DepartureDateTime) = %s", (from_country, to_country, date))
        flights = cursor.fetchall()
        cursor.close()

        # Convert result to JSON and return
        return jsonify(flights)
    else:
        # Handle GET request for rendering the time_table.html template
        return render_template("time_table.html")




if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)