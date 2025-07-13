FROM python:3.13.5-slim

# Seting working directory inside of container
WORKDIR /app

#Copy project files to the container
COPY . .

# Installing requirements
RUN pip install --no-cache-dir -r requirements.txt

#Making script executable
RUN chmod +x start.sh

# Exposing port
EXPOSE 5000

#Run the app
CMD ["./start.sh"]