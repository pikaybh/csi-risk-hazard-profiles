# Internal Modules
from utils.files import load_checkpoint, save_checkpoint, remove_checkpoint, save_data
from utils.scraping import fetch_page_data, get_total_pages
from utils.decorators import retry_on_timeout
from utils.logging import setup_logging
# External Modules
from playwright.sync_api import sync_playwright
from typing import Optional
from tqdm import tqdm
import pandas as pd
import json
import fire

# Set logger
logger = setup_logging('risk_factor_profile')

# Main
def main(params: Optional[str] = 'extracted_data.json', output: Optional[str] = 'risk_factor_profiles', checkpoint: Optional[str] = 'tmp/checkpoint') -> None:
    """
    Main function to orchestrate the scraping process.

    Args:
        params (Optional[str], optional): Path to the input JSON file containing param02 and param232 values. Defaults to 'extracted_data.json'.
        output (Optional[str], optional): Output directory to save the Excel files. Defaults to 'risk_factor_profiles'.
        checkpoint (Optional[str], optional): Path to the checkpoint file. Defaults to 'logs/checkpoint.txt'.
    """
    # Load the input JSON file
    with open(params, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df['param02'] = df['param02'].astype(str)
    df['param232'] = df['param232'].astype(str)

    last_param02, last_param232, last_page = load_checkpoint(checkpoint)
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        checkpoint_reached = False

        # Iterate over each row in the input file
        for index, row in tqdm(df.iterrows(), total=len(df)):
            param02, param232 = row['param02'], row['param232']

            if last_param02 and last_param232 and not checkpoint_reached:
                if param02 == last_param02 and param232 == last_param232:
                    checkpoint_reached = True
                else:
                    continue

            total_pages = get_total_pages(playwright, param02, param232)
            start_page = last_page if param02 == last_param02 and param232 == last_param232 else 1

            all_data = pd.DataFrame()
            for page_num in tqdm(range(start_page, total_pages + 1), desc=f"Fetching {param02}, {param232}"):
                data = fetch_page_data(page, param02, param232, page_num, browser=browser, playwright=playwright)
                all_data = pd.concat([all_data, data])
                save_checkpoint(param02, param232, page_num, checkpoint)
            
            save_data(all_data, param02, param232, output)
            remove_checkpoint(checkpoint)

        browser.close()

# Main Entry point
if __name__ == "__main__":
    fire.Fire(main)
