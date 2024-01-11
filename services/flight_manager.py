import random
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.orm import Session
from models import Flight, FlightModel, get_db
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

def generate_flight_number():
    # Example: AA342
    return f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100, 999)}"

def choose_airline():
    # Example airlines
    airlines = ['Phantom', 'DreamSky Airlines', 'VirtualJet', 'Enchanted Air', 'AeroFiction']
    return random.choice(airlines)

def calculate_times(origin, destination):
    # Randomly add 1 to 10 hours to the current time for departure
    hours_to_add = random.randint(1, 10)
    departure_time = datetime.now() + timedelta(hours=hours_to_add)

    # Random duration for the flight between 30 mins to 10 hours
    duration = timedelta(minutes=random.randint(30, 600))
    arrival_time = departure_time + duration

    return departure_time, arrival_time

def generate_flights(flight_input, num_flights, db: Session):
    flights = []
    
    for _ in range(num_flights):
        flight_number = generate_flight_number()
        airline = choose_airline()
        departure_time, arrival_time = calculate_times(flight_input.origin, flight_input.destination)
        
        open_seats_economy = random.randint(0, 200)  
        open_seats_business = random.randint(0, 50)
        open_seats_first_class = random.randint(0, 20)

        economy_seat_cost = random.randint(50, 500)  
        business_seat_cost = random.randint(500, 1500)
        first_class_cost = random.randint(1500, 3000)

        new_flight = Flight(
            flight_number=flight_number,
            airline=airline,
            origin=flight_input.origin,
            destination=flight_input.destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            date=flight_input.date,
            open_seats_economy=open_seats_economy,
            open_seats_business=open_seats_business,
            open_seats_first_class=open_seats_first_class,
            economy_seat_cost=economy_seat_cost,
            business_seat_cost=business_seat_cost,
            first_class_cost=first_class_cost
        )

        db.add(new_flight)
        db.commit()
        db.refresh(new_flight)
        logging.info(f"Successfully added flight: {new_flight.flight_number}")
        
    return flights

def search_flights(criteria, db: Session):
    query = db.query(Flight)

    if criteria.origin:
        query = query.filter(Flight.origin == criteria.origin)
    if criteria.destination:
        query = query.filter(Flight.destination == criteria.destination)
        
    if criteria.start_date and criteria.end_date:
        query = query.filter(Flight.date.between(criteria.start_date, criteria.end_date))
        
    if criteria.start_date and criteria.end_date:
        query = query.filter(Flight.date.between(criteria.start_date, criteria.end_date))

    if criteria.flight_number:
        query = query.filter(Flight.flight_number == criteria.flight_number)

    if criteria.airline:
        query = query.filter(Flight.airline == criteria.airline)

    if criteria.start_time and criteria.end_time:
        query = query.filter(Flight.departure_time.between(criteria.start_time, criteria.end_time))

    if criteria.seat_type:
        min_cost = int(criteria.min_cost) if criteria.min_cost is not None else 0
        max_cost = int(criteria.max_cost) if criteria.max_cost is not None else float('inf')

        if criteria.seat_type == 'economy':
            query = query.filter(Flight.economy_seat_cost.between(min_cost, max_cost))
        elif criteria.seat_type == 'business':
            query = query.filter(Flight.business_seat_cost.between(min_cost, max_cost))
        elif criteria.seat_type == 'first_class':
            query = query.filter(Flight.first_class_cost.between(min_cost, max_cost))


    flights = query.all()
    # Convert SQLAlchemy models to Pydantic models
    flight_models = [FlightModel.from_orm(flight) for flight in flights]
    total_found = len(flight_models)
    
    if total_found == 0:
        total_found = "There were no flights found for the search criteria"
    
    return {"query_results": total_found, "flights": flight_models}

def book_flight(flight_id: int, seat_type: str, num_seats: int = 1, db: Session = Depends(get_db)):
    # Retrieve the flight from the database
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()

    if not flight:
        return "Flight not found."

    # Initialize the cost variable
    total_cost = 0

    # Check seat availability based on seat type and number of requested seats
    if seat_type == "economy" and flight.open_seats_economy >= num_seats:
        flight.open_seats_economy -= num_seats
        total_cost = flight.economy_seat_cost * num_seats
    elif seat_type == "business" and flight.open_seats_business >= num_seats:
        flight.open_seats_business -= num_seats
        total_cost = flight.business_seat_cost * num_seats
    elif seat_type == "first_class" and flight.open_seats_first_class >= num_seats:
        flight.open_seats_first_class -= num_seats
        total_cost = flight.first_class_cost * num_seats
    else:
        # If not enough seats are available, return a failure message
        return f"Not enough {seat_type} seats available."

    # Commit the booking to the database
    db.commit()
    
    success_message = f"Successfully booked {num_seats} {seat_type} seat(s) on {flight.airline} flight on {flight.date} from {flight.origin} to {flight.destination}. Total cost: ${total_cost}."

    # Return a success message
    return {"message": success_message, "flight_info": flight}

