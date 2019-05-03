- _final_route.py_ is module for calculate routes based on destinations, time window, etc data. Use google OR tools for it. 

- _final_route_flask_server.py_ is Flask server based API for routing. Right now that application is run on _ec2_ in Ohio region, run inside *docker*.

- _final_route_local.py_ is wrapper around _final_route.py_ to run it local with hardcoded data
## Usage

Call http://ec2-18-223-44-74.us-east-2.compute.amazonaws.com/final_route with params to call API

##### _Params_
- **locations** - _Required._ Array of pairs of coordinates or addresses for possible destinations. 
But the first item, with index 0, is for warehouse, hub. 
If you pass coordinates, each pair should be array of two elements, f. e. `[39.2908045, -76.66135799999999]`. 
If you pass an address, each address should be an array with one element, f. e. `['232 n franklintown road baltimore md 21223']`.
- **time_windows** - _Required._ Array of pairs of time windows with format `["HH:MM PM", "HH:MM PM"]`. 
Values indexes should correspond to indexes from _locations_. 
If time window not specified, please, pass maximum day window for corresponding element, f. e. `["05:00 AM", "11:30 PM"]`
- **shops** - _Required._ Array of shop names. Use city or addresses with shop name to avoid 
searches for mistaken shops from other cities.
- **cold_deliveries** - Array of indexes from _locations_ for cold_deliveries. 
Note, that 0 is for warehouse, hub. Default is `[]` means no cold deliveries.
- **num_vehicles** - Number of available vehicles. Default is `20`.

##### _Return_
Json with routes description

#### Examples
- **locations**: 

``` json
[
    [39.2908045, -76.66135799999999],  # warehouse, hub
    [39.3019488, -76.60290979999999],
    [39.3021398, -76.61649560000001],
    [39.3054756, -76.6211893]
]
```
_or for addresses_
``` json
[
    ['232 n franklintown road baltimore md 21223'],   # warehouse, hub
    ['1000 E Eager St, Baltimore, MD 21202'],
    ['1030 N Charles St #302, Baltimore, MD 21201'],
    ['1111 Park Ave #109, Baltimore, MD 21201']
]
```

- **time_windows**: 
``` json
[
    ["05:00 AM", "11:30 PM"], 
    ["02:15 PM", "02:25 PM"], 
    ["02:15 PM", "02:25 PM"], 
    ["02:00 PM", "02:10 PM"]
]
```
- **shops**: 
``` json
[
    "Baltimore price rite", 
    "Baltimore shoppers", 
    "Baltimore safeway", 
    "Baltimore wegmans", 
    "Baltimore acme markets", 
    "Baltimore walmart", 
    "Baltimore 7-Eleven",
    "Baltimore Target", 
    "Baltimore Save A Lot", 
    "Baltimore Walmart Supercenter"
]
```
- **cold_deliveries**: `[2, 3]`
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