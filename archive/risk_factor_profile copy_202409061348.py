from playwright.sync_api import sync_playwright, TimeoutError
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from functools import wraps
from tqdm import tqdm
import pandas as pd
import logging
import fire
import json
import time
import os
import re

# Set up logger for logging
logger_name = 'risk_factor_profile'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# File Handler for logging debug information to file
file_handler = logging.FileHandler(f'logs/{logger_name}.log', encoding='utf-8-sig')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(r'%(asctime)s [%(name)s, line %(lineno)d] %(levelname)s: %(message)s'))
logger.addHandler(file_handler)

# Stream Handler for console output (info level)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(r'%(message)s'))
logger.addHandler(stream_handler)

# Functions
def save_checkpoint(param02: str, param232: str, page: int, checkpoint: Optional[str] = None) -> None:
    """Save the checkpoint to a file so we can resume the scraping later.
    
    Args:
        param02 (str): Current `param02` value being processed.
        param232 (str): Current `param232` value being processed.
        page (int): Current page number that was last processed.
        checkpoint (Optional[str]): Path to the checkpoint file. If not provided, no checkpoint is saved.
    """
    if checkpoint:
        with open(checkpoint, 'w') as f:
            f.write(f'{param02},{param232},{page}')


def load_checkpoint(checkpoint: str) -> Tuple[Optional[str], Optional[str], int]:
    """Load the last checkpoint to resume scraping.
    
    Args:
        checkpoint (str): Path to the checkpoint file.
    
    Returns:
        Tuple[Optional[str], Optional[str], int]: 
        - param02: Last processed `param02` value.
        - param232: Last processed `param232` value.
        - page: Last processed page number.
    """
    if not os.path.exists(checkpoint):
        return None, None, 1
    with open(checkpoint, 'r') as f:
        param02, param232, page = f.read().strip().split(',')
        return param02, param232, int(page)


def remove_checkpoint(checkpoint: str) -> None:
    """Delete the checkpoint file once the scraping is finished.

    Args:
        checkpoint (str): Path to the checkpoint file.
    """
    if os.path.exists(checkpoint):
        os.remove(checkpoint)


def get_total_pages(playwright, param02: str, param232: str) -> int:
    """Fetch the total number of pages available for the given `param02` and `param232`.
    
    Args:
        playwright (Playwright): The Playwright instance for browser automation.
        param02 (str): The value of the `param02` parameter used in the URL.
        param232 (str): The value of the `param232` parameter used in the URL.

    Returns:
        int: Total number of pages extracted from the web page.
    """
    # Launch the browser in invisible mode
    with playwright.chromium.launch(headless=True) as browser: # Launch the browser in visible mode by set headless=False for debugging
        page = browser.new_page()

        # Construct the URL with param02 and param232
        page.goto(f"https://www.csi.go.kr/hrp/hrpRankDtlPop.do?param02={param02}&param03={param232}")

        # Wait for the page to be fully loaded
        page.wait_for_load_state('networkidle')

        # Get the page content
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Check if the desired element is found
        help_inline = soup.find('div', class_='help-inline')
        if help_inline:
            page_text = help_inline.text
            total_pages = int(page_text.split('/')[1].split('페이지')[0].replace(',', '').strip())
            logger.debug(f"{param02 = }; {param232 = }; {total_pages = :,}")
            return total_pages
        else:
            logger.error(f"Could not find 'help-inline' div for {param02} and {param232}")
            return 1  # Default to 1 if the div is not found


def fetch_page_data(page, param02: str, param232: str, page_num: int) -> pd.DataFrame:
    """Fetch the data from a single page and return as a DataFrame.

    Args:
        page (Page): The Playwright page instance for browser automation.
        param02 (str): The value of the `param02` parameter used in the URL.
        param232 (str): The value of the `param232` parameter used in the URL.
        page_num (int): The page number to scrape.

    Returns:
        pd.DataFrame: Data extracted from the page in tabular format.
    """
    # Construct the URL for the specific page number
    url = f"https://www.csi.go.kr/hrp/hrpRankDtlPop.do?param02={param02}&param03={param232}&page_count={page_num}"
    page.goto(url)

    # Wait for the page to be fully loaded
    page.wait_for_load_state('networkidle')

    # Get the page content
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Find the table containing the data
    table = soup.find('table', class_='table table-striped table-bordered table-hover')
    if table:
        # Extract table rows
        rows = table.find('tbody').find_all('tr')
        data = []

        # Loop through rows and extract each cell's text
        for row in rows:
            cols = [ele.text.strip() for ele in row.find_all('td')]
            data.append(cols)

        # Define column names based on the HTML structure
        columns = ['시설물 종류 대분류', '시설물 종류 중분류', '시설물 종류 소분류', '공종 대분류', '공종 중분류', '위험발생 객체 대분류', '위험발생 객체 중분류',
                   '위험발생 위치 대분류', '위험발생 위치 중분류', '위험발생 위치 소분류', '작업 프로세스', '물적 피해', '인적 피해', '사고 원인', 
                   '사고 가능성', '사고 심각성', '설계 단계', '시공 단계']
        return pd.DataFrame(data, columns=columns)
    else:
        logger.error(f"Could not find the table on page {page_num} for {param02} and {param232}")
        return pd.DataFrame()  # Return empty DataFrame if table is not found


