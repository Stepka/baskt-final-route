FROM ubuntu:18.10

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx

WORKDIR /flask-server

COPY requirements.txt requirements.txt

# Install app dependencies
RUN pip3 install -r requirements.txt

# Bundle app source
COPY . .

EXPOSE  5005
CMD ["python3", "final_route_flask_server.py", "-p 5005"]