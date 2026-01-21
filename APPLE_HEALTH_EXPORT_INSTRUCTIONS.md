# Apple Health Data Export Instructions

## Option 1: iOS Shortcut (Automated)

### Creating the Shortcut

1. **Open the Shortcuts app** on your iPhone

2. **Tap the "+" button** (top right) to create a new shortcut

3. **Add actions in this exact order:**

   #### Action 1: Get Sleep Data
   - Tap "Add Action"
   - Search for "Find Health Samples"
   - Configure:
     - **Type:** Sleep Analysis
     - **Sort by:** Start Date (Newest First)
     - **Limit:** Toggle OFF (to get all)
     - **Start Date:** Select "Relative to Current Date" → "Last 30 Days"
     - **End Date:** Current Date

   #### Action 2: Save Sleep Data
   - Add "Set Variable" action
   - Name it: **Sleep Data**

   #### Action 3: Get Heart Rate Data
   - Add another "Find Health Samples"
   - Configure:
     - **Type:** Heart Rate
     - **Sort by:** Start Date (Newest First)
     - **Limit:** Toggle OFF
     - **Start Date:** Last 30 Days
     - **End Date:** Current Date

   #### Action 4: Save Heart Rate
   - Add "Set Variable" action
   - Name it: **Heart Rate Data**

   #### Action 5: Get Resting Heart Rate
   - Add another "Find Health Samples"
   - Configure:
     - **Type:** Resting Heart Rate
     - **Sort by:** Start Date (Newest First)
     - **Limit:** Toggle OFF
     - **Start Date:** Last 30 Days
     - **End Date:** Current Date

   #### Action 6: Save Resting Heart Rate
   - Add "Set Variable" action
   - Name it: **Resting HR Data**

   #### Action 7: Get Heart Rate Variability
   - Add another "Find Health Samples"
   - Configure:
     - **Type:** Heart Rate Variability
     - **Sort by:** Start Date (Newest First)
     - **Limit:** Toggle OFF
     - **Start Date:** Last 30 Days
     - **End Date:** Current Date

   #### Action 8: Combine All Data
   - Add "Text" action
   - Type the following structure:
     ```
     === SLEEP DATA ===
     Sleep Data (the variable)

     === HEART RATE DATA ===
     Heart Rate Data (the variable)

     === RESTING HEART RATE ===
     Resting HR Data (the variable)

     === HRV DATA ===
     Health Samples (this will be the HRV from step 7)
     ```

   #### Action 9: Save to File
   - Add "Save File" action
   - Configure:
     - **File Name:** health_export.txt
     - **Destination:** iCloud Drive or On My iPhone
     - **Ask Before Running:** Toggle ON (so you can choose location)

4. **Name your shortcut:** "Export Health Data to File"

5. **Run the shortcut** - it will ask for Health permissions on first run

6. **Transfer the file** to your computer and upload it here

---

## Option 2: Full Health Export (Manual - More Complete)

### Step-by-Step

1. **Open the Health app** on your iPhone

2. **Tap your profile picture** (top right corner)

3. **Scroll down** and tap **"Export All Health Data"**

4. **Tap "Export"** to confirm
   - This creates a file called `export.zip`
   - It contains ALL your Health data in XML format

5. **Share/Save the file:**
   - Tap the share icon
   - Save to **Files** app → iCloud Drive
   - Or **AirDrop** to your Mac
   - Or email it to yourself

6. **Upload the `export.zip` file** to this directory

---

## After You Have the File

Once you've uploaded the file here, run:

```bash
python3 process_health_data.py <your_file>
```

This will:
- Parse your sleep data (duration, bedtime, wake time, sleep stages)
- Extract heart rate metrics (average, min, max, resting HR, HRV)
- Generate a CSV spreadsheet: `health_data_export.csv`
- Create a summary report

---

## Troubleshooting

**Shortcut asks for permissions:**
- Tap "Allow" for each Health data type
- These are read-only permissions

**Can't find "Find Health Samples":**
- Make sure you're searching in the Actions tab
- Try scrolling through the Health category

**Export.zip is too large:**
- That's normal! Full exports can be 50-500MB
- Upload via your preferred method (iCloud, file transfer, etc.)

**Need help?**
- Let me know which method you're using
- Share any error messages you see
