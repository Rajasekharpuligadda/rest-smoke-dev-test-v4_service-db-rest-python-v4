# Microservice stub.

## Setup & Installation

1.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**:
    Copy the template and fill in your values.
    ```bash
    cp .env.template .env
    ```

## Running the Service

### Local Development

To run the Flask development server:
```bash
export FLASK_APP=run.py
flask run
```

To run with Docker:
```bash
docker build -t your-service-name .
docker run -d -p 5000:5000 --name your-service-container --env-file .env your-service-name
```

## Processing the dependencies

dependencies_processor folder contains logic of generating requirements.txt file, from the provided dependencies-config.yml file.
