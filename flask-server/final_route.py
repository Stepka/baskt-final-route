from __future__ import print_function

import json
import uuid

import sys

import requests
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
from random import randint
from datetime import datetime, date, timedelta

# is the max time between picking up the cold item and delivering it to a customer
MAX_COLD_DELIVERY_MINUTES = 60
MAX_DAY_TIME = 24 * 60
MAX_ROUTE_DURATION = 4 * 60


# Helper class to convert a DynamoDB item to JSON.
class ResultCode:
    def __init__(self, is_successful, body=None, errors=None, warnings=None):
        self.successful = is_successful
        self.body = body
        if errors is None:
            errors = []
        self.errors = errors
        if warnings is None:
            warnings = []
        self.warnings = warnings

    def as_json_string(self, info='all'):
        result = {'successful': self.successful, 'body': self.body}
        if 'errors' in info or 'all' in info:
            result['errors'] = self.errors
        if 'warnings' in info or 'all' in info:
            result['warnings'] = self.warnings

        str = json.dumps(result)
        return str.replace('""', '"-"')


def add_pickups_for_cold_deliveries(gclient,
                                    locations,
                                    location_ids,
                                    order_ids,
                                    time_windows,
                                    types,
                                    shops_arr,
                                    dest_arr):
    '''
    Function for pickup cold deliveries from the nearest shop to destination.

    :param gclient:
    :param locations:
    :param time_windows:
    :param shops_arr:
    :param dest_arr: is the index of locations in the locations array that need cold items delivered
    :return:
    '''
    
    loc_length = len(locations)
    warnings = []
    result = one_hour(gclient, locations, location_ids, order_ids, time_windows, types,
                      shops_arr, dest_arr, MAX_COLD_DELIVERY_MINUTES)
    warnings.extend(result.warnings)
    if not result.successful:
        return result

    pickup_deliver = []
    for i in range(len(dest_arr)):
        pickup_deliver.append([loc_length+i, dest_arr[i]])
    return ResultCode(True, pickup_deliver, [], warnings)


def create_vroom_model(locations, location_ids, time_windows, order_ids, shops, cold_deliveries, num_vehicles,
                       hub_indexes, info='all'):

    gclient = googlemaps.Client(key='AIzaSyAei-_KeQOTzjN_6sIPuQ3yW4MlRk0MtXk')

    errors = []
    warnings = []

    data = {}
    data['locations'] = locations
    data['location_ids'] = location_ids

    # if len(data['locations'][0]) == 1:
    #     data['addresses'] = [i[0] for i in locations]
    #     convert_addresses_to_coordinates(data['locations'], gclient)
    data["time_windows"] = conv_time(time_windows)
    data['order_ids'] = order_ids
    data['starts'] = hub_indexes
    data['ends'] = hub_indexes
    data['types'] = ['delivery' for _ in locations]
    for i in hub_indexes:
        data['types'][i] = 'start'

    result = add_pickups_for_cold_deliveries(gclient, data['locations'], data['location_ids'], data['order_ids'],
                                             data['time_windows'], data['types'], shops, cold_deliveries)

    # if 'addresses' in info or 'all' in info:
    #     data['addresses'] = convert_coordinates_to_addresses(gclient, locations)

    errors.extend(result.errors)
    warnings.extend(result.warnings)
    if not result.successful:
        return result
    data['cold_deliveries'] = result.body

    # print("distance_matrix starts...", len(data['locations']))

    # result = func_dist_mat(data['locations'], gclient)
    # errors.extend(result.errors)
    # warnings.extend(result.warnings)
    # if not result.successful:
    #     return result
    # data['distance_matrix'] = result.body
    # print("distance_matrix ends")

    # data["time_per_demand_unit"] = 1
    # data["vehicle_speed"] = func_speed_mat(data['locations'], gclient)
    # data["time_matrix"] = func_time_matrix(data)

    # data["demands"] = demands

    data['num_vehicles'] = num_vehicles
    data['vehicle_load_time'] = 20
    # data['vehicle_unload_time'] = 5
    data['depot'] = 0
    print("data ready")

    vroom_model = {}
    vroom_model['vehicles'] = []
    vroom_model['jobs'] = []

    # NOTE! swap lat and long for osrm
    for i in range(len(data['starts'])):
        vehicle = {
            "id": i,
            "start": [data['locations'][data['starts'][i]][1], data['locations'][data['starts'][i]][0]],
            "end": [data['locations'][data['starts'][i]][1], data['locations'][data['starts'][i]][0]],
            "time_windows": [[data['time_windows'][data['starts'][i]][0]*60, data['time_windows'][data['starts'][i]][1]*60]]
        }
        vroom_model['vehicles'].append(vehicle)

    for i in range(len(data['locations'])):
        if i not in data['starts']:
            job = {
                "id": i,
                "service": 300,
                "location": [data['locations'][i][1], data['locations'][i][0]],
                "time_windows": [[data['time_windows'][i][0]*60, data['time_windows'][i][1]*60]]
            }
            vroom_model['jobs'].append(job)
    # vroom_model['options'] = {"g": True}
    print(vroom_model)
    print(json.dumps(vroom_model))

    data['vroom'] = vroom_model

    return ResultCode(True, data, errors, warnings)


