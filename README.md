- _final_route.py_ is module for calculate routes based on destinations, time window, etc data. Use google OR tools for it. 

- _final_route_flask_server.py_ is Flask server based API for routing. Right now that application is run on _ec2_ in Ohio region, run inside *docker*.

- _final_route_local.py_ is wrapper around _final_route.py_ to run it local with hardcoded data
## Usage

Call http://ec2-18-223-44-74.us-east-2.compute.amazonaws.com/final_route with params encoded as *application/json*

##### _payload_

- **orders** - _Required._  array of order objects. Object consist of:
    - orderId - string with order id, f. e. `"0b137cb1-1"`.
    - latitude - coordinate of the destination, f. e.`39.3019488`.
    - longitude - coordinate of the destination, f. e. `-76.60290979999999`.
    - fromTime - upper bound for delivery in format`"HH:MM PM"`, f. e. `"04:00 PM"`.
    - toTime - lower bound for delivery in format`"HH:MM PM"`, f. e.  `"06:00 PM"`. 
    - isColdDelivery - `true` or `false`. 
    If `true` routing will adds pickup from shop destination within one hour delivery time from shop to target destination.
- **shops** - _Required._ Array of shop objects. 
Among passed shops routing algo will search the nearest pickup point for cold deliveries.
    - shopId - id, string, f. e. `"24ce6075-394d-4b78-845d-48b58736d934"`.
    - latitude - coordinate of the shop, f. e.`39.3019488`.
    - longitude - coordinate of the shop, f. e. `-76.60290979999999`.
- **hubs** - _Required._ Array of hub objects. From hubs routes will starts. If number of vehicles is less
 than number of hubs it will be increased to number of hubs.
    - latitude - coordinate of the hub, f. e.`39.3019488`.
    - longitude - coordinate of the hub, f. e. `-76.60290979999999`.
    - fromTime - upper bound of hub working time in format`"HH:MM PM"`, f. e. `"04:00 PM"`.
    - toTime - lower bound hub working time in format`"HH:MM PM"`, f. e.  `"06:00 PM"`. 
- **num_vehicles** - Number of available vehicles. Default is `20`.
- **with_print** - If `true` to each route in the result adds field `'route_string' `with full description of the route.

      
**Important!** For Hub you should to specify start and end time of Gig or interval for work. 
F.e. if we need to split day to 3 parts where each part with 4 hours duration, 
you should create 3 API calls for each Gig time window, sort and distribute 
destinations among that 3 call and each call start with depot and depot time 
window for current Gig. 
F. e. the first call with depot time window  `["08:00 AM", "12:00 PM"]`, 
the second call with depot time window  `["12:00 PM", "04:00 PM"]`, 
and the last call with depot time window  `["04:00 PM", "08:00 PM"]`.

Note, if time window not specified, please, pass maximum Gig time window for corresponding element, 
f. e. `"09:00 AM", "10:00 PM"`.

