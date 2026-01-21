#!/usr/bin/env python3
"""
Apple Health Data Processor
Extracts sleep and heart data from Apple Health export and generates a spreadsheet
"""

import xml.etree.ElementTree as ET
import zipfile
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import os
import sys


def extract_export_xml(zip_path):
    """Extract export.xml from the Apple Health export.zip file"""
    print(f"📦 Extracting {zip_path}...")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # The export.xml is in the apple_health_export folder
        xml_files = [f for f in zip_ref.namelist() if f.endswith('export.xml')]

        if not xml_files:
            raise ValueError("No export.xml found in the zip file")

        xml_path = xml_files[0]
        print(f"✓ Found {xml_path}")

        # Extract to temp location
        zip_ref.extract(xml_path)
        return xml_path


def parse_date(date_string):
    """Parse Apple Health date format"""
    # Format: 2024-12-21 23:45:30 -0800
    try:
        return datetime.strptime(date_string.split(' -')[0].split(' +')[0], '%Y-%m-%d %H:%M:%S')
    except:
        return None


def process_sleep_data(root, days_back=30):
    """Extract sleep data from the XML"""
    print("\n😴 Processing sleep data...")

    cutoff_date = datetime.now() - timedelta(days=days_back)
    sleep_sessions = []

    for record in root.findall('.//Record[@type="HKCategoryTypeIdentifierSleepAnalysis"]'):
        start_date = parse_date(record.get('startDate'))
        end_date = parse_date(record.get('endDate'))

        if not start_date or not end_date or start_date < cutoff_date:
            continue

        value = record.get('value')
        source = record.get('sourceName', 'Unknown')

        # Sleep values: HKCategoryValueSleepAnalysisInBed, HKCategoryValueSleepAnalysisAsleep,
        # HKCategoryValueSleepAnalysisAwake, HKCategoryValueSleepAnalysisCore,
        # HKCategoryValueSleepAnalysisDeep, HKCategoryValueSleepAnalysisREM

        duration_minutes = (end_date - start_date).total_seconds() / 60

        sleep_sessions.append({
            'date': start_date.date(),
            'start_time': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': round(duration_minutes, 2),
            'duration_hours': round(duration_minutes / 60, 2),
            'type': value.replace('HKCategoryValueSleepAnalysis', ''),
            'source': source
        })

    print(f"✓ Found {len(sleep_sessions)} sleep records")
    return sleep_sessions


def process_heart_rate_data(root, days_back=30):
    """Extract heart rate data from the XML"""
    print("\n❤️  Processing heart rate data...")

    cutoff_date = datetime.now() - timedelta(days=days_back)
    heart_rates = []

    for record in root.findall('.//Record[@type="HKQuantityTypeIdentifierHeartRate"]'):
        start_date = parse_date(record.get('startDate'))

        if not start_date or start_date < cutoff_date:
            continue

        value = float(record.get('value'))
        unit = record.get('unit')
        source = record.get('sourceName', 'Unknown')

        heart_rates.append({
            'datetime': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'date': start_date.date(),
            'heart_rate': round(value, 1),
            'unit': unit,
            'source': source
        })

    print(f"✓ Found {len(heart_rates)} heart rate measurements")
    return heart_rates


def process_resting_heart_rate(root, days_back=30):
    """Extract resting heart rate data"""
    print("\n💓 Processing resting heart rate data...")

    cutoff_date = datetime.now() - timedelta(days=days_back)
    resting_hrs = []

    for record in root.findall('.//Record[@type="HKQuantityTypeIdentifierRestingHeartRate"]'):
        start_date = parse_date(record.get('startDate'))

        if not start_date or start_date < cutoff_date:
            continue

        value = float(record.get('value'))
        unit = record.get('unit')
        source = record.get('sourceName', 'Unknown')

        resting_hrs.append({
            'date': start_date.date(),
            'datetime': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'resting_heart_rate': round(value, 1),
            'unit': unit,
            'source': source
        })

    print(f"✓ Found {len(resting_hrs)} resting heart rate measurements")
    return resting_hrs


