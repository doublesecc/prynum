import argparse
import json
import os
from datetime import datetime
import pytz
import re
import pandas as pd
from tabulate import tabulate

# Timezone mapping for the conversions
TIMEZONE_MAP = {
    'est': 'America/New_York',
    'edt': 'America/New_York',
    'cst': 'America/Chicago',
    'cdt': 'America/Chicago',
    'mst': 'America/Denver',
    'mdt': 'America/Denver',
    'pst': 'America/Los_Angeles',
    'pdt': 'America/Los_Angeles',
    'gmt': 'Etc/GMT',
    'bst': 'Europe/London'
}

def parse_number(number):
    """Normalize and extract the area code from the phone number."""
    normalized_number = re.sub(r'\D', '', number)
    if normalized_number.startswith('1') and len(normalized_number) > 1:
        # US numbers start with 1, so skip the first digit
        return normalized_number[1:4]
    return normalized_number[:3]

def load_area_codes(file_path):
    """Load area codes data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_local_time(timezone_str):
    """Get the current time in a given timezone."""
    tz = pytz.timezone(timezone_str)
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def convert_time(local_time, from_tz_str, to_tz_str):
    """Convert local time from one timezone to another, handling daylight saving time."""
    from_tz = pytz.timezone(from_tz_str)
    to_tz = pytz.timezone(to_tz_str)
    
    # Parse the local time as naive datetime
    naive_local_dt = datetime.strptime(local_time, '%Y-%m-%d %H:%M:%S')
    
    try:
        # Localize the naive datetime to the source timezone
        local_dt = from_tz.localize(naive_local_dt, is_dst=None)
    except pytz.NonExistentTimeError:
        # Handle cases where the time is not in DST
        local_dt = from_tz.localize(naive_local_dt, is_dst=False)
    except pytz.AmbiguousTimeError:
        # Handle cases where the time is ambiguous (e.g., during DST transition)
        local_dt = from_tz.localize(naive_local_dt, is_dst=True)
    
    # Convert to the target timezone
    target_time = local_dt.astimezone(to_tz)
    
    return target_time.strftime('%Y-%m-%d %H:%M:%S')

def get_corrected_timezone(tz_input):
    """Get the corrected timezone considering DST."""
    tz_mapping = {
        'gmt': 'Etc/GMT',
        'bst': 'Europe/London'
    }
    if tz_input.lower() in TIMEZONE_MAP:
        timezone_str = TIMEZONE_MAP[tz_input.lower()]
        now = datetime.now(pytz.timezone(timezone_str))
        if tz_input.lower() == 'gmt':
            return 'Europe/London' if now.dst() else 'Etc/GMT'
        return timezone_str
    return tz_input

def extract_numbers_from_txt(file_path):
    """Extract phone numbers from a TXT file where each number is on a new line."""
    phone_numbers = []
    with open(file_path, 'r') as file:
        for line in file:
            # Normalize by removing non-digit characters
            numbers = re.sub(r'[^\d+]', '', line.strip()).split(',')
            phone_numbers.extend(numbers)
    return [num for num in phone_numbers if re.search(r'\+?\d{10,15}', num)]

def extract_numbers_from_csv(file_path):
    """Extract phone numbers from a CSV file where numbers may be comma-separated in a single cell or multiple cells."""
    phone_numbers = []
    df = pd.read_csv(file_path, header=None)
    for _, row in df.iterrows():
        for cell in row:
            # Normalize by removing non-digit characters
            numbers = re.sub(r'[^\d+]', '', str(cell)).split(',')
            phone_numbers.extend(numbers)
    return [num for num in phone_numbers if re.search(r'\+?\d{10,15}', num)]

def extract_numbers_from_xlsx(file_path):
    """Extract phone numbers from an XLSX file."""
    df = pd.read_excel(file_path)
    phone_numbers = []
    for column in df.columns:
        phone_numbers.extend(df[column].dropna().astype(str).tolist())
    return [num for num in phone_numbers if re.search(r'\+?\d{10,15}', num)]

def print_table(results, convert_label):
    """Print the results in a tabular format."""
    headers = ["Number", "City", "Timezone", "Current Time", "GMT Offset"]
    if convert_label:
        headers.append(f"Current Time for {convert_label}")
    
    table = []
    for result in results:
        row = [result['number'], result['city'], result['short_tz'], result['local_time'], result['gmt_offset']]
        if convert_label:
            row.append(result.get('converted_time', ''))
        table.append(row)
    
    return tabulate(table, headers=headers, tablefmt='grid')

def print_line_by_line(results, convert_label):
    """Print the results line by line."""
    lines = []
    for result in results:
        line = f"Number: {result['number']}, City: {result['city']}, Time: {result['local_time']}, Timezone: {result['short_tz']}, GMT Offset: {result['gmt_offset']}"
        if convert_label:
            line += f", Time for {convert_label}: {result.get('converted_time', '')}"
        lines.append(line)
    return '\n'.join(lines)

def print_default(results, convert_label):
    """Print the results in the default format."""
    lines = []
    for result in results:
        line = (f"----------------------------------------\n"
                f"Number: {result['number']}\n"
                f"City: {result['city']}\n"
                f"Timezone: {result['short_tz']} (GMT{result['gmt_offset']})\n"
                f"Current Time: {result['local_time']}")
        if convert_label:
            line += f"\nTime for {convert_label}: {result.get('converted_time', '')}"
        line += f"\n----------------------------------------"
        lines.append(line)
    return '\n'.join(lines)

def print_banner():
    """Print an ASCII banner."""
    banner = """
   _ (`-.  _  .-')                    .-') _             _   .-')    
  ( (OO  )( \( -O )                  ( OO ) )           ( '.( OO )_  
 _.`     \ ,------.   ,--.   ,--.,--./ ,--,' ,--. ,--.   ,--.   ,--.)
(__...--'' |   /`. '   \  `.'  / |   \ |  |\ |  | |  |   |   `.'   | 
 |  /  | | |  /  | | .-')     /  |    \|  | )|  | | .-') |         | 
 |  |_.' | |  |_.' |(OO  \   /   |  .     |/ |  |_|( OO )|  |'.'|  | 
 |  .___.' |  .  '.' |   /  /\_  |  |\    |  |  | | `-' /|  |   |  | 
 |  |      |  |\  \  `-./  /.__) |  | \   | ('  '-'(_.-' |  |   |  | 
 `--'      `--' '--'   `--'      `--'  `--'   `-----'    `--'   `--' 
    Phone Number Prying Tool         
    """
    print(banner)

def write_to_file(data, file_path):
    """Write the output data to a file."""
    with open(file_path, 'w') as f:
        f.write(data)

def main():
    parser = argparse.ArgumentParser(description="Process US phone numbers.")
    parser.add_argument('-n', '--numbers', nargs='*', help='List of phone numbers.')
    parser.add_argument('-f', '--file', type=str, help='File containing phone numbers (TXT, CSV, XLSX).')
    parser.add_argument('-t', '--table', action='store_true', help='Print the data in a table format.')
    parser.add_argument('-l', '--line', action='store_true', help='Print the data line by line.')
    parser.add_argument('-o', '--output', type=str, help='File to write the output data to.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print the data to stdout and to a file.')
    parser.add_argument('-s', '--sort', type=str, choices=['city', 'local_time'], help='Sort the output based on the specified column.')
    parser.add_argument('-c', '--convert', type=str, choices=['est', 'edt', 'cst', 'cdt', 'mst', 'mdt', 'pst', 'pdt', 'gmt', 'bst'], help='Convert local time to target time zone (e.g., "bst" for British Summer Time, "edt" for Eastern Daylight Time).')
    parser.add_argument('--no-banner', action='store_true', help='Disable the ASCII banner.')
    args = parser.parse_args()

    if args.numbers is None and args.file is None:
        parser.error("No input provided. Use -n for numbers or -f for file input.")
    
    # Load area codes from local file
    area_codes_file = './definitions/area_codes.json'
    if not os.path.isfile(area_codes_file):
        print(f"Error: The file {area_codes_file} does not exist.")
        return

    area_codes = load_area_codes(area_codes_file)['US']

    phone_numbers = []
    if args.file:
        file_ext = os.path.splitext(args.file)[1].lower()
        if file_ext == '.txt':
            phone_numbers = extract_numbers_from_txt(args.file)
        elif file_ext == '.csv':
            phone_numbers = extract_numbers_from_csv(args.file)
        elif file_ext == '.xlsx':
            phone_numbers = extract_numbers_from_xlsx(args.file)
        else:
            print(f"Error: Unsupported file format {file_ext}.")
            return
    if args.numbers:
        phone_numbers.extend(args.numbers)

    results = []
    for number in phone_numbers:
        area_code = parse_number(number)
        if area_code in area_codes:
            data = area_codes[area_code]
            city = data['city']
            timezone_str = data['timezone']
            short_tz = data['short']
            gmt_offset = data['gmt_offset']
            local_time = get_local_time(timezone_str)
            
            result = {
                'number': number,
                'city': city,
                'short_tz': short_tz,
                'gmt_offset': gmt_offset,
                'local_time': local_time
            }
            
            if args.convert:
                corrected_tz_str = get_corrected_timezone(args.convert)
                target_tz_str = TIMEZONE_MAP.get(args.convert, corrected_tz_str)
                if target_tz_str:
                    converted_time = convert_time(local_time, timezone_str, target_tz_str)
                    result['converted_time'] = converted_time
                    result['convert_label'] = args.convert.upper()
            
            results.append(result)
        else:
            results.append({
                'number': number,
                'city': 'Error: Area code not found',
                'short_tz': '',
                'gmt_offset': '',
                'local_time': '',
                'converted_time': '',
                'convert_label': ''
            })

    # Remove duplicates
    results = [dict(t) for t in {tuple(d.items()) for d in results}]

    # Sort results if -s argument is provided
    if args.sort:
        if args.sort == 'city':
            results.sort(key=lambda x: x['city'])
        elif args.sort == 'local_time':
            results.sort(key=lambda x: x['local_time'])

    output_data = ''
    convert_label = args.convert.upper() if args.convert else ''

    if args.table:
        output_data = print_table(results, convert_label)
    elif args.line:
        output_data = print_line_by_line(results, convert_label)
    else:
        output_data = print_default(results, convert_label)
    
    if not args.no_banner:
        print_banner()
    
    if args.output:
        write_to_file(output_data, args.output)
        print(f"Output written to: {os.path.abspath(args.output)}")  # Print the file path
        if args.verbose:
            print(output_data)
    else:
        print(output_data)
        if args.verbose:
            write_to_file(output_data, 'output.txt')

if __name__ == '__main__':
    main()
