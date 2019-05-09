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

    locations = []
    time_windows = []
    cold_deliveries = []
    order_ids = []

    params_json = request.get_json()

    if 'orders' in params_json:
        orders = params_json['orders']
    else:
        return ResultCode(False, 'Missed required parameter "orders"').as_json_string()

    if 'hub' in params_json:
        hub = params_json['hub']
        locations.append((hub['latitude'], hub['longitude']))
        time_windows.append((hub['fromTime'], hub['toTime']))
        order_ids.append('')
    else:
        return ResultCode(False, 'Missed required parameter "hub"').as_json_string()

    if 'shops' in params_json:
        shops = params_json['shops']
    else:
        return ResultCode(False, 'Missed required parameter "shops"').as_json_string()

    # if 'cold_deliveries' in params_json:
    #     cold_deliveries = params_json['cold_deliveries']
    # else:
    #     cold_deliveries = []

    if 'num_vehicles' in params_json:
        num_vehicles = params_json['num_vehicles']
    else:
        num_vehicles = hardcoded.max_vehicles_hardcoded()

    if 'with_print' in params_json:
        with_print = params_json['with_print'] == 'true'
    else:
        with_print = False

    # locations = json.loads(locations)
    # time_windows = json.loads(time_windows)
    # shops = json.loads(shops)
    # cold_deliveries = json.loads(cold_deliveries)
    # num_vehicles = int(num_vehicles)

    for i in range(len(orders)):
        order = orders[i]
        order_ids.append(order['orderId'])
        locations.append((order['latitude'], order['longitude']))
        time_windows.append((order['fromTime'], order['toTime']))
        if order['isColdDelivery']:
            # we add i + 1 index because 0 is for hub
            cold_deliveries.append(i + 1)

    # for i in range(len(locations)):
    #     locations[i] = tuple(locations[i])
    # for i in range(len(time_windows)):
    #     time_windows[i] = tuple(time_windows[i])

    print(locations)
    print(time_windows)
    print(order_ids)
    print(shops)
    print(cold_deliveries)

    result = fr.create_data_model(locations, time_windows, order_ids, shops, cold_deliveries, num_vehicles)
    if not result.successful:
        return result

    data = result.body

    result, _ = fr.calculate_routes(data, with_print)
    return result.as_json_string()


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

    result, _ = fr.calculate_routes(data, True)
    return result.as_json_string()


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python final_route_flask_server.py -p 5000")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    (args, _) = parser.parse_args()
    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)
