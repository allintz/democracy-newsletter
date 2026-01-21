# Apple Health Data Export Tool

Automatically extract and analyze your Apple Health sleep and heart data.

## Quick Start

### Step 1: Export from iPhone

**Easiest Method:**
1. Open **Health app** on iPhone
2. Tap **profile picture** (top right)
3. Scroll down → **Export All Health Data**
4. Tap **Export**
5. Save the `export.zip` file

### Step 2: Transfer File

Transfer `export.zip` to this directory using:
- **AirDrop** to Mac
- **iCloud Drive** → Download to computer
- **Email** to yourself
- **USB cable** file transfer

### Step 3: Run the Script

```bash
python3 process_health_data.py export.zip
```

**That's it!** You'll get a file called `health_data_export.csv` with all your data.

## What You Get

The CSV spreadsheet includes:

**Sleep Metrics:**
- Bedtime and wake time
- Total sleep hours
- Time in bed
- Deep sleep, REM sleep, core sleep breakdown
- Awake time during night

**Heart Metrics:**
- Average heart rate (daily)
- Min/max heart rate
- Number of measurements
- Resting heart rate
- Heart rate variability (HRV SDNN)

## Advanced Options

### Different time periods

```bash
# Last 7 days
python3 process_health_data.py export.zip --days 7

# Last 3 months
python3 process_health_data.py export.zip --days 90
```

### Custom output filename

```bash
python3 process_health_data.py export.zip --output my_health_jan2026.csv
```

### Process already-extracted XML

```bash
python3 process_health_data.py apple_health_export/export.xml
```

## Troubleshooting

**"File not found" error:**
- Make sure you're in the right directory
- Check the filename (it might be `Export.zip` with capital E)
- Use the full path: `python3 process_health_data.py ~/Downloads/export.zip`

**No data in spreadsheet:**
- Check that you have Health data for the time period
- Try increasing days: `--days 60`
- Make sure Health sync is enabled on your iPhone

**Permission errors:**
- Make script executable: `chmod +x process_health_data.py`

## Privacy

- All processing happens **locally** on your computer
- No data is sent anywhere
- The script only reads the export file
- Your health data stays private

## Requirements

- Python 3.6 or higher (built into macOS/Linux)
- No additional packages needed - uses standard library only

## Need Help?

Check `APPLE_HEALTH_EXPORT_INSTRUCTIONS.md` for detailed instructions on:
- Creating iOS Shortcuts for automated exports
- Understanding Health data types
- Exporting specific data categories
