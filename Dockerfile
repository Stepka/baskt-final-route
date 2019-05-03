FROM ubuntu

# Update
RUN apt-get update
RUN apt-get install -y python 
RUN apt-get install -y python-pip
 
# Install app dependencies
RUN pip install --upgrade pip

# Install app dependencies
RUN pip install --upgrade Flask
RUN pip install --upgrade --user ortools
RUN pip install googlemaps

# Bundle app source
COPY final_route.py Final_route.py

EXPOSE  5000
CMD ["python", "final_route_flask_server.py", "-p 5000"]