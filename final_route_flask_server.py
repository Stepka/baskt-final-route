import json

from flask import Flask
from flask import request
import final_route as fr
from final_route import ResultCode
import hardcoded_routes_data as hardcoded
import sys
import optparse


app = Flask(__name__)


@app.route("/")
def check_if_running():
    print("All is ok, server is running!")
    return "All is ok, server is running!"


@app.route("/final_route", methods=['GET', 'POST'])
def final_route():
    '''
    Here is API method for get some result with this script
    :return:
    '''

    params_json = request.get_json()

    if 'locations' in params_json:
        locations = params_json['locations']
    else:
        return ResultCode(False, 'Missed required parameter "locations"').as_json_string()

    if 'time_windows' in params_json:
        time_windows = params_json['time_windows']
    else:
        return ResultCode(False, 'Missed required parameter "time_windows"').as_json_string()

    if 'order_ids' in params_json:
        order_ids = params_json['order_ids']
    else:
        return ResultCode(False, 'Missed required parameter "order_ids"').as_json_string()

    if 'shops' in params_json:
        shops = params_json['shops']
    else:
        return ResultCode(False, 'Missed required parameter "shops"').as_json_string()

    if 'cold_deliveries' in params_json:
        cold_deliveries = params_json['cold_deliveries']
    else:
        cold_deliveries = []

    if 'num_vehicles' in params_json:
        num_vehicles = params_json['num_vehicles']
    else:
        num_vehicles = hardcoded.max_vehicles_hardcoded()

    # locations = json.loads(locations)
    # time_windows = json.loads(time_windows)
    # shops = json.loads(shops)
    # cold_deliveries = json.loads(cold_deliveries)
    # num_vehicles = int(num_vehicles)

    for i in range(len(locations)):
        locations[i] = tuple(locations[i])
    for i in range(len(time_windows)):
        time_windows[i] = tuple(time_windows[i])

    print(locations)
    print(time_windows)
    print(order_ids)
    print(shops)
    print(cold_deliveries)

    result = fr.create_data_model(locations, time_windows, order_ids, shops, cold_deliveries, num_vehicles)
    if not result.successful:
        return result

    data = result.body
    return fr.calculate_routes(data, False).as_json_string()


@app.route("/final_route/debug")
def final_route_debug():

    # debug, hardcoded values
    locations = hardcoded.locations_hardcoded()
    time_windows = hardcoded.time_windows_hardcoded()
    shops = hardcoded.shops_hardcoded()
    destinations = hardcoded.cold_deliveries_hardcoded()
    order_ids = hardcoded.order_ids_hardcoded()
    num_vehicles = hardcoded.max_vehicles_hardcoded()

    result = fr.create_data_model(locations, time_windows, order_ids, shops, destinations, num_vehicles)
    # result = create_data_model_d()
    if not result.successful:
        return result

    data = result.body

    return fr.calculate_routes(data, False).as_json_string()


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python final_route_flask_server.py -p 5000")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    (args, _) = parser.parse_args()
    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)
