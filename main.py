import os
import csv
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env file
user_check_in = os.getenv('USER_CHECK_IN')
user_check_out = os.getenv('USER_CHECK_OUT')
city_list = os.getenv('CITIES_LIST')
vehicle_parking_fee = os.getenv('VEHICLE_PARKING_FEES')
bill_file = os.getenv('BILL_FILE')
MAX_CAP = 20 # Maximum capacity of parking
ADMIN_PSW = 'adminadmin' # Password for Admin

# User section functions
def setup_file(file_path, headers):
    try:
        # Ensure the CSV file exists and has the required headers
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
    except Exception as err:
        print(f'Error: {err}')

def get_date(format="%m-%d-%Y %H:%M:%S"):
    return datetime.now().strftime(format)

def show_vehicle_brand():
    # Display vehicle types and get user input
    vehicle_options = {}
    with open(vehicle_parking_fee, mode='r', newline='') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            print(f"{row[0]} {row[1]}")
            vehicle_options[i] = row[1]

    try:
        choice = int(input("Choose your vehicle type: "))
        return vehicle_options.get(choice, "Unknown Vehicle")
    except ValueError:
        print("Invalid input. Please choose a number.")
        return None

def city_recognition(License_plate):
    # Determine city based on license plate.
    city_holder = License_plate[-2:]
    with open(city_list, mode='r') as file:
        for line in file:
                parts = line.strip().split('-')
                if city_holder in parts[0].split():
                    return parts[-1]
    return "Unknown City"

def fee(vehicle_name, start, end):
    # Calculate parking fee based on the vehicle type and parking duration
    try:
        start_date = datetime.strptime(start, "%m-%d-%Y %H:%M:%S")
        end_date = datetime.strptime(end, "%m-%d-%Y %H:%M:%S")
        hours = (end_date - start_date).total_seconds() / 3600  # Calculate the difference in hours
        # print(f'Difference is {hours:.2f} hours')

        with open(vehicle_parking_fee, 'r', newline='') as f:
            dict_reader = csv.DictReader(f)
            for value in dict_reader:
                if value['Vehicle'] == vehicle_name:
                    return round(hours * float(value['Hourly Fee']), 2)
            else:
                raise ValueError(f"No hourly fee found for vehicle type: {vehicle_name}")
    except Exception as err:
        print(f"Error calculating fee: {err}")
        return 0

def check_in():
    # Check in a vehicle and record its details
    try:
        setup_file(user_check_in, ['License Plate', 'Vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time'])
        df = pd.read_csv(user_check_in)

        with open(user_check_in, mode='a', newline='') as file:
            writer = csv.writer(file)
            if len(df) < MAX_CAP:
                owner = input('Enter your full name: ')
                License_plate = input('Enter the License Plate: ')
                vehicle = show_vehicle_brand()
                brand_Name = input('Enter the vehicle brand: ')
                city = city_recognition(License_plate)
                check_in_time = get_date()
                writer.writerow([License_plate, vehicle, brand_Name, owner, city, check_in_time])
                print(f'\nVehicle with license plate "{License_plate}" checked in successfully\n')
            else:
                print('Parking lot has reached its maximum capacity!\nWait for someone to check out, then try again.\n')
    except Exception as err:
        print(f'Error: {err}')

