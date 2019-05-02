from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
import googlemaps
from random import randint
from flask import Flask
import sys
import optparse
from datetime import timedelta

app = Flask(__name__)

CURRENT_CITY = 'Baltimore'


# Helper class to convert a DynamoDB item to JSON.
class ResultCode:
    def __init__(self, is_successful, body=None):
        self.is_successful = is_successful
        self.body = body


@app.route("/")
def check_if_running():
    print("All is ok, server is running!")
    return "All is ok, server is running!"


# here is API methon for get some result with this script
@app.route("/final_route")
def final_route():
    return main()


# enter the time windows of all the clients here with the first one as the base time for all
def time_arr():
    time = [
        ("01:00 PM", "01:00 PM"),   # departure time
        ("02:15 PM", "02:25 PM"),
        ("02:15 PM", "02:25 PM"),
        ("02:00 PM", "02:10 PM"),
        ("01:45 PM", "01:55 PM"),
        ("01:00 PM", "01:08 PM"),
        # ("01:50 PM", "02:00 PM"),
        # ("01:00 PM", "01:10 PM"),
        # ("01:10 PM", "01:20 PM"),
        # ("01:00 PM", "01:10 PM"),
        # ("02:15 PM", "02:50 PM"),
        # ("02:25 PM", "03:30 PM"),
        # ("01:05 PM", "03:15 PM"),
        # ("01:15 PM", "03:25 PM"),
        # ("01:10 PM", "03:20 PM"),
        # ("01:45 PM", "03:55 PM"),
        # ("01:30 PM", "03:20 PM"),
        # ("01:00 PM", "04:20 PM")
    ]

    # time = [
    #     ("00:00 PM", "10:00 PM"),   # departure time
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ("00:00 PM", "10:00 PM"),
    #     ]

    time = conv_time(time)

    print(time)

    return time


def data_arr():
    # Array of locations (lat, lng)
    locations = [(39.290440, -76.612330),   # depot
                 (39.348230, -76.732660),
                 (39.320510, -76.724570),
                 (39.353790, -76.758400),
                 (39.348230, -76.732660),
                 (39.658420, -77.175440),
                 # (39.587240, -76.993040),
                 # (39.383070, -76.763020),
                 # (39.290440, -76.612330),
                 # (39.391320, -76.733710),
                 # (39.321000, -76.516160),
                 # (39.589700, -76.995910),
                 # (39.153780, -76.610510),
                 # (39.245270, -76.661030),
                 # (39.254990, -76.657526),
                 # (39.261411, -76.6968749),
                 # (39.284484, -76.7144821),
                 # (39.290409, -76.7495943)
                 ]

    return locations


# function for pickup and delivery
# dest_arr is the index of locations in the locations array that need cold items delivered
# max_delivery_seconds is the max time between picking up the cold item and delivering it to a customer
def pickup_deliver(gclient,
                   locations,
                   time_windows):
    
    shops_arr = [
        CURRENT_CITY + " price rite",
        CURRENT_CITY + " shoppers",
        CURRENT_CITY + " safeway",
        CURRENT_CITY + " wegmans",
        CURRENT_CITY + " acme markets",
        CURRENT_CITY + " walmart",
        CURRENT_CITY + " 7-Eleven",
        CURRENT_CITY + " Target",
        CURRENT_CITY + " Save A Lot",
        CURRENT_CITY + " Walmart Supercenter"
    ]
    # dest_arr = [2, 3, 6, 7, 8, 4]
    dest_arr = [2, 3, 4, 5]
    max_delivery_minutes = 60
    
    loc_length = len(locations)
    result = one_hour(gclient, locations, time_windows, shops_arr, dest_arr, max_delivery_minutes)
    if not result.is_successful:
        return result

    pickup_deliver = []
    for i in range(len(dest_arr)):
        pickup_deliver.append([loc_length+i, dest_arr[i]])
    return ResultCode(True, pickup_deliver)


# index of locations in the locations array to deliver items ,
# basically u can deliver to the same location twice if u would like to
def demands_arr():
    # location index to go to
    demands = [0, 1, 1, 2, 1, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8, 9]
    return demands


# initialize all the variables
def create_data_model():
    gclient = googlemaps.Client(key='AIzaSyAei-_KeQOTzjN_6sIPuQ3yW4MlRk0MtXk')
    
    data = {}
    data['locations'] = data_arr()
    data["time_windows"] = time_arr()
    print("pickup_deliver starts...")
    result = pickup_deliver(gclient, data['locations'], data['time_windows'])

    if not result.is_successful:
        return result
    data['pickups_deliveries'] = result.body
    print("pickup_deliver ends")

    print("distance_matrix starts...", len(data['locations']))
    result = func_dist_mat(data['locations'], gclient)
    if not result.is_successful:
        return result
    data['distance_matrix'] = result.body
    print("distance_matrix ends")
    
    data["time_per_demand_unit"] = 1
    data["vehicle_speed"] = func_speed_mat(data['locations'], gclient)    
    data["time_matrix"] = func_time_matrix(data)
    
    data["demands"] = demands_arr()
    
    data['num_vehicles'] = 4
    data['depot'] = 0
    print("data ready")

    return ResultCode(True, data)


