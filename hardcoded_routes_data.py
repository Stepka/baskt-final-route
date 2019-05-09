import json

import optparse

DEFAULT_TIME_WINDOW = ("09:00 AM", "10:00 PM")


# enter the time windows of all the clients here with the first one as the base time for all
def time_windows_hardcoded():
    time = [
        DEFAULT_TIME_WINDOW,   # departure from hub time
        ("04:00 PM", "06:00 PM"),
        ("03:00 PM", "04:00 PM"),
        DEFAULT_TIME_WINDOW,
        DEFAULT_TIME_WINDOW,
        DEFAULT_TIME_WINDOW,
        DEFAULT_TIME_WINDOW,
        ("09:30 AM", "10:30 AM"),
        # DEFAULT_TIME_WINDOW,
        # ("08:00 AM", "09:00 AM"),
        # ("10:00 AM", "11:00 AM"),
        # ("02:00 PM", "04:00 PM"),
        # ("12:00 PM", "02:00 PM"),
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # ("11:00 AM", "12:00 PM"),
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # ("01:00 PM", "02:00 PM"),
        # ("12:30 PM", "01:30 PM"),
        # DEFAULT_TIME_WINDOW,
        # ("01:15 PM", "02:15 PM"),
        # ("01:00 PM", "02:30 PM"),
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # DEFAULT_TIME_WINDOW,
        # ("02:00 PM", "04:00 PM"),
        # DEFAULT_TIME_WINDOW,
    ]

    return time


def locations_hardcoded():
    # Array of locations (lat, lng)
    locations = [
        (39.2908045, -76.66135799999999),  # warehouse, hub
        (39.3019488, -76.60290979999999),
        (39.3021398, -76.61649560000001),
        (39.3054756, -76.6211893),
        (39.2815397, -76.6549007),
        (39.353636, -76.63003789999999),
        (39.3019488, -76.60290979999999),
        (39.2938149, -76.6156373),
        # (39.2897469, -76.61571339999999),
        # (39.3355969, -76.6302991),
        # (39.2782983, -76.5783549),
        # (39.2806272, -76.5892465),
        # (39.3582352, -76.78333300000001),
        # (39.2782983, -76.5783549),
        # (39.2879203, -76.6155026),
        # (39.3761097, -76.60880010000001),
        # (39.2812367, -76.67296710000001),
        # (39.3362825, -76.61858079999999),
        # (39.2686942, -76.60015820000001),
        # (39.2840184, -76.59947919999999),
        # (39.281656, -76.6133813),
        # (39.2926324, -76.6155929),
        # (39.3285164, -76.6144377),
        # (39.355584, -76.5589226),
        # (39.3124808, -76.5962292),
        # (39.3180117, -76.57607159999999),
        # (39.279029, -76.61246100000001),
        # (39.3777234, -76.73108189999999),
        # (39.272708, -76.6736442),
        # (39.3551716, -76.64614449999999),
        # (39.3355969, -76.6302991),
        # (39.3281407, -76.59497089999999),
        # (39.312422299999994, -76.61839559999999),
        # (39.2895163, -76.6196826),
        # (39.2895163, -76.6196826),
        # (39.2895163, -76.6196826),
        # (39.2895163, -76.6196826),
        # (39.2895163, -76.6196826),
        # (39.2895163, -76.6196826),
        # (39.2895163, -76.6196826)
    ]

    # Array of locations (addresses)
    # locations = [
    #     ['232 n franklintown road baltimore md 21223'],   # warehouse, hub
    #     ['1000 E Eager St, Baltimore, MD 21202'],
    #     ['1030 N Charles St #302, Baltimore, MD 21201'],
    #     ['1111 Park Ave #109, Baltimore, MD 21201'],
    #     ['2429 Frederick Ave, Baltimore, MD 21223'],
    #     ['600 Wyndhurst Ave Suite 270, Baltimore, MD 21210'],
    #     ['1000 E Eager St, Baltimore, MD 21202'],
    #     ['338 N Charles St, Baltimore, MD 21201'],
    #     ['2 N Charles St Suite 130, Baltimore, MD 21201'],
    #     ['711 W 40th St #215, Baltimore, MD 21211'],
    #     ['2700 Lighthouse Point E #210, Baltimore, MD 21224'],
    #     ['949 Fell St Suite A, Baltimore, MD 21231'],
    #     ['5415 Old Court Rd Suite S01, Randallstown, MD 21133'],
    #     ['2700 Lighthouse Point E #210, Baltimore, MD 21224'],
    #     ['36 S Charles St #2202, Baltimore, MD 21201'],
    #     ['6601 York Rd, Baltimore, MD 21212'],
    #     ['3322 Frederick Ave, Baltimore, MD 21229'],
    #     ['3900 N Charles St Ste 112, Baltimore, MD 21218'],
    #     ['1712 Whetstone Way, Baltimore, MD 21230'],
    #     ['1001 Fleet St # R, Baltimore, MD 21202'],
    #     ['600 Light St, Baltimore, MD 21230'],
    #     ['300 N Charles St Suite D, Baltimore, MD 21201'],
    #     ['200 E 33rd St, Baltimore, MD 21218'],
    #     ['5810 Harford Rd, Baltimore, MD 21214'],
    #     ['1900 N Broadway, Baltimore, MD 21213'],
    #     ['2401 Belair Rd Suite 104, Baltimore, MD 21213'],
    #     ['835 Light St, Baltimore, MD 21230'],
    #     ['4000 Old Court Rd # 302, Pikesville, MD 21208'],
    #     ['3407 Wilkens Ave #205, Baltimore, MD 21229'],
    #     ['2 Village Square Ste 250, Baltimore, MD 21210'],
    #     ['711 W 40th St Ste 215, Baltimore, MD 21211'],
    #     ['1501 E 33rd St, Baltimore, MD 21218']
    # ]

    return locations