def process_hrv_data(root, days_back=30):
    """Extract heart rate variability data"""
    print("\n💗 Processing HRV data...")

    cutoff_date = datetime.now() - timedelta(days=days_back)
    hrvs = []

    for record in root.findall('.//Record[@type="HKQuantityTypeIdentifierHeartRateVariabilitySDNN"]'):
        start_date = parse_date(record.get('startDate'))

        if not start_date or start_date < cutoff_date:
            continue

        value = float(record.get('value'))
        unit = record.get('unit')
        source = record.get('sourceName', 'Unknown')

        hrvs.append({
            'date': start_date.date(),
            'datetime': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'hrv_sdnn': round(value, 1),
            'unit': unit,
            'source': source
        })

    print(f"✓ Found {len(hrvs)} HRV measurements")
    return hrvs


def aggregate_daily_heart_data(heart_rates, resting_hrs, hrvs):
    """Aggregate heart data by day"""
    print("\n📊 Aggregating daily heart metrics...")

    daily_data = defaultdict(lambda: {
        'date': None,
        'hr_avg': None,
        'hr_min': None,
        'hr_max': None,
        'hr_count': 0,
        'resting_hr': None,
        'hrv': None
    })

    # Aggregate heart rates by day
    for hr in heart_rates:
        date = hr['date']
        if daily_data[date]['date'] is None:
            daily_data[date]['date'] = date
            daily_data[date]['hr_values'] = []

        daily_data[date]['hr_values'].append(hr['heart_rate'])

    # Calculate stats
    for date in daily_data:
        if 'hr_values' in daily_data[date] and daily_data[date]['hr_values']:
            values = daily_data[date]['hr_values']
            daily_data[date]['hr_avg'] = round(sum(values) / len(values), 1)
            daily_data[date]['hr_min'] = round(min(values), 1)
            daily_data[date]['hr_max'] = round(max(values), 1)
            daily_data[date]['hr_count'] = len(values)
            del daily_data[date]['hr_values']

    # Add resting heart rate
    for rhr in resting_hrs:
        date = rhr['date']
        if daily_data[date]['date'] is None:
            daily_data[date]['date'] = date
        daily_data[date]['resting_hr'] = rhr['resting_heart_rate']

    # Add HRV
    for hrv in hrvs:
        date = hrv['date']
        if daily_data[date]['date'] is None:
            daily_data[date]['date'] = date
        daily_data[date]['hrv'] = hrv['hrv_sdnn']

    return sorted(daily_data.values(), key=lambda x: x['date'] if x['date'] else datetime.now().date())


def aggregate_daily_sleep(sleep_sessions):
    """Aggregate sleep data by night"""
    print("\n📊 Aggregating nightly sleep data...")

    # Group by date (using the start date as the night identifier)
    daily_sleep = defaultdict(lambda: {
        'date': None,
        'total_in_bed_minutes': 0,
        'total_asleep_minutes': 0,
        'total_awake_minutes': 0,
        'core_sleep_minutes': 0,
        'deep_sleep_minutes': 0,
        'rem_sleep_minutes': 0,
        'bedtime': None,
        'wake_time': None
    })

    for session in sleep_sessions:
        # Use the date of when sleep started
        date = session['date']
        sleep_type = session['type']
        duration = session['duration_minutes']

        if daily_sleep[date]['date'] is None:
            daily_sleep[date]['date'] = date

        # Track earliest bedtime and latest wake time
        start_time = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(session['end_time'], '%Y-%m-%d %H:%M:%S')

        if daily_sleep[date]['bedtime'] is None or start_time < daily_sleep[date]['bedtime']:
            daily_sleep[date]['bedtime'] = start_time

        if daily_sleep[date]['wake_time'] is None or end_time > daily_sleep[date]['wake_time']:
            daily_sleep[date]['wake_time'] = end_time

        # Categorize sleep types
        if sleep_type == 'InBed':
            daily_sleep[date]['total_in_bed_minutes'] += duration
        elif sleep_type in ['Asleep', 'AsleepUnspecified']:
            daily_sleep[date]['total_asleep_minutes'] += duration
        elif sleep_type == 'Awake':
            daily_sleep[date]['total_awake_minutes'] += duration
        elif sleep_type in ['Core', 'AsleepCore']:
            daily_sleep[date]['core_sleep_minutes'] += duration
        elif sleep_type in ['Deep', 'AsleepDeep']:
            daily_sleep[date]['deep_sleep_minutes'] += duration
        elif sleep_type in ['REM', 'AsleepREM']:
            daily_sleep[date]['rem_sleep_minutes'] += duration

    # Format the data
    result = []
    for date_data in daily_sleep.values():
        result.append({
            'date': date_data['date'],
            'bedtime': date_data['bedtime'].strftime('%H:%M') if date_data['bedtime'] else '',
            'wake_time': date_data['wake_time'].strftime('%H:%M') if date_data['wake_time'] else '',
            'time_in_bed_hours': round(date_data['total_in_bed_minutes'] / 60, 2),
            'total_sleep_hours': round((date_data['total_asleep_minutes'] +
                                       date_data['core_sleep_minutes'] +
                                       date_data['deep_sleep_minutes'] +
                                       date_data['rem_sleep_minutes']) / 60, 2),
            'awake_minutes': round(date_data['total_awake_minutes'], 1),
            'core_sleep_hours': round(date_data['core_sleep_minutes'] / 60, 2),
            'deep_sleep_hours': round(date_data['deep_sleep_minutes'] / 60, 2),
            'rem_sleep_hours': round(date_data['rem_sleep_minutes'] / 60, 2)
        })

    return sorted(result, key=lambda x: x['date'])


