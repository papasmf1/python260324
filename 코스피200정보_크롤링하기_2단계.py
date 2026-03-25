#페이징 처리를 추가 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def crawl_kospi200_stocks():
    """
    네이버 금융에서 KOSPI 200 편입종목 정보를 크롤링하는 함수
    """
    url = "https://finance.naver.com/sise/entryJongmok.naver?type=KPI200"
    
    # 헤더 설정 (브라우저로 인식되도록)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 웹페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 체크
        response.encoding = 'euc-kr'  # 네이버는 euc-kr 인코딩 사용
        
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 편입종목 테이블 찾기
        table = soup.find('table', class_='type_1')
        
        if not table:
            print("편입종목 테이블을 찾을 수 없습니다.")
            return None
        
        # 테이블 헤더 추출 (첫 번째 tr)
        header_row = table.find('tr')
        headers = []
        for th in header_row.find_all('th'):
            header_text = th.get_text(strip=True)
            # 불필요한 텍스트 제거
            header_text = header_text.replace('(백만)', '').replace('(억)', '')
            if header_text:
                headers.append(header_text)
        
        # 데이터 행 추출 (헤더와 빈 행 제외)
        rows = table.find_all('tr')
        stock_data = []
        
        for row in rows:
            # 빈 행이나 헤더 행 건너뛰기
            if row.find('th') or 'blank' in str(row.get('class', [])) or 'division_line' in str(row.get('class', [])):
                continue
                
            cols = row.find_all('td')
            if len(cols) >= 7:  # 7개 컬럼이 있는 행만 처리
                row_data = []
                
                for i, col in enumerate(cols):
                    if i == 0:  # 종목명 컬럼
                        link = col.find('a')
                        if link:
                            stock_name = link.get_text(strip=True)
                            stock_code = link.get('href', '').split('code=')[-1] if 'code=' in link.get('href', '') else ''
                            row_data.append(stock_name)
                            if len(row_data) == 1:  # 종목코드도 추가
                                row_data.append(stock_code)
                        else:
                            row_data.append(col.get_text(strip=True))
                            row_data.append('')  # 빈 종목코드
                    else:
                        # 숫자 데이터 정리 (콤마 제거 등)
                        text = col.get_text(strip=True)
                        # 보합/상승/하락 등의 특수 문자 처리
                        if '보합' in text or '상승' in text or '하락' in text:
                            # span 태그에서 실제 숫자만 추출
                            span = col.find('span')
                            if span:
                                text = span.get_text(strip=True)
                        
                        # 콤마 제거
                        text = text.replace(',', '')
                        row_data.append(text)
                
                if len(row_data) > 0 and row_data[0]:  # 종목명이 있는 행만 추가
                    stock_data.append(row_data)
        
        # DataFrame 생성
        if stock_data:
            # 헤더에 종목코드 컬럼 추가
            column_names = ['종목명', '종목코드'] + headers[1:]  # 첫 번째 헤더(종목별) 제외하고 종목코드 추가
            
            # 데이터 길이에 맞춰 컬럼명 조정
            max_cols = max(len(row) for row in stock_data)
            if len(column_names) < max_cols:
                for i in range(len(column_names), max_cols):
                    column_names.append(f'컬럼{i+1}')
            elif len(column_names) > max_cols:
                column_names = column_names[:max_cols]
            
            df = pd.DataFrame(stock_data, columns=column_names)
            return df
        else:
            print("추출된 데이터가 없습니다.")
            return None
            
    except requests.RequestException as e:
        print(f"웹페이지 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        return None

def crawl_all_pages(max_pages=20):
    """
    모든 페이지의 KOSPI 200 편입종목을 크롤링
    """
    all_data = []
    page = 1
    
    while page <= max_pages:
        print(f"페이지 {page} 크롤링 중...")
        url = f"https://finance.naver.com/sise/entryJongmok.naver?type=KPI200&page={page}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.encoding = 'euc-kr'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            table = soup.find('table', class_='type_1')
            if not table:
                print(f"페이지 {page}에서 테이블을 찾을 수 없습니다. 크롤링을 종료합니다.")
                break
                
            # 데이터 추출 로직
            rows = table.find_all('tr')
            page_data = []
            
            for row in rows:
                if row.find('th') or 'blank' in str(row.get('class', [])) or 'division_line' in str(row.get('class', [])):
                    continue
                    
                cols = row.find_all('td')
                if len(cols) >= 7:
                    row_data = []
                    
                    for i, col in enumerate(cols):
                        if i == 0:  # 종목명 컬럼
                            link = col.find('a')
                            if link:
                                stock_name = link.get_text(strip=True)
                                stock_code = link.get('href', '').split('code=')[-1] if 'code=' in link.get('href', '') else ''
                                row_data.append(stock_name)
                                row_data.append(stock_code)
                            else:
                                row_data.append(col.get_text(strip=True))
                                row_data.append('')
                        else:
                            text = col.get_text(strip=True)
                            if '보합' in text or '상승' in text or '하락' in text:
                                span = col.find('span')
                                if span:
                                    text = span.get_text(strip=True)
                            text = text.replace(',', '')
                            row_data.append(text)
                    
                    if len(row_data) > 0 and row_data[0]:
                        page_data.append(row_data)
            
            if not page_data:  # 더 이상 데이터가 없으면 종료
                print(f"페이지 {page}에서 더 이상 데이터가 없습니다. 크롤링을 종료합니다.")
                break
                
            all_data.extend(page_data)
            print(f"페이지 {page}에서 {len(page_data)}개 종목 수집 완료")
            page += 1
            time.sleep(1)  # 서버 부하 방지 (1초 대기)
            
        except Exception as e:
            print(f"페이지 {page} 크롤링 중 오류: {e}")
            break
    
    if all_data:
        column_names = ['종목명', '종목코드', '현재가', '전일비', '등락률', '거래량', '거래대금', '시가총액']
        df = pd.DataFrame(all_data, columns=column_names)
        print(f"\n전체 {len(all_data)}개 종목 수집 완료!")
        return df
    else:
        return None

def save_to_csv(df, filename='kospi200_stocks.csv'):
    """
    DataFrame을 CSV 파일로 저장
    """
    if df is not None:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"데이터가 {filename}에 저장되었습니다.")
    else:
        print("저장할 데이터가 없습니다.")