# ******************************************************************************************
# ************************   time_arr functions *******************************************
# ****************************************************************************************
def conv_time(time_arr):
    base_time_0 = convert_to_24(time_arr[0][0])
    base_time_1 = convert_to_24(time_arr[0][1])
    time_list = []
    for i in range(len(time_arr)-1):
        a = abs(base_time_0 - convert_to_24(time_arr[i][0]))
        b = abs(base_time_0 - convert_to_24(time_arr[i][1]))
        time_list.append((a, b))
    return time_list


def convert_to_24(datestr): 
    if datestr[-2:] == "AM" and datestr[:2] == "12": 
        return int(datestr[3:6])
          
    # remove the AM     
    elif datestr[-2:] == "AM": 
        return int(datestr[:2])*60 + int(datestr[3:6])
        
    elif datestr[-2:] == "PM" and datestr[:2] == "12": 
        return int(datestr[:2])*60 + int(datestr[3:6])
          
    else:        
        # add 12 to hours and remove PM 
        return (int(datestr[:2]) + 12)*60 + int(datestr[3:6])


# ***************************************************************************************
# **************************************************************************************
# **************************      time matrix functions ************************************
# ************************************************************************************
def time_callback(from_index, to_index):
    """Returns the manhattan distance travel time between the two nodes."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data["time_matrix"][from_node][to_node]


def func_time_callback(data):
    def service_time(node):
        # Returns the service time for the specified location.
        return data["time_per_demand_unit"]

    def travel_time(from_node, to_node):
        # Returns the travel times between two locations.
        # meters / (meters / minute)
        travel_time = data["distance_matrix"][from_node][to_node] / (data["vehicle_speed"][from_node][to_node])
        return travel_time

    def time_callback(from_node, to_node):
        # Returns the total time between the two nodes.
        serv_time = service_time(from_node)
        trav_time = travel_time(from_node, to_node)
        return serv_time + trav_time

    return time_callback


def func_time_matrix(data):
    time_callback = func_time_callback(data)
    time = data["distance_matrix"]
    size = len(data["distance_matrix"])
    time_mat = [0] * size
    for from_node in range(size):
        time_mat[from_node] = [0] * size
        for to_node in range(size):
            x = time[from_node]
            y = time[to_node]
            time_mat[from_node][to_node] = int(time_callback(from_node, to_node))
    return time_mat


# **************************************************************************************
# **************************************************************************************
# ******************       dist matrix functions ***************************************
# *************************************************************************************
def func_dist_mat(loc, gclient):
    # Create the distance between locations matrix array.
    size = len(loc)
    dist_mat = [0] * size
    for from_node in range(size):
        dist_mat[from_node] = [0] * size
        for to_node in range(size):
            print("calculate distance...", from_node, to_node)
            x1 = loc[from_node][0]
            y1 = loc[from_node][1]
            x2 = loc[to_node][0]
            y2 = loc[to_node][1]

            result = gmaps_dist(gclient, x1, y1, x2, y2)
            if not result.is_successful:
                return result
            dist_mat[from_node][to_node] = result.body

    return ResultCode(True, dist_mat)


def gmaps_dist(gclient, x1, y1,
                        x2, y2):
    # Gmaps distance between points
    origin = [(x1, y1)]
    dest = [(x2, y2)]

    depart_time = "now"

    dist1 = gclient.distance_matrix(origin, dest, departure_time=depart_time,
                                    mode='driving', traffic_model="best_guess")
    dist2 = gclient.distance_matrix(origin, dest, departure_time=depart_time,
                                    mode='driving', traffic_model="pessimistic")

    if dist2['rows'][0]['elements'][0]['status'] != 'OK':
        returned_message = "couldn't get distance between {} and {} " \
                       "must be a server issue or a problem " \
                       "with the geocodes of origin or destination".format(origin, dest)
        print(returned_message)
        print("the output is ", dist2)
        # exit()
        return ResultCode(False, returned_message)

    if dist1['rows'][0]['elements'][0]['status'] != 'OK':
        returned_message = "couldn't get distance between {} and {} must be a server " \
                           "issue or a problem with the geocodes of origin or destination".format(origin, dest)
        print(returned_message)
        print("the output is ", dist1)
        # exit()
        return ResultCode(False, returned_message)

    dist2 = dist2['rows'][0]['elements'][0]['distance']['value']
    dist1 = dist1['rows'][0]['elements'][0]['distance']['value']

    return ResultCode(True, int(max(dist1, dist2)))


# ***************************************************************************************
# **************************************************************************************
# ******************      pickup_deliver  functions ***********************************
# ************************************************************************************
def one_hour_dist(gclient,
                  shop,
                  dest):
    dist = gclient.distance_matrix(shop, dest, mode='driving')

    if dist['rows'][0]['elements'][0]['status'] != 'OK':

        returned_message = "couldn't get distance between {} and {} " \
                           "must be a server issue or a problem with the " \
                           "geocodes of origin or destination".format(shop, dest)
        print(returned_message)
        print("the output is ", dist)
        # exit()
        result = ResultCode(False, returned_message)
        return result
    else:
        #           estimated distance between them                  ,  shop's address         ,         estimated time between them.
        result_body = dist['rows'][0]['elements'][0]['distance']['value'], \
                      dist['origin_addresses'][0], \
                      int(dist['rows'][0]['elements'][0]['duration']['value'] / 60)
        return ResultCode(True, result_body)


def one_hour(gclient,
             locations,
             time_windows,
             shops_arr,
             dest_arr,
             max_delivery_minutes):
  
    # calculate the closest shop to index i
    # append the shop's coords to array of distances
    # increase number of locations by 1
    least_dist = 10000000000
    for i in dest_arr:
        dest = locations[i]
        # print("check destination: {}".format(dest))
        for shop in shops_arr:
            result = one_hour_dist(gclient, shop, dest)
            if not result.is_successful:
                return result
            dist, address, dur = result.body
            # print("  check shop: {}\n    distance: {},\n    address: {},\n    duration: {}".format(shop, dist, address, dur))
            if least_dist > dist:
                least_dist = dist
                closest = address
                duration = dur

        print('closets is {}, distance: {}, duration: {}'.format(closest, least_dist, duration))
        coords = gclient.geocode(closest)

        y_coor = (coords[0]['geometry']['viewport']['northeast']['lng'] +
                  coords[0]['geometry']['viewport']['southwest']['lng']) / 2

        x_coor = (coords[0]['geometry']['viewport']['northeast']['lat'] +
                  coords[0]['geometry']['viewport']['southwest']['lat']) / 2

        if duration > max_delivery_minutes:
            returned_message = "closest shop is more than {} away " \
                               "from client =>: {} mins, address: {} " \
                               "destination: {}".format(max_delivery_minutes, duration, closest, dest)
            print(returned_message)
            # exit()
            result = ResultCode(False, returned_message)
            return result
        # expand shop time such that the upper bound on the shop time is location's lower bound -
        # time between them and shop's lower bound is shop upper bound - one hour
        upper_bound = (time_windows[i][0] + time_windows[i][1])/2
        lower_bound = upper_bound - max_delivery_minutes
        upper_bound = int(upper_bound)
        lower_bound = int(lower_bound)
        # upper_bound and lower bound should be related to time of delivery not location's lower bound

        time_windows.append((lower_bound, upper_bound))
        locations.append((x_coor, y_coor))

    return ResultCode(True)


# ***************************************************************************************
# **************************************************************************************
# **************************      speed functions *************************************
# ************************************************************************************
def gmaps_speed(gclient, x1, y1,
                         x2, y2):
    # speed = gclient.snapped_speed_limits([(x1, y1),(x2, y2)])
    # print("gmaps speed arr = ",speed)
    speed = randint(60, 100)
    # convert km/h to meters/minute
    speed = 1000 * speed / 60
    return speed


def func_speed_mat(loc, gclient):
    # Create the distance between locations matrix array.
    size = len(loc)
    speed_mat = [0] * size
    for from_node in range(size):
        speed_mat[from_node] = [0] * size
        for to_node in range(size):
            x1 = loc[from_node][0]
            y1 = loc[from_node][1]
            x2 = loc[to_node][0]
            y2 = loc[to_node][1]
            speed_mat[from_node][to_node] = gmaps_speed(gclient, x1, y1, x2, y2)
    return speed_mat


# [START solution_printer]
def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    total_distance = 0
    print_str = ""
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Duration of the route: {}\n'.format(str(timedelta(minutes=route_distance))[:-3])
        print(plan_output)
        print_str = print_str + plan_output
        total_distance += route_distance
    # print('Total Distance of all routes: {}m'.format(total_distance))
    print('Total duration of all routes: {}'.format(str(timedelta(minutes=total_distance))[:-3]))
    # print_str = print_str + '\nTotal Distance of all routes: {}m'.format(total_distance)
    print_str = print_str + '\nTotal duration of all routes: {}'.format(str(timedelta(minutes=total_distance))[:-3])
    # [END solution_printer]
    
    return print_str


def create_data_model_d():
    data = {}
    data['locations'] = \
        [(4, 4),  # depot
         (2, 0), (8, 0),  # locations to visit
         (0, 1), (1, 1),
         (5, 2), (7, 2),
         (3, 3), (6, 3),
         (5, 5), (8, 5),
         (1, 6), (2, 6),
         (3, 7), (6, 7),
         (0, 8), (7, 8)]
    data['distance_matrix'] = [
        [
            0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
            468, 776, 662
        ],
        [
            548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
            1016, 868, 1210
        ],
        [
            776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
            1130, 788, 1552, 754
        ],
        [
            696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
            1164, 560, 1358
        ],
        [
            582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
            1050, 674, 1244
        ],
        [
            274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
            514, 1050, 708
        ],
        [
            502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
            514, 1278, 480
        ],
        [
            194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
            662, 742, 856
        ],
        [
            308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
            320, 1084, 514
        ],
        [
            194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
            274, 810, 468
        ],
        [
            536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
            730, 388, 1152, 354
        ],
        [
            502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
            308, 650, 274, 844
        ],
        [
            388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
            536, 388, 730
        ],
        [
            354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
            342, 422, 536
        ],
        [
            468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
            342, 0, 764, 194
        ],
        [
            776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
            388, 422, 764, 0, 798
        ],
        [
            662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
            536, 194, 798, 0
        ],
    ]
    # [START pickups_deliveries]
    data['pickups_deliveries'] = [
        [1, 6],
        [2, 10],
        [4, 3],
        [5, 9],
        [7, 8],
        [15, 11],
        [13, 12],
        [16, 14],
    ]
    data["time_windows"] = [
            (0, 50),  # depot
            (7, 120),  # 1
            (10, 150),  # 2
            (5, 140),  # 3
            (5, 130),  # 4
            (0, 50),  # 5
            (5, 100),  # 6
            (0, 100),  # 7
            (5, 100),  # 8
            (0, 50),  # 9
            (10, 160),  # 10
            (10, 150),  # 11
            (0, 50),  # 12
            (5, 100),  # 13
            (7, 120),  # 14
            (10, 150),  # 15
            (5, 150),  # 16
        ]
    data["time_per_demand_unit"] = 1
    gclient = 1
    data["vehicle_speed"] = func_speed_mat(data['locations'], gclient)
    # print(data["vehicle_speed"])
    
    data["time_matrix"] = func_time_matrix(data)
    # print(data["time_matrix"])
    data["demands"] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    
    # [END pickups_deliveries]
    data['num_vehicles'] = 4
    data['depot'] = 0

    return ResultCode(True, data)


def check():
    return "all is ok"


def main():
    print("create data model")
    result = create_data_model()
    # result = create_data_model_d()
    if not result.is_successful:
        return result.body
    data = result.body

    print(data)

    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Register time callback
    def time_callback(from_index, to_index):
        """Returns the manhattan distance travel time between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["time_matrix"][from_node][to_node]

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    # Register demands callback
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data.demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)

    dimension_name = 'Distance'
    # max distance set to 500km or 500 000 meters
    routing.AddDimension(distance_callback_index, 0, 500000, True,
                             dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_index) <=
            distance_dimension.CumulVar(delivery_index))
    # routing.SetPickupAndDeliveryPolicyOfAllVehicles(pywrapcp.RoutingModel.FIFO)
    # routing.SetPickupAndDeliveryPolicyOfAllVehicles(pywrapcp.RoutingModel.LIFO)

    time = 'Time'
    # max slack time set to 12 hours
    routing.AddDimension(time_callback_index, 60 * 12, 60 * 12, False, time)
    time_dimension = routing.GetDimensionOrDie(time)
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0],
                                                time_window[1])

        routing.AddToAssignment(time_dimension.SlackVar(index))

    # Add time window constraints for each vehicle start node and 'copy' the
    # slack var in the solution object (aka Assignment) to print it.
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_window = data['time_windows'][0]
        time_dimension.CumulVar(index).SetRange(time_window[0],
                                                time_window[1])
        routing.AddToAssignment(time_dimension.SlackVar(index))

    # Instantiate route start and end times to produce feasible times.
    for vehicle_id in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(vehicle_id)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(vehicle_id)))

    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # pylint: disable=no-member
    search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print the solution.
    if assignment:
        return print_solution(data, manager, routing, assignment)
    else: 
        return "no assignment"


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python simple_server.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    (args, _) = parser.parse_args()
    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)