def generate_spreadsheet(sleep_data, heart_data, output_file='health_data_export.csv'):
    """Generate a combined CSV spreadsheet"""
    print(f"\n📄 Generating spreadsheet: {output_file}")

    # Combine data by date
    all_dates = set()
    sleep_by_date = {s['date']: s for s in sleep_data}
    heart_by_date = {h['date']: h for h in heart_data}

    all_dates.update(sleep_by_date.keys())
    all_dates.update(heart_by_date.keys())

    # Create combined rows
    combined_data = []
    for date in sorted(all_dates):
        row = {'date': date}

        # Add sleep data
        if date in sleep_by_date:
            row.update({
                'bedtime': sleep_by_date[date]['bedtime'],
                'wake_time': sleep_by_date[date]['wake_time'],
                'time_in_bed_hours': sleep_by_date[date]['time_in_bed_hours'],
                'total_sleep_hours': sleep_by_date[date]['total_sleep_hours'],
                'awake_minutes': sleep_by_date[date]['awake_minutes'],
                'core_sleep_hours': sleep_by_date[date]['core_sleep_hours'],
                'deep_sleep_hours': sleep_by_date[date]['deep_sleep_hours'],
                'rem_sleep_hours': sleep_by_date[date]['rem_sleep_hours']
            })
        else:
            row.update({
                'bedtime': '', 'wake_time': '', 'time_in_bed_hours': '',
                'total_sleep_hours': '', 'awake_minutes': '', 'core_sleep_hours': '',
                'deep_sleep_hours': '', 'rem_sleep_hours': ''
            })

        # Add heart data
        if date in heart_by_date:
            row.update({
                'hr_avg': heart_by_date[date]['hr_avg'],
                'hr_min': heart_by_date[date]['hr_min'],
                'hr_max': heart_by_date[date]['hr_max'],
                'hr_measurements': heart_by_date[date]['hr_count'],
                'resting_hr': heart_by_date[date]['resting_hr'],
                'hrv_sdnn': heart_by_date[date]['hrv']
            })
        else:
            row.update({
                'hr_avg': '', 'hr_min': '', 'hr_max': '',
                'hr_measurements': '', 'resting_hr': '', 'hrv_sdnn': ''
            })

        combined_data.append(row)

    # Write to CSV
    fieldnames = [
        'date', 'bedtime', 'wake_time', 'time_in_bed_hours', 'total_sleep_hours',
        'awake_minutes', 'core_sleep_hours', 'deep_sleep_hours', 'rem_sleep_hours',
        'hr_avg', 'hr_min', 'hr_max', 'hr_measurements', 'resting_hr', 'hrv_sdnn'
    ]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_data)

    print(f"✓ Spreadsheet created with {len(combined_data)} days of data")
    return output_file


