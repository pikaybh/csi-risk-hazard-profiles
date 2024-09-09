import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging
import fire

# Root Logger 설정
logger_name = '__main__'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

# File Handler 설정 (로그를 파일에 저장)
file_handler = logging.FileHandler(f'logs/{logger_name}.log', encoding='utf-8-sig')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(r'%(asctime)s [%(name)s, line %(lineno)d] %(levellevel)s: %(message)s'))
logger.addHandler(file_handler)

# Stream Handler 설정 (콘솔에 출력)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(r'%(message)s'))
logger.addHandler(stream_handler)


def extract_total_pages(soup: BeautifulSoup) -> int:
    '''BeautifulSoup을 사용하여 총 페이지 수를 추출하는 함수.
    
    Args:
        soup (BeautifulSoup): 페이지의 BeautifulSoup 객체
    
    Returns:
        int: 총 페이지 수
    '''
    # 페이지 네비게이션에서 가장 큰 번호를 가진 <a> 태그를 찾습니다.
    page_nav = soup.find('div', class_='pagination')  # 페이지 네비게이션이 있는 div 태그
    
    if page_nav:
        last_page_link = page_nav.find_all('a')[-1]  # 가장 마지막 <a> 태그가 마지막 페이지 번호
        try:
            return int(last_page_link.get_text(strip=True))  # 페이지 번호를 추출
        except ValueError:
            logger.error("마지막 페이지 번호를 숫자로 변환할 수 없습니다.")
            return 1
    else:
        logger.error("페이지 네비게이션을 찾을 수 없습니다.")
        return 1


def extract_table_data(soup: BeautifulSoup) -> pd.DataFrame:
    '''테이블 데이터를 추출하여 DataFrame으로 변환하는 함수.
    
    Args:
        soup (BeautifulSoup): 페이지의 BeautifulSoup 객체
    
    Returns:
        pd.DataFrame: 추출된 테이블 데이터가 담긴 DataFrame
    '''
    # 3. 테이블 태그 찾기
    table = soup.find('table')

    if not table:
        logger.error("테이블을 찾을 수 없습니다.")
        return pd.DataFrame()

    # 4. 테이블 헤더 추출 (thead -> th 태그)
    headers = [th.get_text(strip=True) for th in table.find_all('th')]

    # 5. 테이블 바디 추출 (tbody -> tr 태그)
    rows = []
    for tr in table.find_all('tr'):
        row = [td.get_text(strip=True) for td in tr.find_all('td')]
        if row:  # 빈 리스트는 무시
            rows.append(row)

    # 6. pandas DataFrame으로 변환
    return pd.DataFrame(rows, columns=headers)


def extract_case_numbers(url: str, output: str = "output.xlsx") -> None:
    '''주어진 URL에서 첫 페이지부터 마지막 페이지까지 테이블 데이터를 추출하여 Excel 파일로 저장하는 함수.
    
    Args:
        url (str): 사고 목록 페이지의 URL
        output (str): 추출된 테이블 데이터를 저장할 엑셀 파일 경로
    '''
    all_data = pd.DataFrame()  # 모든 페이지의 데이터를 저장할 DataFrame

    with sync_playwright() as p:
        try:
            # Chromium 브라우저 실행
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('networkidle')  # 네트워크 활동이 없을 때까지 대기

            # 첫 페이지의 HTML 콘텐츠를 BeautifulSoup으로 파싱
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # 첫 페이지에서 마지막 페이지 번호 추출 (BeautifulSoup 사용)
            total_pages = extract_total_pages(soup)
            logger.info(f"총 {total_pages} 페이지가 발견되었습니다.")

            # 첫 페이지 테이블 데이터 추출
            all_data = pd.concat([all_data, extract_table_data(soup)], ignore_index=True)

            # 2페이지부터 마지막 페이지까지 순회하며 테이블 데이터 추출
            for page_num in range(2, total_pages + 1):
                logger.info(f"페이지 {page_num} 처리 중...")
                page.goto(f'{url}&page_count={page_num}')
                page.wait_for_load_state('networkidle')

                # 해당 페이지의 HTML 콘텐츠를 BeautifulSoup으로 파싱
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # 각 페이지의 테이블 데이터를 추출하여 DataFrame에 추가
                all_data = pd.concat([all_data, extract_table_data(soup)], ignore_index=True)

            # 7. DataFrame을 Excel 파일로 저장
            all_data.to_excel(output, index=False)
            logger.info(f"모든 데이터가 {output}에 저장되었습니다.")

        except Exception as e:
            logger.error(f"오류 발생: {e}")
        finally:
            browser.close()


# Main entry point
def main(url: str, output: str = "output.xlsx") -> None:
    '''URL에서 테이블 데이터를 추출하여 Excel로 저장하는 작업을 실행
    
    Args:
        url (str): 사고 목록 페이지의 URL
        output (str): 결과 엑셀 파일 경로
    '''
    extract_case_numbers(url, output)


if __name__ == '__main__':
    fire.Fire(main)
