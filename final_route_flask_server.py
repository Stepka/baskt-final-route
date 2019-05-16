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
    try:
        locations = []
        time_windows = []
        cold_deliveries = []
        hub_indexes = []
        order_ids = []

        params_json = request.get_json()

        print("payload:", params_json)

        if 'orders' in params_json:
            orders = params_json['orders']
        else:
            return ResultCode(False, '', ['Missed required parameter "orders"']).as_json_string()

        if 'hubs' in params_json:
            hubs = params_json['hubs']
        else:
            return ResultCode(False, '', ['Missed required parameter "hubs"']).as_json_string()

        if 'shops' in params_json:
            shops = params_json['shops']
        else:
            return ResultCode(False, '', ['Missed required parameter "shops"']).as_json_string()

        # if 'cold_deliveries' in params_json:
        #     cold_deliveries = params_json['cold_deliveries']
        # else:
        #     cold_deliveries = []

        if 'num_vehicles' in params_json:
            num_vehicles = params_json['num_vehicles']
        else:
            num_vehicles = hardcoded.max_vehicles_hardcoded()

        if 'with_print' in params_json:
            with_print = params_json['with_print']
        else:
            with_print = False

        # locations = json.loads(locations)
        # time_windows = json.loads(time_windows)
        # shops = json.loads(shops)
        # cold_deliveries = json.loads(cold_deliveries)
        # num_vehicles = int(num_vehicles)

        if num_vehicles < len(hubs):
            num_vehicles = len(hubs)

        vehicles_per_hub = int(num_vehicles / len(hubs))
        for j in range(vehicles_per_hub + 1):
            for i in range(len(hubs)):
                if j * len(hubs) + i >= num_vehicles:
                    break

                # add hub to locations only once
                if j == 0:
                    hub = hubs[i]
                    locations.append((hub['latitude'], hub['longitude']))
                    time_windows.append((hub['fromTime'], hub['toTime']))
                    order_ids.append('')

                hub_indexes.append(i)

        for i in range(len(orders)):
            order = orders[i]
            order_ids.append(order['orderId'])
            locations.append((order['latitude'], order['longitude']))
            time_windows.append((order['fromTime'], order['toTime']))
            if order['isColdDelivery']:
                # we add i + <hubs size> index because first locations for hubs
                cold_deliveries.append(i + len(hubs))

        # for i in range(len(locations)):
        #     locations[i] = tuple(locations[i])
        # for i in range(len(time_windows)):
        #     time_windows[i] = tuple(time_windows[i])

        print("locations:", locations)
        print("time_windows:", time_windows)
        print("order_ids:", order_ids)
        print("shops:", shops)
        print("hub_indexes:", hub_indexes)
        print("cold_deliveries:", cold_deliveries)

        errors = []
        warnings = []
        result = fr.create_data_model(locations, time_windows, order_ids, shops,
                                      cold_deliveries, num_vehicles, hub_indexes)

        errors.extend(result.errors)
        warnings.extend(result.warnings)
        if not result.successful:
            return result.as_json_string()

        data = result.body

        result, _ = fr.calculate_routes(data, with_print)
        result.errors.extend(errors)
        result.warnings.extend(warnings)
        return result.as_json_string()

    except Exception as ex:
        error = "Exception '{}' caught, details: {}".format(type(ex).__name__, str(ex))
        return ResultCode(False, "", [error]).as_json_string()


@app.route("/final_route/debug")
def final_route_debug():

    # debug, hardcoded values
    locations = hardcoded.locations_hardcoded()
    time_windows = hardcoded.time_windows_hardcoded()
    shops = hardcoded.shops_hardcoded()
    cold_deliveries = hardcoded.cold_deliveries_hardcoded()
    order_ids = hardcoded.order_ids_hardcoded()
    num_vehicles = hardcoded.max_vehicles_hardcoded()
    hub_indexes = hardcoded.hubs_hardcoded()

    result = fr.create_data_model(locations, time_windows, order_ids, shops,
                                  cold_deliveries, num_vehicles, hub_indexes)
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
