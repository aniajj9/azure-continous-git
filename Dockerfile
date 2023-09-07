# Use the official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the Python file into the container
COPY helpfulErrors.py .

# Expose the necessary port
EXPOSE 80

# Set the command to run your Python server
CMD ["python", "helpfulErrors.py"]