##### _Return_
Json with routes description
- **successful**: if true all is ok.
- **body**: result.
	- **routes**: an array with routes.
		- **description**: simple description of the route.
		- **destinations**: an array of destinations.
			- **index**: index of the destination from *locations* array.
			- **type**: "`start`" for start from depot, "`pickup`" for picking up cold delivery from shop, "`delivery`" for delivery as target for destination.
			- **order_id**: string with order id.
			- **location**: array with lat long for destination, f. e. `[39.2908045, -76.66135799999999]`.
			- **from_time**: the earliest time to arrive to destination, f. e. `"06:00 AM"`. 
			If driver will arrive to destination earlier than _from_time_ he should wait. 
			- **to_time**: the latest time to arrive to the destination, f.e. `"06:00 AM"`. 
			If driver will arrive to destination later than _to_time_ route will be break.
			- **time_window**: target time window (_from_time_ and _to_time_ should be inside this), f.e. `["09:30 AM", "10:30 AM"]`. 
			It is just for information.
			- **delivery_time**: time from start (from Hub) to destination, in `HH:MM` format. 
			Note, that you should add time between when order was placed and start time 
			from hub to control total delivery time. I. e. total time = (time from order was placed to driver's start from hub) + returned from API time.
			- **next_destination_duration**: road time to the next destination in `HH:MM` format.
		- **route_duration**: total duration of the route in `HH:MM` format.

#### Examples
- **payload**: 

``` json
{
    "orders":[
        {
            "orderId":"0b137cb1-1",
            "latitude":39.3019488,
            "longitude":-76.60290979999999,
            "fromTime":"04:00 PM",
            "toTime":"06:00 PM",
            "isColdDelivery":false
        },
        {
            "orderId":"0b137cb1-2",
            "latitude":39.3021398,
            "longitude":-76.61649560000001,
            "fromTime":"03:00 PM",
            "toTime":"04:00 PM",
            "isColdDelivery":false
        },
        {
            "orderId":"0b137cb1-3",
            "latitude":39.3054756,
            "longitude":-76.6211893,
            "fromTime":"09:00 AM",
            "toTime":"10:00 PM",
            "isColdDelivery":false
        },
        {
            "orderId":"0b137cb1-4",
            "latitude":39.2815397,
            "longitude":-76.6549007,
            "fromTime":"09:00 AM",
            "toTime":"10:00 PM",
            "isColdDelivery":false
        },
        {
            "orderId":"0b137cb1-5",
            "latitude":39.353636,
            "longitude":-76.63003789999999,
            "fromTime":"09:00 AM",
            "toTime":"10:00 PM",
            "isColdDelivery":false
        },
        {
            "orderId":"0b137cb1-6",
            "latitude":39.3019488,
            "longitude":-76.60290979999999,
            "fromTime":"09:00 AM",
            "toTime":"10:00 PM",
            "isColdDelivery":true
        },
        {
            "orderId":"0b137cb1-7",
            "latitude":39.2938149,
            "longitude":-76.6156373,
            "fromTime":"09:30 AM",
            "toTime":"10:30 AM",
            "isColdDelivery":true
        }
    ],
    "shops":[
        {
            "shopId":"24ce6075-394d-4b78-845d-48b58736d934",
            "latitude":39.3054756,
            "longitude":-76.6211893
        }
    ],
    "hubs":[
        {
            "latitude":39.2908045,
            "longitude":-76.66135799999999,
            "fromTime":"09:00 AM",
            "toTime":"10:00 PM"
        }
    ],
    "with_print":false,
    "num_vehicles":4
}

```

- **result**: 
``` json
{
    "successful":true,
    "body":{
        "routes":[
            {
                "description":"Route for vehicle 0",
                "destinations":[
                    {
                        "index":0,
                        "type":"start",
                        "order_id":"",
                        "location":[
                            39.2908045,
                            -76.66135799999999
                        ],
                        "address":"",
                        "from_time":"09:00 AM",
                        "to_time":"09:00 AM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ],
                        "next_destination_duration":"0:25"
                    },
                    {
                        "index":5,
                        "type":"delivery",
                        "order_id":"0b137cb1-5",
                        "location":[
                            39.353636,
                            -76.63003789999999
                        ],
                        "address":"",
                        "from_time":"09:25 AM",
                        "to_time":"09:25 AM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ],
                        "delivery_time":"0:25",
                        "next_destination_duration":"0:08"
                    },
                    {
                        "index":3,
                        "type":"delivery",
                        "order_id":"0b137cb1-3",
                        "location":[
                            39.3054756,
                            -76.6211893
                        ],
                        "address":"",
                        "from_time":"09:33 AM",
                        "to_time":"09:33 AM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ],
                        "delivery_time":"0:33",
                        "next_destination_duration":"0:07"
                    },
                    {
                        "index":0,
                        "order_id":"",
                        "location":[
                            39.2908045,
                            -76.66135799999999
                        ],
                        "address":"",
                        "from_time":"09:40 AM",
                        "to_time":"09:40 AM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ]
                    }
                ],
                "route_duration":"0:40"
            },
            {
                "description":"Route for vehicle 1",
                "destinations":[
                    {
                        "index":0,
                        "type":"start",
                        "order_id":"",
                        "location":[
                            39.2908045,
                            -76.66135799999999
                        ],
                        "address":"",
                        "from_time":"09:00 AM",
                        "to_time":"09:00 AM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ],
                        "next_destination_duration":"0:04"
                    },
                    {
                        "index":4,
                        "type":"delivery",
                        "order_id":"0b137cb1-4",
                        "location":[
                            39.2815397,
                            -76.6549007
                        ],
                        "address":"",
                        "from_time":"09:04 AM",
                        "to_time":"09:21 AM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ],
                        "delivery_time":"0:04",
                        "next_destination_duration":"0:08"
                    },
                    {
                        "index":8,
                        "type":"pickup",
                        "order_id":"0b137cb1-6",
                        "location":[
                            39.3054756,
                            -76.6211893
                        ],
                        "address":"Sutton Place, 1111 Park Ave, Baltimore, MD 21201, USA",
                        "from_time":"09:12 AM",
                        "to_time":"09:29 AM",
                        "time_window":[
                            "09:00 AM",
                            "09:00 PM"
                        ],
                        "delivery_time":"0:12",
                        "next_destination_duration":"0:01"
                    },
                    {
                        "index":9,
                        "type":"pickup",
                        "order_id":"0b137cb1-7",
                        "location":[
                            39.3054756,
                            -76.6211893
                        ],
                        "address":"Sutton Place, 1111 Park Ave, Baltimore, MD 21201, USA",
                        "from_time":"09:13 AM",
                        "to_time":"09:30 AM",
                        "time_window":[
                            "09:00 AM",
                            "09:30 AM"
                        ],
                        "delivery_time":"0:13",
                        "next_destination_duration":"0:03"
                    },
                    {
                        "index":7,
                        "type":"delivery",
                        "order_id":"0b137cb1-7",
                        "location":[
                            39.2938149,
                            -76.6156373
                        ],
                        "address":"",
                        "from_time":"09:30 AM",
                        "to_time":"10:30 AM",
                        "time_window":[
                            "09:30 AM",
                            "10:30 AM"
                        ],
                        "delivery_time":"0:30",
                        "next_destination_duration":"0:02"
                    },
                    {
                        "index":2,
                        "type":"delivery",
                        "order_id":"0b137cb1-2",
                        "location":[
                            39.3021398,
                            -76.61649560000001
                        ],
                        "address":"",
                        "from_time":"03:00 PM",
                        "to_time":"03:57 PM",
                        "time_window":[
                            "03:00 PM",
                            "04:00 PM"
                        ],
                        "delivery_time":"6:00",
                        "next_destination_duration":"0:03"
                    },
                    {
                        "index":1,
                        "type":"delivery",
                        "order_id":"0b137cb1-1",
                        "location":[
                            39.3019488,
                            -76.60290979999999
                        ],
                        "address":"",
                        "from_time":"04:00 PM",
                        "to_time":"04:00 PM",
                        "time_window":[
                            "04:00 PM",
                            "06:00 PM"
                        ],
                        "delivery_time":"7:00",
                        "next_destination_duration":"0:01"
                    },
                    {
                        "index":6,
                        "type":"delivery",
                        "order_id":"0b137cb1-6",
                        "location":[
                            39.3019488,
                            -76.60290979999999
                        ],
                        "address":"",
                        "from_time":"04:01 PM",
                        "to_time":"04:01 PM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ],
                        "delivery_time":"7:01",
                        "next_destination_duration":"0:08"
                    },
                    {
                        "index":0,
                        "order_id":"",
                        "location":[
                            39.2908045,
                            -76.66135799999999
                        ],
                        "address":"",
                        "from_time":"04:09 PM",
                        "to_time":"04:09 PM",
                        "time_window":[
                            "09:00 AM",
                            "10:00 PM"
                        ]
                    }
                ],
                "route_duration":"7:09"
            }
        ]
    }
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