def create_data_model(locations, location_ids, time_windows, order_ids, shops, cold_deliveries, num_vehicles,
                      hub_indexes, info='all'):
    '''
    Initialize all the variables.

    :param locations:
    :param location_ids:
    :param time_windows:
    :param order_ids:
    :param shops:
    :param cold_deliveries:
    :param num_vehicles:
    :param hub_indexes:
    :param info:
    :return:
    '''

    gclient = googlemaps.Client(key='AIzaSyAei-_KeQOTzjN_6sIPuQ3yW4MlRk0MtXk')

    errors = []
    warnings = []

    data = {}
    data['locations'] = locations
    data['location_ids'] = location_ids

    # if len(data['locations'][0]) == 1:
    #     data['addresses'] = [i[0] for i in locations]
    #     convert_addresses_to_coordinates(data['locations'], gclient)
    data["time_windows"] = conv_time(time_windows)
    data['order_ids'] = order_ids
    data['starts'] = hub_indexes
    data['ends'] = hub_indexes
    data['types'] = ['delivery' for _ in locations]
    for i in hub_indexes:
        data['types'][i] = 'start'

    result = add_pickups_for_cold_deliveries(gclient, data['locations'], data['location_ids'], data['order_ids'],
                                             data['time_windows'], data['types'], shops, cold_deliveries)

    # if 'addresses' in info or 'all' in info:
    #     data['addresses'] = convert_coordinates_to_addresses(gclient, locations)

    errors.extend(result.errors)
    warnings.extend(result.warnings)
    if not result.successful:
        return result
    data['cold_deliveries'] = result.body

    print("distance_matrix starts...", len(data['locations']))

    # result = func_dist_mat(data['locations'], gclient)
    result = func_dist_mat_osrm(data['locations'])
    errors.extend(result.errors)
    warnings.extend(result.warnings)
    if not result.successful:
        return result
    data['distance_matrix'] = result.body
    ####
    print("distance_matrix ends")
    
    data["time_per_demand_unit"] = 1
    data["vehicle_speed"] = func_speed_mat(data['locations'], gclient)    
    data["time_matrix"] = func_time_matrix(data)
    
    # data["demands"] = demands
    
    data['num_vehicles'] = num_vehicles
    data['vehicle_load_time'] = 20
    # data['vehicle_unload_time'] = 5
    data['depot'] = 0
    print("data ready")

    return ResultCode(True, data, errors, warnings)


# ******************************************************************************************
# ************************   time_arr functions *******************************************
# ****************************************************************************************
def conv_time(time_arr):
    # base_time_0 = convert_to_24(time_arr[0][0])
    # base_time_1 = convert_to_24(time_arr[0][1])
    time_list = []
    for i in range(len(time_arr)):
        # a = abs(base_time_0 - convert_to_24(time_arr[i][0]))
        # b = abs(base_time_0 - convert_to_24(time_arr[i][1]))
        a = abs(convert_to_24(time_arr[i][0]))
        b = abs(convert_to_24(time_arr[i][1]))
        time_list.append((a, b))
    return time_list


