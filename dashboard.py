import streamlit as st
import pandas as pd
import xlwings as xw
import os
import tempfile
from datetime import date

DATA_SHEET_NAME = 'RawData'   
DASHBOARD_SHEET_NAME = 'Dashboard' 

def generate_dashboard(template_path, csv_file, output_folder, start_date, end_date):

    try:
        df = pd.read_csv(csv_file)
        date_col = 'Timestamp' 
        
        if date_col in df.columns:
            # Convert timestamp to datetime
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True)
            
            # Create a mask for filtering
            mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
            filtered_df = df.loc[mask]
        else:
            st.warning(f"Column '{date_col}' not found. Using full dataset.")
            filtered_df = df
        
        # Dropping unnecessary columns
        if 'Unnamed: 0' in filtered_df.columns:
            filtered_df = filtered_df.drop(columns=['Unnamed: 0'])


        # 2. Excel App
        app = xw.App(visible=False)
        
        wb = app.books.open(template_path)
        
        # 3. Inserting Data
        try:
            data_sheet = wb.sheets[DATA_SHEET_NAME]
            data_sheet.clear() 
            data_sheet.range('A1').options(index=False).value = filtered_df
        except Exception as e:
            wb.close()
            app.quit()
            return False, f"Error writing to sheet '{DATA_SHEET_NAME}': {str(e)}"

        # 4. Refresh Pivot Tables/Charts
        wb.api.RefreshAll()
        
        # 5. Export to PDF
        dashboard_sheet = wb.sheets[DASHBOARD_SHEET_NAME]
        
        output_pdf_name = f"Machine_Report_{start_date}_to_{end_date}.pdf"
        output_full_path = os.path.join(output_folder, output_pdf_name)
        
        dashboard_sheet.api.ExportAsFixedFormat(0, output_full_path)
        
        wb.close()
        app.quit()
        
        return True, output_full_path

    except Exception as e:
        try:
            app.quit()
        except:
            pass
        return False, str(e)

# Streamlit Interface
st.set_page_config(page_title="Machine Data Reporter")
st.title("Machine Efficiency Dashboard Generator")

# Upload Raw excel file
csv_file = st.file_uploader("1. Upload RawData.csv", type=['csv'])

# Upload excel template
template_file = st.file_uploader("2. Upload Excel Template (.xlsx)", type=['xlsx'])

# Folder path
output_dir = st.text_input("3. Output Folder Path", value=os.getcwd())

# Date Filter
st.subheader("Filter Data by Time")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=date(2024, 1, 1))
with col2:
    end_date = st.date_input("End Date", value=date(2024, 1, 7))

# Generate PDF
if st.button("Generate Report", type="primary"):
    if csv_file and template_file and output_dir:
        if not os.path.exists(output_dir):
            st.error("The output directory does not exist.")
        else:
            with st.spinner("Processing data and generating PDF..."):
                # Save temp template
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                    tmp.write(template_file.getvalue())
                    tmp_template_path = tmp.name

                success, message = generate_dashboard(
                    tmp_template_path, 
                    csv_file, 
                    output_dir, 
                    start_date, 
                    end_date
                )
                
                os.remove(tmp_template_path)

                if success:
                    st.success(f"Report saved: {message}")
                    with open(message, "rb") as pdf_file:
                        st.download_button(
                            label="Download PDF",
                            data=pdf_file,
                            file_name="Machine_Report.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.error(f"Failed: {message}")
    else:
        st.warning("Please upload all files to proceed.")