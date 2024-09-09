from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import fire
import bs4


def get_column_value(cols, index, previous_value):
    """Attempt to get the value from cols at index, if it fails, return the previous value."""
    try:
        # Try to fetch and return the stripped text, if it's non-empty, otherwise return the previous value
        return cols[index].get_text(strip=True) or previous_value
    except Exception:
        # In case of any exception (like IndexError), return the previous value
        return previous_value

def get_code(raw: bs4.ResultSet.sort) -> List[Dict[str, str]]:
    # Extract data and store it in a list of dictionaries
    data: List[Dict[str, str]] = []
    for button in tqdm(buttons):
        onclick_text = button.get("onclick")
        if "go_viewpop" in onclick_text:
            # Extract the parameters inside the go_viewpop function call
            params: List[str] = onclick_text.split("'")
            param02: str = params[1]  # '02'
            param232: str = params[3]  # '015'
            # Find associated elements in the same row (in this case, I assume they might be <td> or <span> elements)
            row = button.find_parent("tr")
            if row:
                cols = row.find_all("td")
                # Assuming you have your variables defined as:
                공종_대분류: str = ""
                공종_중분류: str = ""
                위험발생객체_대분류: str = ""
                위험발생객체_중분류: str = ""
                # Now use the function to handle missing or faulty columns
                공종_대분류 = get_column_value(cols, -6, 공종_대분류)
                공종_중분류 = get_column_value(cols, -5, 공종_중분류)
                위험발생객체_대분류 = get_column_value(cols, -4, 위험발생객체_대분류)
                위험발생객체_중분류 = get_column_value(cols, -3, 위험발생객체_중분류)
                건수 = cols[-2].text.strip()
                # Append the extracted data to the list
                data.append({
                    "공종(대분류)": 공종_대분류,
                    "공종(중분류)": 공종_중분류,
                    "위험발생객체(대분류)": 위험발생객체_대분류,
                    "위험발생객체(중분류)": 위험발생객체_중분류,
                    "건수": 건수,
                    "param02": param02,
                    "param232": param232
                })
    # Return data
    return data

def main(input: Optional[str] = "samples/위험요소프로파일 _ 위험요소 프로파일 _ 위험요소 프로파일 순위.html",
        output: Optional[str] = "extracted_data.xlsx") -> None:
    # Load the HTML file
    with open(input, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    # Find all the relevant button tags with the specific onclick attribute
    buttons = soup.find_all("button", {"type": "button", "class": "btn blue"})
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(get_code(buttons))
    # Save the dataframe to an Excel file
    output_file = output
    df.to_excel(output_file, index=False)

# Main
if __name__ == '__main__':
    fire.Fire(main)

