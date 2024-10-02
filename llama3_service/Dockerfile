# Start with the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /llama3_service

# Copy the requirements file
COPY ./requirements.txt /llama3_service/requirements.txt

# Install dependencies, including PyTorch
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install torch

# Copy the rest of the application code
COPY . /llama3_service/

# Command to run the application
CMD ["python", "llama3.py"]
