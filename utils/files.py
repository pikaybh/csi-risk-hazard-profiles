import pandas as pd
import os
import re


def replace_illegal_characters(text: str) -> str:
    """
    Replace illegal characters in a string with underscores.
    
    Args:
        text (str): The input string that may contain illegal characters.

    Returns:
        str: A sanitized string with illegal characters replaced.
    """
    illegal_pattern = r'[\\/*?:"<>|\n\r\t]'
    return re.sub(illegal_pattern, '_', text)


def save_data(data: pd.DataFrame, param02: str, param232: str, directory: str) -> None:
    """
    Save the DataFrame to an Excel file based on the given `param02` and `param232` values.

    Args:
        data (pd.DataFrame): The DataFrame containing the extracted data.
        param02 (str): The `param02` value to name the file.
        param232 (str): The `param232` value to name the file.
        directory (str): The directory where the Excel file will be saved.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    safe_param02 = replace_illegal_characters(param02)
    safe_param232 = replace_illegal_characters(param232)
    
    filename = os.path.join(directory, f"{safe_param02}-{safe_param232}.xlsx")
    data.to_excel(filename, index=False)


def save_checkpoint(param02: str, param232: str, page: int, checkpoint: str) -> None:
    """
    Save the checkpoint to a file so we can resume the scraping later.

    Args:
        param02 (str): Current `param02` value being processed.
        param232 (str): Current `param232` value being processed.
        page (int): Current page number that was last processed.
        checkpoint (str): Path to the checkpoint file.
    """
    if checkpoint:
        with open(checkpoint, 'w') as f:
            f.write(f'{param02},{param232},{page}')


def load_checkpoint(checkpoint: str) -> tuple:
    """
    Load the last checkpoint to resume scraping.

    Args:
        checkpoint (str): Path to the checkpoint file.
    
    Returns:
        tuple: A tuple containing param02, param232, and the last processed page.
    """
    if not os.path.exists(checkpoint):
        return None, None, 1
    with open(checkpoint, 'r') as f:
        param02, param232, page = f.read().strip().split(',')
        return param02, param232, int(page)


def remove_checkpoint(checkpoint: str) -> None:
    """
    Delete the checkpoint file once the scraping is finished.

    Args:
        checkpoint (str): Path to the checkpoint file.
    """
    if os.path.exists(checkpoint):
        os.remove(checkpoint)
