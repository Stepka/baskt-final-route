import final_route as fr
import hardcoded_routes_data as hardcoded


if __name__ == '__main__':
    print("create data model")

    # debug, hardcoded values
    locations = hardcoded.locations_hardcoded()
    time_windows = hardcoded.time_windows_hardcoded()
    shops = hardcoded.shops_hardcoded()
    cold_deliveries = hardcoded.cold_deliveries_hardcoded()
    order_ids = hardcoded.order_ids_hardcoded()
    num_vehicles = 4

    result = fr.create_data_model(locations, time_windows, order_ids, shops, cold_deliveries, num_vehicles)
    # result = create_data_model_d()
    if not result.successful:
        print(result)
    else:
        data = result.body
        print(data)
        result = fr.calculate_routes(data)
        print(result.body)
