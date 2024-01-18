import random
import requests
from datetime import datetime, timedelta, time, date
from typing import Optional
from fastapi import Depends
from sqlalchemy import and_
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

def calculate_times(origin, destination, flight_date):
    # Randomly generate departure time between 0 and 23 hours
    departure_hour = random.randint(0, 23)
    departure_minute = random.randint(0, 59)
    # Use flight_date instead of datetime.now()
    departure_time = datetime.combine(flight_date, datetime.min.time()).replace(hour=departure_hour, minute=departure_minute)

    # Random duration for the flight between 30 mins to 10 hours
    duration = timedelta(minutes=random.randint(30, 600))
    arrival_time = departure_time + duration

    return departure_time, arrival_time

def generate_flights(flight_input, num_flights, db: Session):
    flights = []
    
    for _ in range(num_flights):
        flight_number = generate_flight_number()
        airline = choose_airline()
        departure_time, arrival_time = calculate_times(flight_input.origin, flight_input.destination, flight_input.date)
        
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

def handle_flight_search(criteria, db: Session, page: Optional[int] = 1, page_size: Optional[int] = 10):
    """
    Searches for flights based on various criteria and implements pagination.

    This function searches the database for flights matching specified criteria. It supports filtering by various parameters, including mandatory ones like origin, destination, and date range, and optional ones like flight number, airline, departure time range, seat type, and cost range. Pagination is used to manage large datasets, returning a controlled subset of results based on the specified page number and page size.

    If the requested page number exceeds the total number of available pages, or if no flights match the criteria, appropriate messages are returned.

    Parameters:
    - criteria (FlightSearchCriteria): An object containing fields to filter the flights. This includes:
        - origin (str): The starting airport/location of the flight.
        - destination (str): The destination airport/location of the flight.
        - start_date (date): The earliest departure date for the flight.
        - end_date (date): The latest departure date for the flight.
        - flight_number (Optional[str]): Specific flight number to search for (default is None).
        - airline (Optional[str]): Specific airline to search for (default is None).
        - start_time (Optional[time]): The earliest departure time range (default is None).
        - end_time (Optional[time]): The latest departure time range (default is None).
        - seat_type (Optional[str]): Type of seat, e.g., 'economy', 'business', 'first_class' (default is None).
        - min_cost (Optional[int]): Minimum cost of the flight ticket (default is None).
        - max_cost (Optional[int]): Maximum cost of the flight ticket (default is None).
    - db (Session): SQLAlchemy database session for executing queries. Required for database access.
    - page (Optional[int]): The current page number for pagination. Defaults to 1 if not specified.
    - page_size (Optional[int]): The number of records to return per page. Defaults to 10 if not specified.

    Returns:
    A dictionary containing:
    - 'query_results': Number of flights found for the current page, or '0' if no flights match or the page number exceeds total pages.
    - 'flights': List of flights (as Pydantic models) that match the criteria for the current page. An empty list is returned if no flights are found or if the page number is out of range.
    - 'page': Current page number.
    - 'total_pages': Total number of pages available, based on the total count of records matching the search criteria.
    - 'message': Optional field providing additional information in cases where no flights are found or the requested page is out of range.

    """
    
    query = db.query(Flight)
    
    # Convert the start and end dates to datetime objects
    start_datetime = datetime.combine(criteria.start_date, time.min)
    end_datetime = datetime.combine(criteria.end_date, time.max)

    # Apply a filter using departure_time field
    query = query.filter(
        Flight.departure_time >= start_datetime,
        Flight.departure_time <= end_datetime,
        Flight.origin == criteria.origin,
        Flight.destination == criteria.destination
    )

    # Flight Extra Filters
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

        # Calculate the total count of matching records

        # Calculate the total count of matching records
    total_count = query.count()

    # If no flights are found, return immediately
    if total_count == 0:
        return {
            "message": "There were no flights found for the search criteria.",
            "flights": [],
            "page": page,
            "total_pages": 0
        }

    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size

    # Check if the requested page exceeds the total number of pages
    if page > total_pages:
        return {
            "message": "The requested page exceeds the total number of available pages.",
            "flights": [],
            "page": page,
            "total_pages": total_pages
        }

    # Apply pagination
    offset = (page - 1) * page_size
    flights = query.offset(offset).limit(page_size).all()

    # Convert SQLAlchemy models to Pydantic models
    flight_models = [FlightModel.from_orm(flight) for flight in flights]

    # Return the query results
    return {
        "query_results": len(flight_models),
        "flights": flight_models,
        "page": page,
        "total_pages": total_pages
    }

def handle_flight_book(flight_id: int, seat_type: str, num_seats: int = 1, db: Session = Depends(get_db)):
    """
    Books a specified number of seats on a flight.

    This function books seats on a flight identified by its flight_id. It handles seat 
    booking for different classes (economy, business, first class) and calculates the total cost based 
    on the number of seats and the seat type. It updates the flight's seat availability and commits the 
    changes to the database.

    Parameters:
    - flight_id (int): The unique identifier of the flight to book.
    - seat_type (str): The class of the seat to book (economy, business, or first_class).
    - num_seats (int, optional): The number of seats to book (default is 1).
    - db (Session, default Depends(get_db)): SQLAlchemy database session for executing queries.

    Returns:
    - On successful booking: A dictionary containing a success message and flight information.
    - On failure (flight not found or not enough seats): A failure message as a string.

    The function checks seat availability before booking. If the requested number of seats is 
    not available in the specified class, it returns an error message. If the flight is not found, 
    it returns a 'Flight not found.' message.
    """
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

def search_flights(origin: str, destination: str, start_date: date, end_date: date):
    """
    Sends a GET request to a FastAPI endpoint to search for flights.

    Parameters:
    - origin (str): The starting airport/location of the flight.
    - destination (str): The destination airport/location of the flight.
    - start_date (date): The departure date for the flight.
    - end_date (date): The return date for the flight.

    Returns:
    The response from the FastAPI endpoint as a JSON object.
    """
    # Constructing the URL with query parameters
    url = f"http://127.0.0.1:8000/search-flights/?origin={origin}&destination={destination}&start_date={start_date}&end_date={end_date}&page=1&page_size=10"

    # Making the GET request
    response = requests.get(url, headers={'accept': 'application/json'})

    # Returning the JSON response
    return response.json()
