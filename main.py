from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from services.flight_manager import generate_flights, search_flights, book_flight
import models

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
    
app = FastAPI()

@app.post("/generate-flight/")
def generate_flight(flight_input: models.FlightInput, num_flights: int, db: Session = Depends(models.get_db)):
    return generate_flights(flight_input, num_flights, db)

@app.post("/book_flight")
def book_flight_endpoint(flight_id: int, seat_type: str, num_seats: int = 1, db: Session = Depends(models.get_db)):
    try:
        result = book_flight(flight_id, seat_type, num_seats, db)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/flights/", response_model=List[models.FlightModel])
def read_all_flights(db: Session = Depends(models.get_db)):
    flights = db.query(models.Flight).all()
    return flights

@app.get("/search-flights/")
def search_flights_endpoint(criteria: models.FlightSearchCriteria = Depends(), db: Session = Depends(models.get_db)):
    return search_flights(criteria, db)
