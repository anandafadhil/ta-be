# Use the official Python image from the Docker Hub
FROM python:3.10

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


ENV MYSQLCLIENT_CFLAGS="$(mysql_config --cflags)"
ENV MYSQLCLIENT_LDFLAGS="$(mysql_config --libs)"
# Copy project
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "ta_be.wsgi:application", "--bind", "0.0.0.0:8000"]