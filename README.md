Final_route.py is modified to be a Flask application. Right now that application is run on ec2 in Ohio region, marked as "Final_route.py", run inside *docker*.

## Usage

Call http://ec2-18-223-44-74.us-east-2.compute.amazonaws.com/final_route ro call API function *final_route()*  that runs *main()* function from *Final_route.py*

Here is code from *Final_route.py*

```python
@app.route("/final_route")
def final_route():
    return main()
```

You can add new API functions by writing new fucntion with leading 
`@app.route("/your_api_function_name")`

Also you can parse parameters from api call by following code:

```python
from flask import request

@app.route("/your_api_function_name")
def your_api_function_name():
    param_1 = request.args.get('param_1')
    param_2 = request.args.get('param_2')
```
and pass extracted arguments to f.e.* main()* function

## Rerun server

After you have updated code you need to load new code to ec2 instance and rebuild and rerun docker.  

##### *Case 1*

Run shell script *rebuild_docker.sh* that remove old container and image and build and run new:
`sh rebuild_docker.sh`

##### *Case 2*

Or you can do the same as in *Case 1* section manually step by step.

###### Delete All Running and Stopped Containers
`docker stop $(docker ps -a -q)`
`docker rm $(docker ps -a -q)`


###### Remove all images
`docker rmi $(docker images -a -q)`


###### Build new docker image
`docker build -t final_route .`

Note, that docker use Dockerfile from current directory (added to sources)

###### Run new docker container with flask app
`docker run -d -p 80:5000 final_route`

And updated application will run on the previous wrote url.