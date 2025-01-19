import os
import csv
# import datetime
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
user_check_in = os.getenv('USER_CHECK_IN')
user_check_out = os.getenv('USER_CHECK_OUT')
city_list = os.getenv('CITIES_LIST')
vehicle_parking_fee = os.getenv('VEHICLE_PARKING_FEES')
bill_file = os.getenv('BILL_FILE')
MAX_CAP = 20 # Maximum capacity of parking
ADMIN_PSW = 'adminadmin' # Password for Admin


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
    return datetime.now().strftime("%m-%d-%Y %H:%M:%S")

def show_vehicle_brand():
    with open(vehicle_parking_fee, mode='r', newline='') as file:
        reader = csv.reader(file)

        for row in reader:
            print(row[0], end=' ')
            print(row[1])

    case = int(input('Choose your best vehicle: '))

    match case:
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

def city_recognition(License_plate):
    city_holder = License_plate[-2:]

    with open(city_list, mode='r') as file:
        for line in file:
                parts = line.strip().split('-')
                if parts and city_holder in parts[0].split():
                    return parts[-1]

def fee(vehicle_name, start, end):
    
    start_date = datetime.strptime(start, "%m-%d-%Y %H:%M:%S")
    end_date = datetime.strptime(end, "%m-%d-%Y %H:%M:%S")
    hours = (end_date - start_date).total_seconds() / 3600  # Calculate the difference in hours
    # print(f'Difference is {hours:.2f} hours')

    with open(vehicle_parking_fee, 'r', newline='') as f:
        dict_reader = csv.DictReader(f)
        # hourly_fee = None
        for value in dict_reader:
            if value['Vehicle'] == vehicle_name:
                hourly_fee = value['Hourly Fee'] # The value would be string
                break

    # if hourly_fee is None:
    #     raise ValueError(f"Hourly fee not found for vehicle: {vehicle_name}")
    
    total_fee = round(hours * float(hourly_fee), 2)
    return total_fee

def check_in():
    try:
        with open(user_check_in, mode='r', newline='') as file:
            read = csv.DictReader(file)
            capacity = 0
            for _ in read:
                capacity += 1
        if capacity < MAX_CAP:
            with open(user_check_in, mode='a', newline='') as file:
                writer = csv.writer(file)
                headers = ['License plate number', 'vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time']
                file_op(user_check_in, headers)

                owner = input('Enter your full name: ')
                License_plate = input('Enter your License plate number: ')
                vehicle = show_vehicle_brand()
                brand_Name = input('Enter your vehicle model: ')
                city = city_recognition(License_plate)
                check_in_time = date()
                writer.writerow([License_plate, vehicle, brand_Name, owner, city, check_in_time])
                print('data saved successfully\n')
        else:
            print('Parking lot has reached the maximum capacity!\n')
    except Exception as err:
        print(f'Error: {err}')

def check_out():
    try:
        license_plate_to_remove = input('Enter the License Plate Number to check out: ')
        end_date = date()
        found_plate = False
        updated_rows = []

        with open(user_check_in, 'r', newline='') as read_file:
            check_in_records = csv.DictReader(read_file)
            for record in check_in_records:
                if record['License plate number'] == license_plate_to_remove:
                    vehicle_name = record['vehicle']
                    brand_name = record['Brand Name']
                    owner_name = record['Owner Name']
                    city = record['City']
                    Check_in_time = record['Check in Time']
                    found_plate = True
                else:
                    updated_rows.append(record)

        if not found_plate:
            raise ValueError(f"License plate {license_plate_to_remove} not found in check-in records!")
        # -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        with open(user_check_in, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=check_in_records.fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        print(f'User with License Plate {license_plate_to_remove} checked out.')
        headers = ['License plate number', 'vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time', 'Check out Time', 'Fee']
        file_op(user_check_out, headers)

        with open(user_check_out, 'a', newline='') as check_out_file:
            writer = csv.writer(check_out_file)
            tot_fee = fee(vehicle_name, Check_in_time, end_date)
            writer.writerow([
                license_plate_to_remove, vehicle_name, record.get('Brand Name'), record.get('Owner Name'),
                record.get('City'), Check_in_time, end_date, tot_fee
            ])

        generate_bill(license_plate_to_remove, vehicle_name, brand_name, owner_name, city, Check_in_time, end_date, tot_fee)
        # -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    except Exception as err:
        print(f'Error: {err}')

def generate_bill(license_plate, vehicle_name, brand_name, owner_name, city, check_in_time, check_out_time, fee):
    bill_content = f'''
    ================================
                Parking Bill
    ================================
    License Plate: {license_plate}
    Vehicle Name: {vehicle_name}
    Brand Name: {brand_name}
    Owner Name: {owner_name}
    City: {city}
    Check-In Time: {check_in_time}
    Check-Out Time: {check_out_time}
    Total Fee: ${fee}
    ================================
    '''
    
    with open(bill_file, 'w') as f:
        f.write(bill_content)
    
    # print(bill_content)
    os.system(f"notepad {bill_file}")  # To open the bill in Notepad

def runMatch():
    while True:
        try:
            num = int(input('0. To exit\n1. Enter as Admin\n2. Enter as user\n'))
            
            match num:
                case 0:
                    break
                case 1:
                    # Admin section
                    adm_pws = input("Enter Admin password: ")
                    if adm_pws == ADMIN_PSW:
                        # reporting()
                        print("Admin Section")
                    else:
                        print("Incorrect password!")
                case 2:
                    # User section
                    print('Welcome to Parking Lot!\n')
                    while True:
                        try:
                            user_num = int(input('1. Check in your car\n2. Check out your car\nPress 0 to exit\n'))
                            
                            match user_num:
                                case 0:
                                    print("Exiting user section.")
                                    break
                                case 1:
                                    check_in()
                                case 2:
                                    check_out()
                                case _:
                                    print("Invalid input. Please enter 1, 2, or 0.")
                        except ValueError:
                            print("Invalid input. Please enter a valid number.")
                case _:
                    print("Invalid input. Please enter 0 for Admin or 1 for User.\n")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# runMatch()
if __name__ == "__main__":
    runMatch()