def save_to_excel(df, filename='kospi200_stocks.xlsx'):
    """
    DataFrame을 Excel 파일로 저장
    """
    if df is not None:
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"데이터가 {filename}에 저장되었습니다.")
    else:
        print("저장할 데이터가 없습니다.")

# 메인 실행 코드
if __name__ == "__main__":
    print("KOSPI 200 편입종목 정보 크롤링을 시작합니다...")
    
    # 모든 페이지 크롤링
    df = crawl_all_pages()
    
    if df is not None:
        print(f"\n총 {len(df)}개의 종목 정보를 수집했습니다.")
        print("\n상위 10개 종목:")
        print(df.head(10).to_string(index=False))
        
        print("\n하위 10개 종목:")
        print(df.tail(10).to_string(index=False))
        
        # CSV 파일로 저장
        save_to_csv(df)
        
        # Excel 파일로도 저장 (선택사항)
        try:
            save_to_excel(df)
        except ImportError:
            print("Excel 저장을 위해 openpyxl 라이브러리를 설치해주세요: pip install openpyxl")
        
        # 기본 통계 정보
        print(f"\n데이터 shape: {df.shape}")
        print(f"컬럼명: {list(df.columns)}")
        
        # 간단한 분석
        print(f"\n시가총액 상위 5개 종목:")
        if '시가총액' in df.columns:
            # 시가총액 컬럼을 숫자로 변환
            df['시가총액_숫자'] = pd.to_numeric(df['시가총액'], errors='coerce')
            top_5 = df.nlargest(5, '시가총액_숫자')[['종목명', '시가총액']]
            print(top_5.to_string(index=False))
    else:
        print("크롤링에 실패했습니다.")
    
    print("\n크롤링이 완료되었습니다.")