def convert_to_24(datestr):
    in_time = datetime.strptime(datestr, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")

    return int(out_time[:2])*60 + int(out_time[-2:])


def conv_minutes_to_time(minutes):
    today = date.today()
    today = datetime.combine(today, datetime.min.time())
    time1 = today + timedelta(minutes=minutes)
    return time1.strftime("%I:%M %p")


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
# def func_dist_mat(loc, gclient):
#     # Create the distance between locations matrix array.
#     size = len(loc)
#     dist_mat = [0] * size
#     warnings = []
#     for from_node in range(size):
#         dist_mat[from_node] = [0] * size
#         for to_node in range(size):
#             print("calculate distance... {}/{}, from {} to {}".format(size * from_node + to_node,
#                                                                       size * size,
#                                                                       loc[from_node],
#                                                                       loc[to_node]))
#             x1 = loc[from_node][0]
#             y1 = loc[from_node][1]
#
#             x2 = loc[to_node][0]
#             y2 = loc[to_node][1]
#
#             result = gmaps_dist(gclient, x1, y1, x2, y2)
#             if not result.successful:
#                 # return result
#                 # we decide error on this step as warning - just set maximum distance to error point
#                 warnings.extend(result.errors)
#                 warnings.extend(result.warnings)
#                 dist_mat[from_node][to_node] = sys.maxsize
#             else:
#                 dist_mat[from_node][to_node] = result.body
#
#     return ResultCode(True, dist_mat, [], warnings)


def func_dist_mat_osrm(locations):
    # Create the distance between locations matrix array.
    warnings = []

    # osrm_url = "http://router.project-osrm.org/table/v1/driving/"
    osrm_url = "http://osrm:5000/table/v1/driving/"

    for loc in locations:
        osrm_url += '{},{};'.format(loc[1], loc[0])

    osrm_url = osrm_url[:-1] + '?annotations=distance'
    tables_request = requests.get(osrm_url)

    osrm_response = json.loads(tables_request.text)

    dist_mat = osrm_response['distances']

    return ResultCode(True, dist_mat, [], warnings)


# def func_dist_from_to(sources, destinations, gclient):
#     # Create the distance between locations matrix array.
#
#     sources_index = 0
#     destinations_index = 0
#     sources_sizes = len(sources)
#     destinations_sizes = len(destinations)
#     dist_mat = [0] * sources_sizes
#     warnings = []
#     for from_node in sources:
#         destinations_index = 0
#         dist_mat[sources_index] = [0] * destinations_sizes
#         for to_node in destinations:
#             print("calculate distance... {}/{}, from {} to {}".format(destinations_sizes * sources_index + destinations_index,
#                                                                       destinations_sizes * sources_sizes,
#                                                                       sources_index,
#                                                                       destinations_index))
#             x1 = from_node[0]
#             y1 = from_node[1]
#
#             x2 = to_node[0]
#             y2 = to_node[1]
#
#             result = gmaps_dist(gclient, x1, y1, x2, y2)
#             if not result.successful:
#                 # return result
#                 # we decide error on this step as warning - just set maximum distance to error point
#                 warnings.extend(result.errors)
#                 warnings.extend(result.warnings)
#                 dist_mat[sources_index][destinations_index] = sys.maxsize
#             else:
#                 dist_mat[sources_index][destinations_index] = result.body
#
#             destinations_index += 1
#
#         sources_index += 1
#
#     return ResultCode(True, dist_mat, [], warnings)


def func_dist_from_to_osrm(sources, destinations):
    # Create the distance between locations matrix array.

    warnings = []

    # osrm_url = "http://router.project-osrm.org/table/v1/driving/"
    osrm_url = "http://osrm:5000/table/v1/driving/"

    for loc in sources:
        osrm_url += '{},{};'.format(loc[1], loc[0])

    for loc in destinations:
        osrm_url += '{},{};'.format(loc[1], loc[0])

    osrm_url = osrm_url[:-1] + '?annotations=distance,duration'

    osrm_url += '&sources='
    for i in range(len(sources)):
        osrm_url += str(i) + ';'
    osrm_url = osrm_url[:-1]

    osrm_url += '&destinations='
    for i in range(len(destinations)):
        osrm_url += str(len(sources) + i) + ';'
    osrm_url = osrm_url[:-1]

    print(osrm_url)

    tables_request = requests.get(osrm_url)

    osrm_response = json.loads(tables_request.text)

    # dist_mat = osrm_response['distances']

    return ResultCode(True, osrm_response, [], warnings)


# def gmaps_dist(gclient, x1, y1,
#                         x2, y2):
#     # Gmaps distance between points
#     origin = [(x1, y1)]
#     dest = [(x2, y2)]
#
#     depart_time = "now"
#
#     dist1 = gclient.distance_matrix(origin, dest, departure_time=depart_time,
#                                     mode='driving', traffic_model="best_guess")
#     dist2 = gclient.distance_matrix(origin, dest, departure_time=depart_time,
#                                     mode='driving', traffic_model="pessimistic")
#
#     if dist2['rows'][0]['elements'][0]['status'] != 'OK':
#         returned_message = "Couldn't get distance between {} and {} can be a problem with the geocodes of origin or " \
#                            "destination or a server issue.".format(origin, dest)
#         print(returned_message)
#         print("the output is ", dist2)
#         # exit()
#         return ResultCode(False, "", [returned_message])
#
#     if dist1['rows'][0]['elements'][0]['status'] != 'OK':
#         returned_message = "Couldn't get distance between {} and {} can be a problem with the geocodes of origin or " \
#                            "destination or a server issue.".format(origin, dest)
#         print(returned_message)
#         print("the output is ", dist1)
#         # exit()
#         return ResultCode(False, "", [returned_message])
#
#     dist2 = dist2['rows'][0]['elements'][0]['distance']['value']
#     dist1 = dist1['rows'][0]['elements'][0]['distance']['value']
#
#     return ResultCode(True, int(max(dist1, dist2)))


def get_coordinates(loc, gclient):
    coordinates = gclient.geocode(loc)

    x_coor = coordinates[0]['geometry']['location']['lat']
    y_coor = coordinates[0]['geometry']['location']['lng']

    return x_coor, y_coor


def convert_addresses_to_coordinates(data, gclient):
    size = len(data)
    for i in range(size):
        if ('latitude' not in data[i]) or ('longitude' not in data[i]):
            x, y = get_coordinates(data[i]['address'], gclient)
            data[i]['latitude'] = x
            data[i]['longitude'] = y


def get_address(gclient, location):
    response = gclient.reverse_geocode(location)

    if len(response) > 0:
        address = response[0]['formatted_address']
    else:
        address = ""

    return address


def convert_coordinates_to_addresses(gclient, locations):
    addresses = []
    size = len(locations)
    for i in range(size):
        address = get_address(gclient, locations[i])
        addresses.append(address)

    return addresses


# ***************************************************************************************
# **************************************************************************************
# ******************      pickup_deliver  functions ***********************************
# ************************************************************************************
def one_hour_dist(gclient,
                  shop,
                  dest):
    dist = gclient.distance_matrix(shop, dest, mode='driving')

    if dist['rows'][0]['elements'][0]['status'] != 'OK':

        returned_message = "Couldn't get distance between {} and {} can be a problem with the geocodes of origin or " \
                           "destination or a server issue.".format(shop, dest)
        print(returned_message)
        print("the output is ", dist)
        # exit()
        result = ResultCode(False, "", [returned_message])
        return result
    else:
        #           estimated distance between them                  ,  shop's address         ,         estimated time between them.
        result_body = dist['rows'][0]['elements'][0]['distance']['value'], \
                      dist['origin_addresses'][0], \
                      int(dist['rows'][0]['elements'][0]['duration']['value'] / 60)
        return ResultCode(True, result_body)


def one_hour(gclient,
             locations,
             location_ids,
             order_ids,
             time_windows,
             types,
             shops_arr,
             dest_arr,
             max_delivery_minutes):
  
    # calculate the closest shop to index i
    # append the shop's coords to array of distances
    # increase number of locations by 1
    least_dist = 10000000000

    # all pickups should be after depot start time
    depot_start_time = time_windows[0][0]

    warnings = []
    dest_arr_coords = []
    dest_arr_indexes = []
    shops_arr_coords = []
    for i in dest_arr:
        dest_arr_coords.append(locations[i])
        dest_arr_indexes.append(i)
    for shop in shops_arr:
        shops_arr_coords.append([shop['latitude'], shop['longitude']])

    result = func_dist_from_to_osrm(dest_arr_coords, shops_arr_coords)
    print(result.body)

    duration_matrix = result.body['durations']
    distance_matrix = result.body['distances']
    for cold_index in range(len(duration_matrix)):
        i = dest_arr_indexes[cold_index]
        dest = locations[i]
        for shop_index in range(len(duration_matrix[cold_index])):
            dur = duration_matrix[cold_index][shop_index] / 60
            dist = distance_matrix[cold_index][shop_index]
            if least_dist > dist:
                least_dist = dist
                shop_id = shops_arr[shop_index]['shopId']
                duration = dur

    # for i in dest_arr:
    #     dest = locations[i]
    #     # print("check destination: {}".format(dest))
    #     for shop in shops_arr:
    #         result = one_hour_dist(gclient, (shop['latitude'], shop['longitude']), dest)
    #         if not result.successful:
    #             # return result
    #             # we decide error on this step as warning - just add warning
    #             warnings.extend(result.errors)
    #         else:
    #             dist, address, dur = result.body
    #             if least_dist > dist:
    #                 least_dist = dist
    #                 shop_id = shop['shopId']
    #                 closest = address
    #                 duration = dur

        print('closets is {}, distance: {}, duration: {}'.format(shop_id, least_dist, duration))

        if duration > max_delivery_minutes:
            returned_message = "closest shop is more than {} away " \
                               "from client =>: {} mins, " \
                               "destination: {}".format(max_delivery_minutes, duration, dest)
            print(returned_message)
            # exit()
            result = ResultCode(False, "", [returned_message], warnings)
            return result
        # expand shop time such that the upper bound on the shop time is location's lower bound -
        # time between them and shop's lower bound is shop upper bound - one hour
        # upper_bound = (time_windows[i][0] + time_windows[i][1])/2
        upper_bound = time_windows[i][1] - max_delivery_minutes
        lower_bound = time_windows[i][0] - max_delivery_minutes
        upper_bound = int(upper_bound)
        lower_bound = int(lower_bound)
        if lower_bound < depot_start_time:
            lower_bound = depot_start_time
        if upper_bound < lower_bound:
            upper_bound = lower_bound

        # upper_bound and lower bound should be related to time of delivery not location's lower bound

        time_windows.append((lower_bound, upper_bound))
        # locations.append((x_coor, y_coor))
        locations.append((shop['latitude'], shop['longitude']))
        location_ids.append(shop['shopId'])
        # addresses.append(closest)
        order_ids.append(order_ids[i])
        types.append('pickup')

    return ResultCode(True, "", [], warnings)


# ***************************************************************************************
# **************************************************************************************
# **************************      speed functions *************************************
# ************************************************************************************
def gmaps_speed(gclient, x1, y1,
                         x2, y2):
    # speed = gclient.snapped_speed_limits([(x1, y1),(x2, y2)])
    # print("gmaps speed arr = ",speed)
    speed = randint(20, 50)
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


def parse_solution_from_vroom(data, vroom_response, info='all'):
    result = {'routes': []}
    for vroom_route in vroom_response['routes']:
        start_time = -1
        vehicle_route = {}
        vehicle_route['route_id'] = str(uuid.uuid4())
        vehicle_route['description'] = 'Route for vehicle {}'.format(vroom_route['vehicle'])
        if 'destinations' in info or 'all' in info:
            vehicle_route['destinations'] = []
        if 'coordinates' in info or 'all' in info:
            vehicle_route['coordinates'] = []

        num_orders = 0
        for step_index in range(len(vroom_route['steps'])):
            vroom_step = vroom_route['steps'][step_index]
            destination = {}
            if vroom_step['type'] == 'start':
                index = 0
            elif vroom_step['type'] == 'end':
                index = 0
            elif vroom_step['type'] == 'job':
                index = int(vroom_step['job'])
            # destination['index'] = manager.IndexToNode(index)
            destination['type'] = data['types'][index]
            if destination['type'] == 'delivery':
                num_orders += 1
            if vroom_step['type'] == 'end':
                destination['type'] = 'finish'
            destination['order_id'] = data['order_ids'][index]
            destination['location'] = data['locations'][index]
            destination['location_id'] = data['location_ids'][index]
            # if 'addresses' in info or 'all' in info:
            #     destination['address'] = data['addresses'][index]

            from_time = vroom_step['arrival']
            to_time = vroom_step['arrival']
            if vroom_step['type'] == 'job':
                to_time += vroom_step['waiting_time']
            destination['from_time'] = conv_minutes_to_time(int(from_time/60))
            destination['to_time'] = conv_minutes_to_time(int(to_time/60))
            time_window = data['time_windows'][index]
            destination['time_window'] = (conv_minutes_to_time(time_window[0]), conv_minutes_to_time(time_window[1]))

            if start_time >= 0:
                delivery_time = vroom_step['arrival'] - start_time
                destination['delivery_time'] = str(timedelta(minutes=int(delivery_time/60)))[:-3]

            if step_index < len(vroom_route['steps']) - 1:
                next_destination_duration = vroom_route['steps'][step_index + 1]['duration'] - vroom_route['steps'][step_index]['duration']
                destination['next_destination_duration'] = str(timedelta(minutes=int(next_destination_duration/60)))[:-3]

            if 'destinations' in info or 'all' in info:
                vehicle_route['destinations'].append(destination)
            if 'coordinates' in info or 'all' in info:
                vehicle_route['coordinates'].append(destination['location'])

        route_duration = vroom_route['duration'] + vroom_route['service'] + vroom_route['waiting_time']
        vehicle_route['route_duration'] = str(timedelta(minutes=int(route_duration/60)))[:-3]
        vehicle_route['num_orders'] = num_orders

        if ('destinations' in vehicle_route and len(vehicle_route['destinations']) > 2) or \
                ('coordinates' in vehicle_route and len(vehicle_route['coordinates']) > 2):
            result['routes'].append(vehicle_route)

    return result


def parse_solution(data, manager, routing, assignment, with_print, info='all'):
    """Prints assignment on console."""
    time_dimension = routing.GetDimensionOrDie('Time')
    total_duration = 0
    print_str = ""
    result = {'routes': []}
    for vehicle_id in range(data['num_vehicles']):
        vehicle_route = {}
        vehicle_route['route_id'] = str(uuid.uuid4())
        vehicle_route['description'] = 'Route for vehicle {}'.format(vehicle_id)
        if 'destinations' in info or 'all' in info:
            vehicle_route['destinations'] = []
        if 'coordinates' in info or 'all' in info:
            vehicle_route['coordinates'] = []
        start_index = index = routing.Start(vehicle_id)
        previous_index = -1
        start_time = -1
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)

        num_orders = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            destination = {}
            destination['index'] = manager.IndexToNode(index)
            destination['type'] = data['types'][destination['index']]
            if destination['type'] == 'delivery':
                num_orders += 1
            destination['order_id'] = data['order_ids'][destination['index']]
            destination['location'] = data['locations'][destination['index']]
            destination['location_id'] = data['location_ids'][destination['index']]
            # if 'addresses' in info or 'all' in info:
            #     destination['address'] = data['addresses'][destination['index']]
            destination['from_time'] = conv_minutes_to_time(assignment.Min(time_var))
            destination['to_time'] = conv_minutes_to_time(assignment.Max(time_var))
            time_window = data['time_windows'][destination['index']]
            destination['time_window'] = (conv_minutes_to_time(time_window[0]), conv_minutes_to_time(time_window[1]))

            # we should shift start time and end time of the start point closer to the next after start destination
            if previous_index == start_index:
                duration = routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                start_time = assignment.Min(time_var) - duration
                if start_time < 0:
                    start_time = 0
                previous_destination['from_time'] = conv_minutes_to_time(assignment.Min(time_var) - duration)
                previous_destination['to_time'] = conv_minutes_to_time(assignment.Max(time_var) - duration)

            if start_time >= 0:
                delivery_time = assignment.Min(time_var) - start_time
                destination['delivery_time'] = str(timedelta(minutes=delivery_time))[:-3]

            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            next_destination_duration = routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            destination['next_destination_duration'] = str(timedelta(minutes=next_destination_duration))[:-3]

            plan_output += ' {0} for {1} [{2}, {3}] \n ... {4} min -> '.format(destination['type'],
                                                                               destination['order_id'],
                                                                               destination['from_time'],
                                                                               destination['to_time'],
                                                                               destination['next_destination_duration'])
            if 'destinations' in info or 'all' in info:
                vehicle_route['destinations'].append(destination)
            if 'coordinates' in info or 'all' in info:
                vehicle_route['coordinates'].append(destination['location'])
            previous_destination = destination

        # add back to depot
        time_var = time_dimension.CumulVar(index)
        destination = {}
        destination['index'] = manager.IndexToNode(index)
        destination['type'] = 'finish'
        destination['order_id'] = data['order_ids'][destination['index']]
        destination['location'] = data['locations'][destination['index']]
        destination['location_id'] = data['location_ids'][destination['index']]
        # if 'addresses' in info or 'all' in info:
        #     destination['address'] = data['addresses'][destination['index']]
        destination['from_time'] = conv_minutes_to_time(assignment.Min(time_var))
        destination['to_time'] = conv_minutes_to_time(assignment.Max(time_var))
        time_window = data['time_windows'][destination['index']]
        destination['time_window'] = (conv_minutes_to_time(time_window[0]), conv_minutes_to_time(time_window[1]))
        plan_output += ' {0} [{1}, {2}]\n'.format(destination['order_id'],
                                                  destination['from_time'],
                                                  destination['to_time'])
        if 'destinations' in info or 'all' in info:
            vehicle_route['destinations'].append(destination)
        if 'coordinates' in info or 'all' in info:
            vehicle_route['coordinates'].append(destination['location'])

        # calculate totals for route/vehicle
        route_duration = assignment.Min(time_var) - start_time
        plan_output += 'Duration of the route: {}\n'.format(str(timedelta(minutes=route_duration))[:-3])
        if with_print:
            vehicle_route['route_string'] = plan_output
        vehicle_route['route_duration'] = str(timedelta(minutes=route_duration))[:-3]
        vehicle_route['num_orders'] = num_orders

        if ('destinations' in vehicle_route and len(vehicle_route['destinations']) > 2) or \
                ('coordinates' in vehicle_route and len(vehicle_route['coordinates']) > 2):
            result['routes'].append(vehicle_route)

            print_str = print_str + plan_output
            total_duration += route_duration

    print_str = print_str + '\nTotal duration of all routes: {}'.format(str(timedelta(minutes=total_duration))[:-3])

    return result, print_str


