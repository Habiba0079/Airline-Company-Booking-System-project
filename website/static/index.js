// index.js

// Function to add a new passenger
function addPassenger() {
    fetch('/add_passenger', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            first_name: 'Alice',
            last_name: 'Doe',
            email: 'alice@example.com',
            phone: '9876543210',
            address: '789 Oak St.'
        })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

// Function to view available flights
function viewFlights() {
    fetch('/view_flights')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

// Function to book a flight
function bookFlight() {
    fetch('/book_flight', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            passenger_id: 1,
            flight_id: 1,
            seat_number: '15A',
            ticket_class: 'Economy',
            price: 300
        })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

// Function to delete a booked ticket
function deleteBookedTicket() {
    fetch('/delete_booked_ticket', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            ticket_id: 1,
            passenger_id: 1
        })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

// Call functions to interact with the Flask API
addPassenger();
viewFlights();
bookFlight();
deleteBookedTicket();
