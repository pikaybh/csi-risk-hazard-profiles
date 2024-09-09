# Internal Modules
from utils.decorators import retry_on_timeout
# External Modules
from bs4 import BeautifulSoup
from random import randint
import pandas as pd
import logging

# Set logger
logger = logging.getLogger('risk_factor_profile')

@retry_on_timeout(retries=10, delay=randint(1, 10), restart_browser_every=3)
def get_total_pages(playwright, param02: str, param232: str, browser=None, page=None) -> int:
    """
    Fetch the total number of pages available for the given `param02` and `param232`.

    Args:
        playwright (Playwright): The Playwright instance for browser automation.
        param02 (str): The value of the `param02` parameter used in the URL.
        param232 (str): The value of the `param232` parameter used in the URL.
        browser: Browser instance to handle page loading.
        page: Page instance to load content.

    Returns:
        int: Total number of pages extracted from the web page.
    """
    # If browser or page is None (when retrying after a restart)
    if browser is None or page is None:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

    # Construct the URL and navigate
    page.goto(f"https://www.csi.go.kr/hrp/hrpRankDtlPop.do?param02={param02}&param03={param232}")
    page.wait_for_load_state('networkidle')

    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    help_inline = soup.find('div', class_='help-inline')
    if help_inline:
        page_text = help_inline.text
        total_pages = int(page_text.split('/')[1].split('페이지')[0].replace(',', '').strip())
        logger.debug(f"{param02 = }, {param232 = }, {total_pages = }")
        return total_pages
    else:
        logger.error(f"Could not find 'help-inline' div for {param02} and {param232}")
        return 1

@retry_on_timeout(retries=10, delay=randint(1, 10), restart_browser_every=3)
def fetch_page_data(page, param02: str, param232: str, page_num: int, browser=None, playwright=None) -> pd.DataFrame:
    """
    Fetch the data from a single page and return as a DataFrame.

    Args:
        page (Page): The Playwright page instance for browser automation.
        param02 (str): The value of the `param02` parameter used in the URL.
        param232 (str): The value of the `param232` parameter used in the URL.
        page_num (int): The page number to scrape.
        browser: Browser instance for handling page.
        playwright: Playwright instance for restarting browser if necessary.

    Returns:
        pd.DataFrame: Data extracted from the page in tabular format.
    """
    url = f"https://www.csi.go.kr/hrp/hrpRankDtlPop.do?param02={param02}&param03={param232}&page_count={page_num}"
    page.goto(url)
    page.wait_for_load_state('networkidle')

    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    table = soup.find('table', class_='table table-striped table-bordered table-hover')
    if table:
        rows = table.find('tbody').find_all('tr')
        data = [[ele.text.strip() for ele in row.find_all('td')] for row in rows]

        columns = ['시설물 종류 대분류', '시설물 종류 중분류', '시설물 종류 소분류', '공종 대분류', '공종 중분류',
                   '위험발생 객체 대분류', '위험발생 객체 중분류', '위험발생 위치 대분류', '위험발생 위치 중분류',
                   '위험발생 위치 소분류', '작업 프로세스', '물적 피해', '인적 피해', '사고 원인', 
                   '사고 가능성', '사고 심각성', '설계 단계', '시공 단계']
        return pd.DataFrame(data, columns=columns)
    else:
        logger.error(f"Could not find the table on page {page_num} for {param02} and {param232}")
        return pd.DataFrame()
