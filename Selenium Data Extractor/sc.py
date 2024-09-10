from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
import pandas as pd
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define date range
start_date = datetime(2022, 1, 1)  # Replace with your start date
end_date = datetime(2022, 12, 31)  # Replace with your end date

# File path for Excel file
excel_file_path = 'state_food_prices_22.xlsx'

# Check if the Excel file already exists
file_exists = os.path.isfile(excel_file_path)

# Create a new Excel file with headers if it doesn't exist
if not file_exists:
    # Create an empty DataFrame with headers
    df_empty = pd.DataFrame(columns=['State', 'Date', 'Price'])  # Adjust headers as needed
    df_empty.to_excel(excel_file_path, index=False)

# Loop through each date in the range
current_date = start_date

while current_date <= end_date:
    driver = webdriver.Chrome()
    driver.get('https://fcainfoweb.nic.in/reports/report_menu_web.aspx')

    try:
        # Wait for the page to load
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'ctl00_MainContent_Rbl_Rpt_type_0'))
        )

        # Click on the radio button by ID
        radio_button_id = 'ctl00_MainContent_Rbl_Rpt_type_0'
        driver.find_element(By.ID, radio_button_id).click()

        # Check if the dropdown menu is present and select "Daily Prices"
        dropdown_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'ctl00_MainContent_Ddl_Rpt_Option0'))
        )
        Select(dropdown_element).select_by_visible_text('Daily Prices')

        # Check if the date input box is present and input the current date
        date_input_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'ctl00_MainContent_Txt_FrmDate'))
        )
        formatted_date = current_date.strftime('%d/%m/%Y')
        date_input_element.clear()
        date_input_element.send_keys(formatted_date)

        # Click on the "Get Data" button
        driver.find_element(By.ID, 'ctl00_MainContent_btn_getdata1').click()

        # Wait for the page to load after redirection
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'gv0'))
        )

        # Extract data from the table
        table = driver.find_element(By.ID, 'gv0')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, 'th')]

        # Extract data for the specific state
        state_name = "Madhya Pradesh"
        data = []
        for row in rows[1:]:
            columns = row.find_elements(By.TAG_NAME, 'td')
            if columns and columns[0].text.strip() == state_name:
                state_data = [column.text.strip() for column in columns]
                data.append(state_data)
                break  # Assuming only one row per state

        # Convert the data to a DataFrame
        df = pd.DataFrame(data, columns=headers)
        df['Date'] = formatted_date  # Add date column

        # Append new data to the existing Excel file
        if file_exists:
            # Read existing data
            existing_df = pd.read_excel(excel_file_path)
            # Append new data
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            # Write the combined data to the Excel file
            combined_df.to_excel(excel_file_path, index=False)
        else:
            # Write new data to a new file
            df.to_excel(excel_file_path, index=False)

        logging.info(f"Data for {state_name} on {formatted_date} has been saved to {excel_file_path}.")

    except Exception as e:
        logging.error("An error occurred: %s", e)

    finally:
        driver.quit()

    # Move to the next date
    current_date += timedelta(days=1)