def check_out():
    # Check out a vehicle and calculate the fee
    try:
        license_plate_to_remove = input('Enter the License Plate to check out: ')
        found_plate = False
        updated_rows = []

        with open(user_check_in, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for record in reader:
                if record['License Plate'] == license_plate_to_remove:
                    found_plate = True
                    vehicle = record['Vehicle']
                    brand = record['Brand Name']
                    owner = record['Owner Name']
                    city = record['City']
                    Check_in_time = record['Check in Time']
                else:
                    updated_rows.append(record)
        if not found_plate:
            raise ValueError(f'Vehicle with license plate "{license_plate_to_remove}" not found!')

        with open(user_check_in, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        end_date = get_date()
        tot_fee = fee(vehicle, Check_in_time, end_date)

        setup_file(user_check_out, ['License Plate', 'Vehicle', 'Brand Name', 'Owner Name', 'City', 'Check in Time', 'Check out Time', 'Fee'])

        with open(user_check_out, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([license_plate_to_remove, vehicle, brand, owner, city, Check_in_time, end_date, tot_fee])

        generate_bill(license_plate_to_remove, vehicle, brand, owner, city, Check_in_time, end_date, tot_fee)
        print(f'Vehicle with License Plate {license_plate_to_remove} checked out.')
    except Exception as err:
        print(f'Error: {err}')

def generate_bill(license_plate, vehicle, brand, owner, city, check_in_time, check_out_time, fee):
    # Generate a parking bill
    bill_content = f'''
    ================================
                Parking Bill
    ================================
    License Plate: {license_plate}
    Vehicle: {vehicle}
    Brand: {brand}
    Owner: {owner}
    City: {city}
    Check-In Time: {check_in_time}
    Check-Out Time: {check_out_time}
    Total Fee: ${fee}
    ================================
    '''
    with open(bill_file, 'w') as file:
        file.write(bill_content)
    os.system(f"notepad {bill_file}") # To open the bill in Notepad

# Admin section functions
def view_info():
    # View all checked-in vehicle information
    try:
        df = pd.read_csv(user_check_in)
        print(f'{df}\n')
    except Exception as err:
        print(f'Error: {err}')

def revenue_report():
    # Generate revenue report
    try:
        df = pd.read_csv(user_check_out)
        df['Check out Time'] = pd.to_datetime(df['Check out Time']) # Convert 'Check out Time' to datetime
        
        # Get today's date, week, month and year
        today = datetime.today()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_today - timedelta(days=today.weekday()) # Start of current week is Monday
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Filters for each period, values are boolean
        filters = {
            "Today": (df['Check out Time'] >= start_of_today),
            "This Week": (df['Check out Time'] >= start_of_week),
            "This Month": (df['Check out Time'] >= start_of_month),
            "This Year": (df['Check out Time'] >= start_of_year),
        }
        
        report = {period: df.loc[filter]['Fee'].sum() for period, filter in filters.items()} # Calculate revenue for each period
        report['Total Revenue'] = df['Fee'].sum() # Add the total revenue to the report

        print('\n'.join([f'{period}: ${amount:.2f}' for period, amount in report.items()]))
    except Exception as err:
        print(f'Error: {err}')

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
        if report.empty:
            print(f'\n{period}: No check-in for today!')
        else:
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
            choice = int(input('0. Exit\n1. Enter as Admin\n2. Enter as User\nChoose an option: '))
            match choice:
                case 0:
                    break
                case 1:
                    # Admin Menu
                    if input("Enter Password: ") == ADMIN_PSW:
                        while True:
                            try:
                                adm_choice = int(input('0. Back\n1. View Vehicles and Their Info\n2. Search Vehicle\n3. Reporting Info\nChoose an option: '))
                                match adm_choice:
                                    case 0:
                                        break
                                    case 1:
                                        view_info()
                                    case 2:
                                        search()
                                    case 3:
                                        try:
                                            Rpt_choice = int(input('0. Back\n1. Parking Revenue Report\n2. Report On The Number Of Parked Vehicles\nChoose an option: '))
                                            match Rpt_choice:
                                                case 0:
                                                    break
                                                case 1:
                                                    revenue_report()
                                                case 2:
                                                    reporting()
                                                case _:
                                                    print("Invalid input. Please enter 1, 2 or 0 to exit.")
                                        except ValueError:
                                            print("Invalid option. Please enter a valid number.")
                                    case _:
                                        print("Invalid input. Please enter 1, 2, 3 or 0 to exit.")
                            except ValueError:
                                print("Invalid option. Please enter a valid number.")
                    else:
                        print("Incorrect password!")
                case 2:
                    # User Menu
                    print('Welcome to Parking Lot!\n')
                    while True:
                        try:
                            user_choice = int(input('0. Back\n1. Check in\n2. Check out\nChoose an option: '))
                            match user_choice:
                                case 0:
                                    break
                                case 1:
                                    check_in()
                                case 2:
                                    check_out()
                                case _:
                                    print("Invalid input. Please enter 1, 2, or 0 to exit.")
                        except ValueError:
                            print("Invalid option. Please enter a valid number.")
                case _:
                    print("Invalid input. Please enter 1 for Admin or 2 for User or 0 to exit.\n")
        except ValueError:
            print("Invalid option. Please enter a valid number.")

if __name__ == "__main__":
    RunMenu()