def print_summary(sleep_data, heart_data):
    """Print a summary of the data"""
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)

    if sleep_data:
        print("\n😴 SLEEP METRICS:")
        total_nights = len(sleep_data)
        avg_sleep = sum(s['total_sleep_hours'] for s in sleep_data) / total_nights
        avg_deep = sum(s['deep_sleep_hours'] for s in sleep_data if s['deep_sleep_hours'] > 0)
        deep_count = len([s for s in sleep_data if s['deep_sleep_hours'] > 0])
        avg_rem = sum(s['rem_sleep_hours'] for s in sleep_data if s['rem_sleep_hours'] > 0)
        rem_count = len([s for s in sleep_data if s['rem_sleep_hours'] > 0])

        print(f"  Total nights tracked: {total_nights}")
        print(f"  Average sleep: {avg_sleep:.2f} hours/night")
        if deep_count > 0:
            print(f"  Average deep sleep: {avg_deep/deep_count:.2f} hours/night")
        if rem_count > 0:
            print(f"  Average REM sleep: {avg_rem/rem_count:.2f} hours/night")

    if heart_data:
        print("\n❤️  HEART METRICS:")
        hr_values = [h['hr_avg'] for h in heart_data if h['hr_avg']]
        resting_values = [h['resting_hr'] for h in heart_data if h['resting_hr']]
        hrv_values = [h['hrv'] for h in heart_data if h['hrv']]

        if hr_values:
            print(f"  Average heart rate: {sum(hr_values)/len(hr_values):.1f} bpm")
        if resting_values:
            print(f"  Average resting HR: {sum(resting_values)/len(resting_values):.1f} bpm")
        if hrv_values:
            print(f"  Average HRV (SDNN): {sum(hrv_values)/len(hrv_values):.1f} ms")

    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Extract sleep and heart data from Apple Health export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 process_health_data.py export.zip
  python3 process_health_data.py export.zip --days 60 --output my_health_data.csv
  python3 process_health_data.py apple_health_export/export.xml --days 7
        """
    )

    parser.add_argument('input_file', help='Apple Health export.zip or export.xml file')
    parser.add_argument('--days', type=int, default=30, help='Number of days to look back (default: 30)')
    parser.add_argument('--output', default='health_data_export.csv', help='Output CSV file name')

    args = parser.parse_args()

    print("🍎 Apple Health Data Processor")
    print("="*60)

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: File not found: {args.input_file}")
        sys.exit(1)

    # Determine if we have a zip or xml file
    xml_file = args.input_file
    if args.input_file.endswith('.zip'):
        try:
            xml_file = extract_export_xml(args.input_file)
        except Exception as e:
            print(f"❌ Error extracting zip file: {e}")
            sys.exit(1)

    # Parse the XML
    print(f"\n📖 Parsing XML file...")
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        print("✓ XML parsed successfully")
    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
        sys.exit(1)

    # Process the data
    try:
        sleep_sessions = process_sleep_data(root, args.days)
        heart_rates = process_heart_rate_data(root, args.days)
        resting_hrs = process_resting_heart_rate(root, args.days)
        hrvs = process_hrv_data(root, args.days)

        # Aggregate data
        daily_sleep = aggregate_daily_sleep(sleep_sessions)
        daily_heart = aggregate_daily_heart_data(heart_rates, resting_hrs, hrvs)

        # Generate spreadsheet
        output_file = generate_spreadsheet(daily_sleep, daily_heart, args.output)

        # Print summary
        print_summary(daily_sleep, daily_heart)

        print(f"\n✅ Done! Your health data is in: {output_file}")
        print(f"📊 You can open it in Excel, Google Sheets, or any spreadsheet app")

    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup extracted XML if we extracted from zip
        if args.input_file.endswith('.zip') and os.path.exists(xml_file):
            import shutil
            dir_to_remove = os.path.dirname(xml_file)
            if os.path.exists(dir_to_remove) and 'apple_health_export' in dir_to_remove:
                shutil.rmtree(dir_to_remove)


if __name__ == '__main__':
    main()
