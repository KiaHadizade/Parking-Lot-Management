import os
import csv
import datetime
from dotenv import load_dotenv

load_dotenv()
user_check_in = os.getenv('USER_CHECK_IN')
user_check_out = os.getenv('USER_CHECK_OUT')
city_list = os.getenv('CITIES_LIST')
vehicle_parking_fee = os.getenv('VEHICLE_PARKING_FEES')

print('Welcome to Parking Lot!')

def file_op(file_path, headers):
    try:
        # Check if file exists and has content
        file_exists = os.path.exists(file_path)
        is_empty = os.stat(file_path).st_size == 0 if file_exists else True

        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write headers only if the file is new or empty
            if is_empty:
                writer.writerow(headers)

    except Exception as err:
        print(f'Error: {err}')

def date():
    return datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")

def show_vehicle_brand():
    with open(vehicle_parking_fee, mode='r', newline='') as file:
        reader = csv.reader(file)

        for row in reader:
            print(row[0], end=' ')
            print(row[1])

    num = int(input('Choose your best vehicle: '))

    match num:
        case 1:
            return 'Car'
        case 2:
            return 'Motorcycle'
        case 3:
            return 'Bicycle'
        case 4:
            return 'Truck'
        case 5:
            return 'Bus'
        case 6:
            return 'Van'
        case 7:
            return 'Luxury Vehicle'
        case 8:
            return 'Electric Car'
        case 9:
            return 'Scooter'
        case _:
            print('blah')

def city_recognition():
    city_holder = License_plate[-2:]

    with open(city_list, mode='r') as file:
        for line in file:
                parts = line.strip().split('-')
                if parts and city_holder in parts[0].split():
                    return parts[-1]

def check_in():
    try:
        with open(user_check_in, mode='a', newline='') as file:
            writer = csv.writer(file)
            headers = ['License plate number', 'vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time']
            file_op(user_check_in, headers)

            global License_plate
            owner = input('Enter your full name: ')
            License_plate = input('Enter your License plate number: ')
            vehicle = show_vehicle_brand()
            brand_Name = input('Enter your vehicle model: ')
            city = city_recognition()
            check_in_time = date()

            writer.writerow([License_plate, vehicle, brand_Name, owner, city, check_in_time])

            print('data saved successfully\n')

            runMatch()
    except Exception as err:
        print(f'Error: {err}')

def check_out():
    try:
        license_plate_to_remove = input('Enter the License Plate Number to check out: ')
        
        with open(user_check_in, 'r', newline='') as inp:
            rows = list(csv.reader(inp))
        
        with open(user_check_in, 'w', newline='') as out:
            writer = csv.writer(out)
            for row in rows:
                if row[0] != license_plate_to_remove:
                    writer.writerow(row)
                else:
                    print(f'User with License Plate {license_plate_to_remove} checked out.')
                    headers = ['License plate number', 'vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time', 'Check out Time']
                    file_op(user_check_out, headers)
                    # need to append the records out of loop to prevent any bugs
                    # to do this, have to save the desired record into new variable
                    new_row = row

        with open(user_check_out, 'a', newline='') as check_out:
                    writer = csv.writer(check_out)
                    writer.writerow([*new_row, date()])
        
        runMatch()
    except Exception as err:
        print(f'Error: {err}')

def runMatch():
    while True:
        try:
            num = int(input('1. Check in your car\n2. Check out your car\nPress any number to exit\n'))
        except ValueError:
            # print("Please enter a valid integer.")
            continue

        match num:
            case 1:
                check_in()
            case 2:
                check_out()
            case _:
                return

runMatch()