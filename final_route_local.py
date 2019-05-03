import final_route as fr
import hardcoded_routes_data as hardcoded


if __name__ == '__main__':
    print("create data model")

    # debug, hardcoded values
    locations = hardcoded.locations_hardcoded()
    time_windows = hardcoded.time_windows_hardcoded()
    shops = hardcoded.shops_hardcoded()
    destinations = hardcoded.dest_hardcoded()
    demands = hardcoded.demands_hardcoded()
    num_vehicles = 4

    result = fr.create_data_model(locations, time_windows, shops, destinations, demands, num_vehicles)
    # result = create_data_model_d()
    if not result.successful:
        print(result)
    else:
        data = result.body
        fr.calculate_routes(data)
