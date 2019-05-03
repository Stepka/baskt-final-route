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


@app.route("/final_route")
def final_route():
    '''
    Here is API method for get some result with this script
    :return:
    '''

    locations = request.args.get('locations')
    time_windows = request.args.get('time_windows')
    shops = request.args.get('shops')
    cold_deliveries = request.args.get('cold_deliveries')
    num_vehicles = request.args.get('num_vehicles')

    if locations is None:
        return ResultCode(False, 'Missed required parameter "locations"').as_json_string()
    if time_windows is None:
        return ResultCode(False, 'Missed required parameter "time_windows"').as_json_string()
    if shops is None:
        return ResultCode(False, 'Missed required parameter "shops"').as_json_string()
    if cold_deliveries is None:
        # return ResultCode(False, 'Missed required parameter "cold_deliveries"').as_json_string()
        cold_deliveries = '[]'
    if num_vehicles is None:
        # return ResultCode(False, 'Missed required parameter "num_vehicles"').as_json_string()
        num_vehicles = hardcoded.max_vehicles_hardcoded()

    locations = json.loads(locations)
    time_windows = json.loads(time_windows)
    shops = json.loads(shops)
    cold_deliveries = json.loads(cold_deliveries)
    num_vehicles = int(num_vehicles)

    for i in range(len(locations)):
        locations[i] = tuple(locations[i])
    for i in range(len(time_windows)):
        time_windows[i] = tuple(time_windows[i])

    print(locations)
    print(time_windows)
    print(shops)
    print(cold_deliveries)

    result = fr.create_data_model(locations, time_windows, shops, cold_deliveries, num_vehicles)
    if not result.successful:
        return result

    data = result.body
    return json.dumps(fr.calculate_routes(data, False))


@app.route("/final_route/debug")
def final_route_debug():

    # debug, hardcoded values
    locations = hardcoded.locations_hardcoded()
    time_windows = hardcoded.time_windows_hardcoded()
    shops = hardcoded.shops_hardcoded()
    destinations = hardcoded.cold_deliveries_hardcoded()
    # demands = hardcoded.demands_hardcoded()
    num_vehicles = hardcoded.max_vehicles_hardcoded()

    result = fr.create_data_model(locations, time_windows, shops, destinations, num_vehicles)
    # result = create_data_model_d()
    if not result.successful:
        return result

    data = result.body
    return json.dumps(fr.calculate_routes(data, False))


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python final_route_flask_server.py -p 5000")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    (args, _) = parser.parse_args()
    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)
