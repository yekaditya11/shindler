# Use the official Python image from Docker Hub
FROM python:3.13

# Set environment variables to ensure the Python output is not buffered
ENV PYTHONUNBUFFERED 1
ENV APP_HOST 0.0.0.0
ENV APP_PORT 8000

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . /app/

# Expose the port that your app will run on
EXPOSE $APP_PORT

# Install Uvicorn to serve the FastAPI app
RUN pip install uvicorn

# Command to run the server (FastAPI with Uvicorn)
CMD ["python", "app.py"]
