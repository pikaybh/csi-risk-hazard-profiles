from bs4 import BeautifulSoup
import pandas as pd

# 1. HTML 데이터 (여기에 실제 HTML 문자열을 넣으세요)
html_content = '''
<div class="table-scrollable scrollOptionY">
    <table class="table table-striped table-bordered table-hover" summary="시설물 종류,공종,위험요소,위험성,저감대책으로 구성되어 있습니다.">
        <!-- 여기에 전체 HTML 테이블 내용이 들어갑니다 -->
    </table>
</div>
'''

# 2. BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(html_content, 'lxml')

# 3. 테이블 태그 찾기
table = soup.find('table')

# 4. 테이블 헤더 추출 (thead -> th 태그)
headers = []
for th in table.find_all('th'):
    headers.append(th.get_text(strip=True))

# 5. 테이블 바디 추출 (tbody -> tr 태그)
rows = []
for tr in table.find_all('tr'):
    row = [td.get_text(strip=True) for td in tr.find_all('td')]
    if row:  # 빈 리스트는 무시
        rows.append(row)

# 6. pandas DataFrame으로 변환
df = pd.DataFrame(rows, columns=headers)

# 7. DataFrame을 Excel 파일로 저장
df.to_excel("output.xlsx", index=False)

# DataFrame 결과 출력
print(df)
