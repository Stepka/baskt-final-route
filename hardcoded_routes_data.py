import json

import final_route as fr
import optparse


# enter the time windows of all the clients here with the first one as the base time for all
def time_windows_hardcoded():
    time = [
        ("01:00 PM", "01:00 PM"),   # departure time
        ("02:15 PM", "02:25 PM"),
        ("02:15 PM", "02:25 PM"),
        ("02:00 PM", "02:10 PM"),
        # ("01:45 PM", "01:55 PM"),
        # ("01:00 PM", "01:08 PM"),
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
    #     ("01:00 PM", "02:00 PM"),   # departure time
    #     ("02:15 PM", "03:25 PM"),
    #     ("02:15 PM", "03:25 PM"),
    #     ("02:00 PM", "03:10 PM"),
    #     ("01:45 PM", "02:55 PM"),
    #     ("01:00 PM", "02:08 PM"),
    #     ("01:50 PM", "03:00 PM"),
    #     ("01:00 PM", "02:10 PM"),
    #     ("01:10 PM", "02:20 PM"),
    #     ("01:00 PM", "02:10 PM"),
    #     ("02:15 PM", "03:50 PM"),
    #     ("02:25 PM", "04:30 PM"),
    #     ("01:05 PM", "04:15 PM"),
    #     ("01:15 PM", "04:25 PM"),
    #     ("01:10 PM", "04:20 PM"),
    #     ("01:45 PM", "04:55 PM"),
    #     ("01:30 PM", "04:20 PM"),
    #     ("01:00 PM", "05:20 PM")
    #     ]

    return time


def locations_hardcoded():
    # Array of locations (lat, lng)
    locations = [(39.290440, -76.612330),   # depot
                 (39.348230, -76.732660),
                 (39.320510, -76.724570),
                 (39.353790, -76.758400),
                 # (39.348230, -76.732660),
                 # (39.658420, -77.175440),
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


def shops_hardcoded():
    current_city = 'Baltimore'
    shops = [
        current_city + " price rite",
        current_city + " shoppers",
        current_city + " safeway",
        current_city + " wegmans",
        current_city + " acme markets",
        current_city + " walmart",
        current_city + " 7-Eleven",
        current_city + " Target",
        current_city + " Save A Lot",
        current_city + " Walmart Supercenter"
    ]

    return shops


def dest_hardcoded():
    # destinations = [2, 3, 6, 7, 8, 4]
    destinations = [2, 3]
    return destinations


# index of locations in the locations array to deliver items ,
# basically u can deliver to the same location twice if u would like to
def demands_hardcoded():
    # location index to go to
    demands = [0, 1, 1, 2, 1, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8, 9]
    return demands


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
    data["vehicle_speed"] = fr.func_speed_mat(data['locations'], gclient)
    # print(data["vehicle_speed"])

    data["time_matrix"] = fr.func_time_matrix(data)
    # print(data["time_matrix"])
    data["demands"] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]

    # [END pickups_deliveries]
    data['num_vehicles'] = 4
    data['depot'] = 0

    return fr.ResultCode(True, data)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="")
    parser.add_option('-l', '--locations', action='store_true', dest='locations')
    parser.add_option('-t', '--time_windows', action='store_true', dest='time_windows')
    parser.add_option('-s', '--shops', action='store_true', dest='shops')
    parser.add_option('-d', '--destinations', action='store_true', dest='destinations')
    parser.add_option('-m', '--demands', action='store_true', dest='demands')
    parser.add_option('-a', '--all', action='store_true', dest='all')
    (args, _) = parser.parse_args()
    if args.locations is not None or args.all is not None:
        print('locations:', json.dumps(locations_hardcoded()))
    if args.time_windows is not None or args.all is not None:
        print('time_windows:', json.dumps(time_windows_hardcoded()))
    if args.shops is not None or args.all is not None:
        print('shops:', json.dumps(shops_hardcoded()))
    if args.destinations is not None or args.all is not None:
        print('destinations:', json.dumps(dest_hardcoded()))
    if args.demands is not None or args.all is not None:
        print('demands:', json.dumps(demands_hardcoded()))
