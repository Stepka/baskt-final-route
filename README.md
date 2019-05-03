- _final_route.py_ is module for calculate routes based on destinations, time window, etc data. Use google OR tools for it. 

- _final_route_flask_server.py_ is Flask server based API for routing. Right now that application is run on _ec2_ in Ohio region, run inside *docker*.

- _final_route_local.py_ is wrapper around _final_route.py_ to run it local with hardcoded data
## Usage

Call http://ec2-18-223-44-74.us-east-2.compute.amazonaws.com/final_route with params to call API

##### _Params_
- **locations** - Array of pairs of coordinates for possible destinations.
- **time_windows** - Array of pairs of time windows with format ["HH:MM PM", "HH:MM PM"].
- **shops** - Array of shop names. Use city or addresses with shop name to avoid 
searches for mistaken shops from other cities.
- **destinations** - Array of indexes from _locations_ for destinations.
- **demands** - Array of indexes (looks like do not use by tool).
- **num_vehicles** - Number of available vehicles.

##### _Return_
Json with routes description

#### Examples
- **locations**: `[[39.29044, -76.61233], [39.34823, -76.73266], [39.32051, -76.72457], [39.35379, -76.7584]]`
- **time_windows**: `[["01:00 PM", "01:00 PM"], ["02:15 PM", "02:25 PM"], ["02:15 PM", "02:25 PM"], ["02:00 PM", "02:10 PM"]]`
- **shops**: `["Baltimore price rite", "Baltimore shoppers", "Baltimore safeway", "Baltimore wegmans", "Baltimore acme markets", "Baltimore walmart", "Baltimore 7-Eleven", "Baltimore Target", "Baltimore Save A Lot", "Baltimore Walmart Supercenter"]`
- **destinations**: `[2, 3]`
- **demands**: `[0, 1, 1, 2, 1, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8, 9]`
- **num_vehicles**: `4`

Result
``` json
{
    "result": [
        {
            "description": "Route for vehicle 0", 
            "route": " 0 ->  4 ->  5 ->  3 ->  1 ->  2 -> 0", 
            "total_duration": "1:16"
        }, 
        {
            "description": "Route for vehicle 1", 
            "route": " 0 -> 0", 
            "total_duration": "0:00"
        }, 
        {
            "description": "Route for vehicle 2", 
            "route": " 0 -> 0", 
            "total_duration": "0:00"
        }, 
        {
            "description": "Route for vehicle 3", 
            "route": " 0 -> 0", 
            "total_duration": "0:00"
        }
    ], 
    "success": "true", 
    "total_duration": "1:16"
}
```

For test purposes you can call 
http://ec2-18-223-44-74.us-east-2.compute.amazonaws.com/final_route/debug
for calculate routes on hardcoded data
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