def calculate_routes(data_model, with_print=True, info='all'):
    '''
    Function to calculate routes based on passed data model. Use create_data_model() for model creation.
    :param data_model: data model created with create_data_model() function
    :param with_print: return json (False) or print solution (True)
    :return: assigns
    '''

    manager = pywrapcp.RoutingIndexManager(
        len(data_model['time_matrix']),
        data_model['num_vehicles'],
        data_model['starts'],
        data_model['ends']
    )
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data_model['distance_matrix'][from_node][to_node]

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Register time callback
    def time_callback(from_index, to_index):
        """Returns the manhattan distance travel time between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data_model["time_matrix"][from_node][to_node]

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    # # Register demands callback
    # def demand_callback(from_index):
    #     """Returns the demand of the node."""
    #     # Convert from routing variable Index to demands NodeIndex.
    #     from_node = manager.IndexToNode(from_index)
    #     return data_model.demands[from_node]
    #
    # demand_callback_index = routing.RegisterUnaryTransitCallback(
    #     demand_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)

    dimension_name = 'Distance'
    # max distance set to 500km or 500 000 meters
    routing.AddDimension(distance_callback_index, 0, 500000, True, dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    time = 'Time'
    # max slack time set to 12 hours
    routing.AddDimension(time_callback_index, MAX_DAY_TIME, MAX_DAY_TIME, False, time)
    time_dimension = routing.GetDimensionOrDie(time)

    for request in data_model['cold_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            time_dimension.CumulVar(pickup_index) <=
            time_dimension.CumulVar(delivery_index))
    # routing.SetPickupAndDeliveryPolicyOfAllVehicles(pywrapcp.RoutingModel.FIFO)
    # routing.SetPickupAndDeliveryPolicyOfAllVehicles(pywrapcp.RoutingModel.LIFO)

    intervals = []
    for location_idx, time_window in enumerate(data_model['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        # print("::", index, type(time_window[0]), type(time_window[1]), time_window[0], time_window[1])
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        routing.AddToAssignment(time_dimension.SlackVar(index))

        # Add time windows at start of routes
        intervals.append(
            routing.solver().FixedDurationIntervalVar(
                time_dimension.CumulVar(index),
                data_model['vehicle_load_time'], 'load_interval'))

    # Add time window constraints for each vehicle start node and 'copy' the
    # slack var in the solution object (aka Assignment) to print it.
    for vehicle_id in range(data_model['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_window = data_model['time_windows'][0]
        time_dimension.CumulVar(index).SetRange(time_window[0],
                                                time_window[1])

        routing.AddToAssignment(time_dimension.SlackVar(index))

        # print("::>", index)
        # Add time windows at start of routes
        intervals.append(
            routing.solver().FixedDurationIntervalVar(
                time_dimension.CumulVar(index),
                data_model['vehicle_load_time'], 'load_interval'))
        # print(intervals[len(intervals) - 1])

    depot_usage = [1 for _ in range(len(intervals))]
    routing.solver().Add(
        routing.solver().Cumulative(intervals, depot_usage, 100, 'load_unload'))

    # Instantiate route start and end times to produce feasible times.
    for vehicle_id in range(data_model['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(vehicle_id)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(vehicle_id)))

    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # pylint: disable=no-member
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    # search_parameters.first_solution_strategy = (
    #     routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print the solution.
    if assignment:
        solution_json, solution_str = parse_solution(data_model, manager, routing, assignment, with_print, info)
        return ResultCode(True, solution_json), solution_str
    else:
        return ResultCode(False, "", ["no assignment"]), "no assignment"


def calculate_locations_in_radius(sources, destinations, radius, info):

    gclient = googlemaps.Client(key='AIzaSyAei-_KeQOTzjN_6sIPuQ3yW4MlRk0MtXk')

    convert_addresses_to_coordinates(sources, gclient)
    convert_addresses_to_coordinates(destinations, gclient)

    source_locations = []
    for i in range(len(sources)):
        source = sources[i]
        source_locations.append((source['latitude'], source['longitude']))

    destination_locations = []
    for i in range(len(destinations)):
        destination = destinations[i]
        destination_locations.append((destination['latitude'], destination['longitude']))

    # result = func_dist_from_to(source_locations, destination_locations, gclient)
    result = func_dist_from_to_osrm(source_locations, destination_locations)

    distances = result.body['distances']

    solution = []
    if 'in_radius' in info or 'all' in info:
        for i in range(len(distances)):
            in_radius = []
            for j in range(len(distances[i])):
                if distances[i][j] < radius:
                    destinations[j]['distance'] = distances[i][j]
                    in_radius.append(destinations[j])

            solution.append({'center': sources[i], 'in_radius': in_radius})

    return ResultCode(True, {'in_radius': solution})
