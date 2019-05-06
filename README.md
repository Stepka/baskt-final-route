- _final_route.py_ is module for calculate routes based on destinations, time window, etc data. Use google OR tools for it. 

- _final_route_flask_server.py_ is Flask server based API for routing. Right now that application is run on _ec2_ in Ohio region, run inside *docker*.

- _final_route_local.py_ is wrapper around _final_route.py_ to run it local with hardcoded data
## Usage

Call http://ec2-18-223-44-74.us-east-2.compute.amazonaws.com/final_route with params encoded as *application/json*

##### _Params_

- **locations** - _Required._ Array of pairs of coordinates or addresses for possible destinations. 
But the first item, with index 0, is for warehouse, hub. 
If you pass coordinates, each pair should be array of two elements, f. e. `[39.2908045, -76.66135799999999]`. 
If you pass an address, each address should be an array with one element, f. e. `['232 n franklintown road baltimore md 21223']`.

- **order_ids** - _Required._ Array of strings with order ids. 
Values indexes should correspond to indexes from _locations_. 
Note, that 0 is for warehouse, hub, so you can pass any value for 0 index, f. e. empty string or `"depot"`.

- **time_windows** - _Required._ Array of pairs of time windows with format `["HH:MM PM", "HH:MM PM"]`. 
Values indexes should correspond to indexes from _locations_. 
If time window not specified, please, pass maximum day window for corresponding element, f. e. `["05:00 AM", "11:30 PM"]`. 
**Important!** Note, that 0 is for warehouse, hub. So for depot you should to specify start and end time of Gig or interval for work. F.e. if we need to split day to 3 parts where each part with 4 hours duration, you should create 3 API calls for each Gig time window, sort and distribute destinations among that 3 call and each call start with depot and depot time window for current Gig. F. e. the first call with depot time window  `["08:00 AM", "12:00 PM"]`, the second call with depot time window  `["12:00 PM", "04:00 PM"]`, and the last call with depot time window  `["04:00 PM", "08:00 PM"]`.

- **shops** - _Required._ Array of shop names. Use city or addresses with shop name to avoid searches for mistaken shops from other cities.

- **cold_deliveries** - Array of indexes from _locations_ for cold_deliveries. 
Note, that 0 is for warehouse, hub. Default is `[]` means no cold deliveries.

- **num_vehicles** - Number of available vehicles. Default is `20`.

- **with_print** - If `'true'` to each route in the result adds field `'route_string' `with full description of the route.

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
			- **address**: address of destination if it was passed, f. e. `"232 n franklintown road baltimore md 21223"`
			- **from_time**: the earliest time to arrive to destination, f. e. `"06:00 AM"`
			- **to_time**: the latest time to arrive to the destination, f.e. `"06:00 AM"`
			- **next_destination_duration**: road time to the next destination.
		- **route_duration**: total duration of the route in `HH:MM` format.

#### Examples
- **locations**: 

``` json
{
	"locations": [
		[39.2908045, -76.66135799999999],  # warehouse, hub
		[39.3019488, -76.60290979999999],
		[39.3021398, -76.61649560000001],
		[39.3054756, -76.6211893]
		[39.2815397, -76.6549007],
		[39.353636, -76.63003789999999],
		[39.3019488, -76.60290979999999],
		[39.2938149, -76.6156373]
	],
	"time_windows": [
		["06:00 AM", "11:00 PM"], # warehouse, hub
		["04:00 PM", "06:00 PM"],
		["03:00 PM", "04:00 PM"],
		["06:00 AM", "11:00 PM"],
		["06:00 AM", "11:00 PM"],
		["06:00 AM", "11:00 PM"],
		["09:00 AM", "10:00 PM"],
		["09:30 AM", "10:30 AM"]
	],
	"order_ids": [
		"depot load", # warehouse, hub
		"order 2",
		"order 3",
		"order 4",
		"order 5",
		"order 6",
		"order 7",
		"order 8"
	],
	"shops": [
		"Baltiore price rite",
		"Baltimore shoppers",
		"Baltimore safeway",
		"Baltimore wegmans",
		"Baltimore acme markets",
		"Baltimore walmart",
		"Baltimore 7-Eleven",
		"Baltimore Target",
		"Baltimore Save A Lot",
		"Baltimore Walmart Supercenter"
		],
	"cold_deliveries": [6, 7]
}
```
_or for addresses_
``` json
{
	"locations": [
		["232 n franklintown road baltimore md 21223"], # warehouse, hub
		["1000 E Eager St, Baltimore, MD 21202"],
		["1030 N Charles St #302, Baltimore, MD 21201"],
		["1111 Park Ave #109, Baltimore, MD 21201"],
		["2429 Frederick Ave, Baltimore, MD 21223"],
		["600 Wyndhurst Ave Suite 270, Baltimore, MD 21210"],
		["1000 E Eager St, Baltimore, MD 21202"],
		["338 N Charles St, Baltimore, MD 21201"]
	],
	"time_windows": [
		["06:00 AM", "11:00 PM"], # warehouse, hub
		["04:00 PM", "06:00 PM"],
		["03:00 PM", "04:00 PM"],
		["06:00 AM", "11:00 PM"],
		["06:00 AM", "11:00 PM"],
		["06:00 AM", "11:00 PM"],
		["09:00 AM", "10:00 PM"],
		["09:30 AM", "10:30 AM"]
	],
	"order_ids": [
		"depot load", # warehouse, hub
		"order 2",
		"order 3",
		"order 4",
		"order 5",
		"order 6",
		"order 7",
		"order 8"
	],
	"shops": [
		"Baltiore price rite",
		"Baltimore shoppers",
		"Baltimore safeway",
		"Baltimore wegmans",
		"Baltimore acme markets",
		"Baltimore walmart",
		"Baltimore 7-Eleven",
		"Baltimore Target",
		"Baltimore Save A Lot",
		"Baltimore Walmart Supercenter"
		],
	"cold_deliveries": [6, 7]
}

```

