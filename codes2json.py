from typing import Dict, Optional
from logging import Logger
import pandas as pd
import fire
import json

# logger
logger = Logger()

# Function
def save_json(df: pd.DataFrame, output: str) -> None:
    # Convert the dataframe to JSON format
    json_data = json.loads(df.to_json(orient='records', force_ascii=False))

    # Save the pretty JSON data to a file with indentations
    with open(output, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

def main(input: Optional[str] = "extracted_data.xlsx", output: Optional[str] = 'extracted_data.json', **kwargs: Optional[Dict[str, type]]) -> None:
    # Load the data, explicitly define the data types for the 'param02' and 'param232' columns as string
    df = pd.read_excel(input, sheet_name='Sheet1', dtype={'param02': str, 'param232': str} if not kwargs else kwargs)

    save_json(df, output)
    logger.info(f"Json file save at {output}.")

# Main
if __name__ == '__main__':
    fire.Fire(main)
