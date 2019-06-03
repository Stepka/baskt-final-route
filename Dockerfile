FROM ubuntu

# Update
RUN apt-get update
RUN apt-get install -y python 
RUN apt-get install -y python-pip
 
# Install app dependencies
RUN pip install --upgrade pip

# Install app dependencies
RUN pip install -r requirements.txt

# Bundle app source
COPY final_route.py final_route.py
COPY final_route_flask_server.py final_route_flask_server.py
COPY hardcoded_routes_data.py hardcoded_routes_data.py

EXPOSE  5000
CMD ["python", "final_route_flask_server.py", "-p 5000"]