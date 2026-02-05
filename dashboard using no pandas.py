import streamlit as st
import xlwings as xw
import os
import tempfile
import csv
from datetime import datetime, date

DATA_SHEET_NAME = 'RawData'   
DASHBOARD_SHEET_NAME = 'Dashboard' 

def convert_row_types(row, header):
    type_map = {
        'Machine_ID': int,
        'Temperature_C': float,
        'Vibration_Hz': float,
        'Power_Consumption_kW': float,
        'Network_Latency_ms': float,
        'Packet_Loss_%': float,
        'Quality_Control_Defect_Rate_%': float,
        'Production_Speed_units_per_hr': float,
        'Predictive_Maintenance_Score': float,
        'Error_Rate_%': float
    }

    converted_row = []
    for value, col_name in zip(row, header):
        value = value.strip()
        
        # 1. Timestamp 
        if col_name == 'Timestamp':
            try:
                converted_row.append(datetime.strptime(value, '%d-%m-%Y %H:%M'))
            except:
                converted_row.append(value) 
        
        # 2. Convert numbers
        elif col_name in type_map:
            try:
                converted_row.append(type_map[col_name](value))
            except:
                converted_row.append(0)
        else:
            converted_row.append(value)
            
    return converted_row

def parse_csv_and_filter(csv_path, start_date, end_date):
    filtered_data = []
    
    with open(csv_path, mode='r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        
        try:
            original_header = next(reader)
        except StopIteration:
            return []

        has_index_col = original_header[0] == '' or 'Unnamed' in original_header[0]
        
        if has_index_col:
            clean_header = original_header[1:]
            start_index = 1
        else:
            clean_header = original_header
            start_index = 0

        filtered_data.append(clean_header)
        
        # Timestamp index
        try:
            ts_idx_clean = clean_header.index('Timestamp')
        except ValueError:
            st.error("Error: 'Timestamp' column not found.")
            return []

        # 3. Iterate Rows
        for row in reader:
            if not row: continue 
            clean_row = row[start_index:]
            
            # Convert types
            typed_row = convert_row_types(clean_row, clean_header)
            
            # Filter Logic
            try:
                row_date = typed_row[ts_idx_clean].date()
                if start_date <= row_date <= end_date:
                    filtered_data.append(typed_row)
            except AttributeError:
                continue

    return filtered_data

def generate_dashboard(template_path, csv_file_path, output_folder, start_date, end_date):
    try:
        # 1. Load Data
        data_rows = parse_csv_and_filter(csv_file_path, start_date, end_date)
        
        if len(data_rows) <= 1: 
            return False, "No data found for date range."

        # 2. Open Excel
        app = xw.App(visible=False)
        wb = app.books.open(template_path)
        
        # 3. Inject Data
        try:
            data_sheet = wb.sheets[DATA_SHEET_NAME]
            data_sheet.clear()
            data_sheet.range('A1').value = data_rows
        except Exception as e:
            wb.close()
            app.quit()
            return False, f"Error writing data: {str(e)}"

        # 4. Refresh
        wb.api.RefreshAll()
        
        # 5. Export
        dashboard_sheet = wb.sheets[DASHBOARD_SHEET_NAME]
        output_pdf = os.path.join(output_folder, f"Report_{start_date}_{end_date}.pdf")
        dashboard_sheet.api.ExportAsFixedFormat(0, output_pdf)
        
        wb.close()
        app.quit()
        return True, output_pdf

    except Exception as e:
        try: app.quit()
        except: pass
        return False, str(e)

# Interface
st.title("Excel Dashboard Generator")
csv_file = st.file_uploader("Upload CSV", type=['csv'])
template_file = st.file_uploader("Upload Template", type=['xlsx'])
output_dir = st.text_input("Output Path", value=os.getcwd())
col1, col2 = st.columns(2)
with col1: start = st.date_input("Start", value=date(2024, 1, 1))
with col2: end = st.date_input("End", value=date(2024, 1, 7))

if st.button("Generate PDF"):
    if csv_file and template_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_t:
            tmp_t.write(template_file.getvalue())
            t_path = tmp_t.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='wb') as tmp_c:
            tmp_c.write(csv_file.getvalue())
            c_path = tmp_c.name
            
        success, msg = generate_dashboard(t_path, c_path, output_dir, start, end)
        os.remove(t_path); os.remove(c_path)
        
        if success:
            st.success("Report Saved!")
            with open(msg, "rb") as f: st.download_button("Download", f, "Report.pdf")
        else: st.error(msg)