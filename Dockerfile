FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Build arguments
ARG MONGO_URI
ARG TWILIO_ACCOUNT_SID
ARG TWILIO_AUTH_TOKEN
ARG TWILIO_MESSAGING_SERVICE_SID
ARG BASE_URL
ARG MONGO_DATABASE
ARG GCP_BUCKET_CREDENTIALS
ARG TICKET_BUCKET_NAME

# Set environment variables
ENV MONGO_URI=${MONGO_URI}
ENV TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
ENV TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
ENV TWILIO_MESSAGING_SERVICE_SID=${TWILIO_MESSAGING_SERVICE_SID}
ENV BASE_URL=${BASE_URL}
ENV MONGO_DATABASE=${MONGO_DATABASE}
ENV GCP_BUCKET_CREDENTIALS=${GCP_BUCKET_CREDENTIALS}
ENV TICKET_BUCKET_NAME=${TICKET_BUCKET_NAME}

COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application to the container
COPY . .

# Copy the GCP bucket credentials file
COPY ../gcp_bucket_credentials.json /app/

# Expose the port the application runs on
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


