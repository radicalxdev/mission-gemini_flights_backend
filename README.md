# Gemini Flight Manager
![geminiflights-ezgif com-video-to-gif-converter](https://github.com/AnikethRai/mission-gemini_flights_backend_AR/assets/95706188/da17e9cf-9fbd-4661-b460-af3fc95720da)
## Overview

Gemini Flight Manager is a comprehensive backend system built using FastAPI, designed for managing and simulating flight-related operations. This system provides a robust platform for handling various aspects of flight management, including flight generation, search, and booking functionalities.

The project leverages FastAPI's efficient and easy-to-use framework to create a high-performance, scalable solution ideal for flight data management. It comes equipped with an SQLite database (`flights.db`) pre-populated with initial data, allowing for quick deployment and testing.

Key features of Gemini Flight Manager include:
- Advanced search capabilities to query flights based on criteria like origin, destination, and dates.
- Booking system that handles seat availability across different classes and calculates costs accordingly.

Designed with extensibility and scalability in mind, Gemini Flight Manager is well-suited for both educational purposes and as a foundation for more complex flight management applications.

**For the purposes of Gemini Function Calling, you will only need `search_flights` and `book_flight` functions.

## Installation

### Prerequisites
Before you begin, ensure you have the following installed on your system:
- Python 3.6 or higher [Download](https://www.python.org/downloads/)
- FastAPI [Reference](https://fastapi.tiangolo.com/reference/)
- Uvicorn, an ASGI server for FastAPI [Documentation](https://www.uvicorn.org/)

## Architecture
<img src = 'https://github.com/AnikethRai/mission-gemini_flights_backend_AR/assets/95706188/de24509b-f0e9-47b3-8fa0-49314c664681' width = 500>

## Table of Contents
- Task✨ Setting up Google Gemini
- Task Clone Premade FastAPI Server
- Task☁️ Google Cloud Developer Initialization
- Task📞 Function Calling with Tools
- Task📊 Streamlit Integration
- Task✈️ Build the Book_Flight Tool

## Task✨ Setting up Google Gemini
  - Create a Google Cloud account by signing into console.cloud.google.com
  - Create a Project 'Gemini-flights'
  - Add Card for billing * will not charge to activate account.
    ![image](https://github.com/AnikethRai/mission-gemini_flights_backend_AR/assets/95706188/c9bd7f75-46ba-4a36-a21d-a3059fd1b104)

## Task Clone Premade FastAPI Server
- Install WSL or Favourite CLI to the local machine on the editor.
      To install WSL use the following command.
   ```bash
         WSL --install
   ```
- **Clone the Repository**
    Start by cloning the repository to your local machine. Use the following command:
    fork this repo: [Repo](https://github.com/radicalxdev/mission-gemini_flights_backend.git)
  ```bash
       git clone https://github.com/your-username/your-repository.git
       cd your-repository
  ```
-  Set Up a Virtual Environment (Optional but recommended)

    It's a good practice to create a virtual environment for your Python projects. This keeps your project dependencies isolated. If you have `virtualenv` installed, create a new environment with:
    
    ```bash
    virtualenv venv
    source venv/bin/activate
    ```
- Install Dependencies
  Inside the virtual environment, install all necessary dependencies by running:
  ```bash
  pip install -r requirements.txt
  ```
- Starting the FastAPI Server

  - After the installation, you can start the FastAPI server using Uvicorn. Navigate to the project directory and run:

    ```bash
    uvicorn main:app
    ```
- Accessing the API
   - With the server running, you can access the API at `http://127.0.0.1:8000.`

   - For interactive API documentation, visit `http://127.0.0.1:8000/docs`, where you can test the API endpoints directly from your browser.
    
- **Test Endpoints**
      -  Try using origin: BOS, Destination: SFO, Date: 2024-01-18 for Searching flights.
    ![image](https://github.com/AnikethRai/mission-gemini_flights_backend_AR/assets/95706188/2b9f95c5-77de-4c18-937d-24f362b060e6)


##  Task☁️ Google Cloud Developer Initialization
  - Install the Google Cloud SDK: Follow the installation instructions for your operating system here.
  - Open a terminal or command prompt.
  - Run the following command to initialize the SDK:
        ```
            gcloud init
        ```
  - Sign in with your Google Account: Follow the prompts to sign in or create a new account.
  - Choose a Google Cloud project: Select an existing project or create a new one.
  - Set the default a: Choose a default compute region and zone.
  - Confirm your choices: Review your selections and confirm to complete the initialization.
  - Verify the configuration: Run the following command to verify your configuration: arduinoCopy code
    ``` gcloud config list ```
  (Optional) Install additional components: Depending on your needs, you may want to install additional components using the gcloud components install command.
  You're now ready to use Gcloud commands to interact with Google Cloud Platform services!
  ![task2](https://github.com/AnikethRai/Gemini_Explorer/assets/95706188/373d51c0-fa38-48b7-a827-ef44c158f45c)

## Task📞 Function Calling with Tools
- CD to services/ folder and create gemini tools file. But in this case, I used the pre-defined tools files, Sample.py
- Create FunctionDeclaration Object for Gemini and Bind.
  ```python
    #Syntax for function declaration
    get_search_flights = generative_models.FunctionDeclaration(
    name="get_search_flights",
    description="DESCRIPTION HERE",
    parameters={
        "type": "object",
        "properties": {
            // Define the properties of the parameters here
         }
       }
      )
    ```
- Create the Model with Config.
    ``` python
    # Model Syntax
    model = GenerativeModel(
    "gemini-pro",
    tools=[search_tool],
    generation_config=config
      )
    ```
## Task📊 Streamlit Integration
- Install Streamlit on Virtual Env
  - Here is the link on how to install. [Streamlit](https://docs.streamlit.io/)
- Streamlit Process:
  - Create Response Handler
  - Create LLM Response with handle_response
  - Initialize chat history
  - display chat messages from history
  - Accept user inputs
- After Initialization run the following command
  ```Python
  streamlit run filename.py | python -m streamlit run filename.py
  ```
![image](https://github.com/AnikethRai/mission-gemini_flights_backend_AR/assets/95706188/1b6fbf4b-e015-4677-bfc5-a9b4bcbfbe8d)

## Task✈️ Build the Book_Flight Tool
- Within Flight_Manager.py create a new book_flight function that sends a POST request to the prebuilt endpoint. Ensure it matches the requirements for the endpoint.
   ```python
   #Syntax
   def book_flight(flight_id, num_seats, seat_preference):
    # Code to send POST request to book a flight
    endpoint = "https://example.com/book_flight"
    payload = {
        "flight_id": flight_id,
        "num_seats": num_seats,
        "seat_preference": seat_preference
    }
    response = requests.post(endpoint, json=payload)
    return response.json()
   ```
- Create a new FunctionDeclaration for the Book Flight function
    ``` python
    #syntax
    book_flight_declaration = FunctionDeclaration(
    name="book_flight",
    description="DESCRIPTION HERE",
    parameters={
        "type": "object",
        "properties": {
            "flight_id": {"type": "integer"},
            "num_seats": {"type": "integer"},
            "seat_preference": {"type": "string"}
            # Add more parameters as needed
        }
    }
   )  
   ```

- Bind the tool to Gemini. Gemini should now be able to check flights and also book using the endpoint as an agent.
![image](https://github.com/AnikethRai/mission-gemini_flights_backend_AR/assets/95706188/944bf6fb-8797-44d8-a2d9-d678ea177447)

## Acknowledgements
I wanna express my gratitude towards RadicalX Community, especially Talha Sabri and Mikhail Ocampo for providing me the opportunity to learn and build Gemini flights.
 ![image](https://github.com/AnikethRai/Gemini_Explorer/assets/95706188/7fec3346-20fe-4566-8a32-4ca49de2ea83)

## Socials
- To join RadicalX follow this link. [RadicalX AI](https://www.community.radicalx.co/about](https://www.community.radicalx.co/share/VAN9ZwQaHlvm-ASn?utm_source=manual)https://www.community.radicalx.co/share/VAN9ZwQaHlvm-ASn?utm_source=manual)
- LinkedIn [Aniketh Rai](https://www.linkedin.com/in/aniketh-rai/)
