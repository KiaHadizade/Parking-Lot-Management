import os
import csv
import pandas as pd
from datetime import datetime, timedelta
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
        with open(user_check_in, mode='a', newline='') as file:
            writer = csv.writer(file)
            headers = ['License Plate', 'Vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time']
            file_op(user_check_in, headers)

            with open(user_check_in, mode='r', newline='') as file:
                read = csv.DictReader(file)
                capacity = 0
                for _ in read:
                    capacity += 1
            if capacity < MAX_CAP:
                owner = input('Enter your full name: ')
                License_plate = input('Enter your License Plate: ')
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
        license_plate_to_remove = input('Enter the License Plate to check out: ')
        end_date = date()
        found_plate = False
        updated_rows = []

        with open(user_check_in, 'r', newline='') as read_file:
            check_in_records = csv.DictReader(read_file)
            for record in check_in_records:
                if record['License Plate'] == license_plate_to_remove:
                    vehicle_name = record['Vehicle']
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
        headers = ['License Plate', 'Vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time', 'Check out Time', 'Fee']
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

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

def view_info():
    df = pd.read_csv(user_check_in)
    print(f'{df}\n')

def revenue_report():
    df = pd.read_csv(user_check_out)

    # Convert 'Check out Time' to datetime
    df['Check out Time'] = pd.to_datetime(df['Check out Time'])
    
    # Get today's date and the current week, month and year
    today = datetime.today()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_today - timedelta(days=today.weekday()) # Start of current week is Monday
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Filters for each time period, values are boolean
    filters = {
        "Today": (df['Check out Time'] >= start_of_today),
        "This Week": (df['Check out Time'] >= start_of_week),
        "This Month": (df['Check out Time'] >= start_of_month),
        "This Year": (df['Check out Time'] >= start_of_year),
    }
    
    # revenue for each period
    report = {period: df.loc[filter]['Fee'].sum() for period, filter in filters.items()}
    # Add the total revenue to the report
    report['Total Revenue'] = df['Fee'].sum()
    print(f'''
    Today: ${report['Today']:.2f}
    This Week: ${report['This Week']:.2f}
    This Month: ${report['This Month']:.2f}
    This Year: ${report['This Year']:.2f}
    Total Income: ${report['Total Revenue']:.2f}
    ''')

def reporting():
    # Display of vehicles and their count based on the type of vehicle
    df = pd.read_csv(user_check_in)
    print('Display of Parking Lot:\n', df)

    type_count = df.groupby('Vehicle').size().reset_index(name='Number of Vehicles')
    print('\nCount of any parked vehicle\n', type_count)

    # Breakdown based on today's vehicles and the last 7 days
    df['Check in Time'] = pd.to_datetime(df['Check in Time'])
    
    today = datetime.today()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_last_7_days = start_of_today - timedelta(days=7)
    
    filters = {
        "Today": (df['Check in Time'] >= start_of_today),
        "Last 7 Days": (df['Check in Time'] >= start_of_last_7_days)
    }
    
    reports = {period: df.loc[filter] for period, filter in filters.items()}
    for period, report in reports.items():
        print(f'\n{period}:\n', report)

    # Providing vehicle statistics based on the city of license plate registration (how many vehicles are from each city)
    city_count = df.groupby('City').size().reset_index(name='Number of Vehicles')
    print('\nCount of vehicle based on the city\n', city_count)

    # Providing statistics on vehicles with even and odd license plate
    even = df[df['License Plate'].apply(lambda x: int(x[-1]) % 2 == 0)]
    odd = df[df['License Plate'].apply(lambda x: int(x[-1]) % 2 != 0)]
    print(f'\nEven License Plate: \n{even}')
    print(f'\nOdd License Plate: \n{odd}\n')

def search():
    df = pd.read_csv(user_check_in)
    search = input('Enter a License Plate or vehicle type to search: ')
    for x in df.index:
        if not (df.loc[x, 'License Plate'] == search or df.loc[x, 'Vehicle'] == search):
            df.drop(x, inplace= True)
    if df.empty:
        print('Nothing founded!')
    else:
        print(f'\n{df}\n')

def RunMenu():
    # Main Menu
    while True:
        try:
            num = int(input('0. To exit\n1. Enter as Admin\n2. Enter as User\n'))
            
            match num:
                case 0:
                    break
                case 1:
                    # Admin Menu
                    adm_pws = input("Enter Password: ")
                    if adm_pws == ADMIN_PSW:
                        while True:
                            try:
                                adm_num = int(input('1. View Vehicles and Their Info\n2. Search Vehicle\n3. Reporting Info\nPress 0 to Exit\n'))
                                
                                match adm_num:
                                    case 0:
                                        print("Exiting Admin Menu.")
                                        break
                                    case 1:
                                        view_info()
                                    case 2:
                                        search()
                                    case 3:
                                        # Reporting
                                        try:
                                            Rpt_num = int(input('1. Parking Revenue Report\n2. Report On The Number Of Parked Vehicles\nPress 0 to Exit\n'))
                                            
                                            match Rpt_num:
                                                case 0:
                                                    break
                                                case 1:
                                                    revenue_report()
                                                case 2:
                                                    reporting()
                                                case _:
                                                    print("Invalid input. Please enter 1, 2 or 0.")
                                        except ValueError:
                                            print("Invalid input. Please enter a valid number.")
                                    case _:
                                        print("Invalid input. Please enter 1, 2, 3 or 0.")
                            except ValueError:
                                print("Invalid input. Please enter a valid number.")
                    else:
                        print("Incorrect password!")
                case 2:
                    # User Menu
                    print('Welcome to Parking Lot!\n')
                    while True:
                        try:
                            user_num = int(input('1. Check in your car\n2. Check out your car\nPress 0 to exit\n'))
                            
                            match user_num:
                                case 0:
                                    print("Exiting User Menu.")
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

# RunMenu()
if __name__ == "__main__":
    RunMenu()