Result
``` json
{
	"successful": true, 
	"body": {
		"routes": [
			{
				"description": "Route for vehicle 0", 
				"destinations": [
					{
						"index": 0, 
						"type": "start", 
						"order_id": "depot", 
						"location": [39.2908045, -76.66135799999999], 
						"address": "232 n franklintown road baltimore md 21223", 
						"from_time": "06:00 AM", 
						"to_time": "06:00 AM", 
						"next_destination_duration": 19
					}, 
					{
						"index": 5, 
						"type": "delivery", 
						"order_id": "order 6", 
						"location": [39.353636, -76.63003789999999], 
						"address": "600 Wyndhurst Ave Suite 270, Baltimore, MD 21210", 
						"from_time": "06:19 AM", 
						"to_time": "06:19 AM",
						"next_destination_duration": 17
					}, 
					{
						"index": 3, 
						"type": "delivery", 
						"order_id": "order 4", 
						"location": [39.3054756, -76.6211893], 
						"address": "1111 Park Ave #109, Baltimore, MD 21201", 
						"from_time": "06:36 AM", 
						"to_time": "06:36 AM", 
						"next_destination_duration": 15
					}, 
					{
						"index": 0, 
						"order_id": "depot", 
						"location": [39.2908045, -76.66135799999999], 
						"address": "232 n franklintown road baltimore md 21223", 
						"from_time": "06:51 AM", 
						"to_time": "06:51 AM"
					}
				], 
				"route_duration": "0:51"
			}, 
			{
				"description": "Route for vehicle 1", 
				"destinations": [
					{
						"index": 0, 
						"type": "start", 
						"order_id": 
						"depot", "location": [39.2908045, -76.66135799999999], 
						"address": "232 n franklintown road baltimore md 21223", 
						"from_time": "06:00 AM", 
						"to_time": "06:00 AM", 
						"next_destination_duration": 8
					}, 
					{
						"index": 9, 
						"type": "pickup", 
						"order_id": "order 8", 
						"location": [39.2895163, -76.6196826], 
						"address": "300 W Baltimore St, Baltimore, MD 21201, USA", 
						"from_time": "09:00 AM", 
						"to_time": "10:00 AM", 
						"next_destination_duration": 2
					}, 
					{
						"index": 7, 
						"type": "delivery", 
						"order_id": "order 8", 
						"location": [39.2938149, -76.6156373], 
						"address": "338 N Charles St, Baltimore, MD 21201", 
						"from_time": "09:30 AM", 
						"to_time": "10:30 AM", 
						"next_destination_duration": 2
					}, 
					{
						"index": 2, 
						"type": "delivery", 
						"order_id": "order 3", 
						"location": [39.3021398, -76.61649560000001], 
						"address": "1030 N Charles St #302, Baltimore, MD 21201", 
						"from_time": "03:00 PM", 
						"to_time": "03:27 PM", 
						"next_destination_duration": 3
					}, 
					{
						"index": 8, 
						"type": "pickup", 
						"order_id": "order 7", 
						"location": [39.312422299999994, -76.61839559999999], 
						"address": "2008 Maryland Ave, Baltimore, MD 21218, USA", 
						"from_time": "03:03 PM", 
						"to_time": "03:30 PM", 
						"next_destination_duration": 5
					}, 
					{
						"index": 1, 
						"type": "delivery", 
						"order_id": "order 2", 
						"location": [39.3019488, -76.60290979999999], 
						"address": "1000 E Eager St, Baltimore, MD 21202", 
						"from_time": "04:00 PM",
						"to_time": "04:00 PM", 
						"next_destination_duration": 1
					}, 
					{
						"index": 6, 
						"type": "delivery", 
						"order_id": "order 7", 
						"location": [39.3019488, -76.60290979999999], 
						"address": "1000 E Eager St, Baltimore, MD 21202", 
						"from_time": "04:01 PM", 
						"to_time": "04:01 PM", 
						"next_destination_duration": 10
					}, 
					{
						"index": 4, 
						"type": "delivery", 
						"order_id": "order 5", 
						"location": [39.2815397, -76.6549007], 
						"address": "2429 Frederick Ave, Baltimore, MD 21223", 
						"from_time": "04:11 PM", 
						"to_time": "04:11 PM", 
						"next_destination_duration": 2
					}, 
					{
						"index": 0, 
						"order_id": "depot", 
						"location": [39.2908045, -76.66135799999999], 
						"address": "232 n franklintown road baltimore md 21223", 
						"from_time": "04:13 PM", 
						"to_time": "04:13 PM"
					}
				], 
				"route_duration": "10:13"
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