def shops_hardcoded():
    shops = [
        {
            "shopId": "24ce6075-394d-4b78-845d-48b58736d934",
            "latitude": 39.3054756,
            "longitude": -76.6211893
        }
    ]

    return shops


def cold_deliveries_hardcoded():
    # destinations = [6, 7, 11, 12, 17, 21, 25, 30]
    destinations = [6, 7]
    # destinations = []
    return destinations


def order_ids_hardcoded():
    order_ids = [
        "",
        "order 2",
        "order 3",
        "order 4",
        "order 5",
        "order 6",
        "order 7",
        "order 8"
    ]
    return order_ids


def max_vehicles_hardcoded():
    return 20


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="")
    parser.add_option('-l', '--locations', action='store_true', dest='locations')
    parser.add_option('-t', '--time_windows', action='store_true', dest='time_windows')
    parser.add_option('-s', '--shops', action='store_true', dest='shops')
    parser.add_option('-d', '--destinations', action='store_true', dest='destinations')
    parser.add_option('-m', '--demands', action='store_true', dest='demands')
    parser.add_option('-a', '--all', action='store_true', dest='all')
    (args, _) = parser.parse_args()
    # if args.locations is not None or args.all is not None:
    #     print('locations:', json.dumps(locations_hardcoded()))
    # if args.time_windows is not None or args.all is not None:
    #     print('time_windows:', json.dumps(time_windows_hardcoded()))
    # if args.shops is not None or args.all is not None:
    #     print('shops:', json.dumps(shops_hardcoded()))
    # if args.destinations is not None or args.all is not None:
    #     print('destinations:', json.dumps(cold_deliveries_hardcoded()))
    # if args.demands is not None or args.all is not None:
    #     print('demands:', json.dumps(demands_hardcoded()))

    print(json.dumps({
        'locations': locations_hardcoded(),
        'time_windows': time_windows_hardcoded(),
        'shops': shops_hardcoded(),
        'cold_deliveries': cold_deliveries_hardcoded()
    }))