# Function to replace illegal characters
def replace_illegal_characters(text: str) -> str:
    """Replace illegal characters in a string with underscores.

    Args:
        text (str): The input string that may contain illegal characters.

    Returns:
        str: A sanitized string with illegal characters replaced.
    """
    # Define a regex pattern for illegal characters (you can add more if needed)
    illegal_pattern: str = r'[\\/*?:"<>|\n\r\t]'
    
    # Replace any illegal character with '_'
    sanitized_text: str = re.sub(illegal_pattern, '_', text)
    
    return sanitized_text


def save_data(data: pd.DataFrame, param02: str, param232: str, directory: str) -> None:
    """Save the DataFrame to an Excel file based on the given `param02` and `param232` values.
    
    Args:
        data (pd.DataFrame): The DataFrame containing the extracted data.
        param02 (str): The `param02` value to name the file.
        param232 (str): The `param232` value to name the file.
        directory (str): The directory where the Excel file will be saved.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Ensure filename is safe for file systems by replacing illegal characters
    safe_param02 = replace_illegal_characters(param02)
    safe_param232 = replace_illegal_characters(param232)
    
    # Construct the filename with sanitized param02 and param232
    filename = os.path.join(directory, f"{safe_param02}-{safe_param232}.xlsx")
    data.to_excel(filename, index=False)


def main(params: Optional[str] = 'extracted_data.json', output: Optional[str] = 'risk_factor_profiles', checkpoint: Optional[str] = 'tmp/checkpoint') -> None:
    """Main function to orchestrate the scraping process.

    Args:
        params (Optional[str], optional): Path to the input JSON file containing param02 and param232 values. Defaults to 'extracted_data.json'.
        output (Optional[str], optional): Output directory to save the Excel files. Defaults to 'risk_factor_profiles'.
        checkpoint (Optional[str], optional): Path to the checkpoint file. Defaults to 'logs/checkpoint.txt'.
    """
    # Load the input JSON file
    with open(params, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert the JSON data into a DataFrame for easy processing
    df = pd.DataFrame(data)
    
    # Ensure param02 and param232 are treated as strings
    df['param02'] = df['param02'].astype(str)
    df['param232'] = df['param232'].astype(str)

    # Load the checkpoint if available
    last_param02, last_param232, last_page = load_checkpoint(checkpoint)
    
    # Initialize Playwright
    with sync_playwright() as playwright:
        # Launch the browser once
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        checkpoint_reached = False  # Flag to indicate if we've reached the checkpoint

        # Iterate over each row in the input file
        for index, row in tqdm(df.iterrows(), total=len(df)):
            param02, param232 = row['param02'], row['param232']
            
            # If the checkpoint is set and not yet reached
            if last_param02 and last_param232 and not checkpoint_reached:
                # Skip rows until we reach the last processed row in the checkpoint
                if param02 == last_param02 and param232 == last_param232:
                    checkpoint_reached = True  # We've reached the checkpoint, start from here
                else:
                    continue  # Skip this row, it's already processed
            
            # If the checkpoint is reached or there is no checkpoint
            if checkpoint_reached or (last_param02 is None and last_param232 is None):
                # Get the total number of pages for the current param02 and param232
                total_pages = get_total_pages(playwright, param02, param232)
                
                # Start from the last saved page if resuming from a checkpoint, otherwise start from page 1
                start_page = last_page if param02 == last_param02 and param232 == last_param232 else 1
                
                # Collect data from each page and accumulate in a DataFrame
                all_data = pd.DataFrame()
                for page_num in tqdm(range(start_page, total_pages + 1), desc=f"Fetching {param02}, {param232}"):
                    data = fetch_page_data(page, param02, param232, page_num)
                    all_data = pd.concat([all_data, data])
                    # Save checkpoint after processing each page
                    save_checkpoint(param02, param232, page_num, checkpoint)
                
                # Save the accumulated data to an Excel file
                save_data(all_data, param02, param232, output)
                
                # Reset checkpoint once the row is fully processed
                remove_checkpoint(checkpoint)
                last_page = 1  # Reset the page tracker for the next param02/param232 pair
        
        # Close the browser after all rows are processed
        browser.close()


# Main entry point
if __name__ == "__main__":
    fire.Fire(main)
