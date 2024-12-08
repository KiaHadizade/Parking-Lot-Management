import os
import csv
import datetime
from dotenv import load_dotenv

load_dotenv()

file_path = os.getenv('USER_DATA')
file_path_vehicle = os.getenv('VEHICLE_PARKING_FEES')
headers = ['License plate number', 'vehicle', 'Brand Name', 'Owner Name', 'Entering date']
print('Welcome to Parking Lot!')



def print_vehicle():
    with open(file_path_vehicle, mode='r', newline='') as file:
        reader = csv.reader(file)

        for row in reader:
            print(row[0], end=' ')
            print(row[1])

    num = int(input('Choose your best vehicle: '))

    match num:
        case 1:
            return 'car'
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

    


def giv_info():
    try:
        # Check if file exists and has content
        file_exists = os.path.exists(file_path)
        is_empty = os.stat(file_path).st_size == 0 if file_exists else True

        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write headers only if the file is new or empty
            if is_empty:
                writer.writerow(headers)


            while True:
                License_plate = input('Enter your License plate number: ')
                if License_plate.lower() == 'exit':
                    break
                vehicle = print_vehicle()
                brand_Name = input('Enter your vehicle model: ')
                owner = input('Enter your full name: ')
                date_rn = datetime.datetime.now()
                date = date_rn.strftime("%Y-%m-%d %H:%M:%S")

                writer.writerow([License_plate, vehicle, brand_Name, owner, date])

                print('data saved successfully')
                print("Type 'exit' if you done")

            runMatch()
    except Exception as err:
        print(f'Error: {err}')


def runMatch():
    num = int(input('1. Parking your car\n2. Taking your car\n'))

    match num:
        case 1:
            giv_info()
        case 2:
            print('two')
        case _:
            print('blah')

runMatch()
# print_vehicle()