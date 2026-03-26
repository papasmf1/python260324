import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook


URL = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"
ENTRY_URL = "https://finance.naver.com/sise/entryJongmok.naver"


def crawl_kpi200_top_items(page=1):
    """
    코스피200 페이지의 '편입종목상위' 표를 크롤링해서
    [{종목별, 현재가, 전일비, 등락률, 거래량, 거래대금(백만), 시가총액(억)}, ...] 형태로 반환
    """
    params = {
        "type": "KPI200",
        "page": page,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    # 편입종목상위 데이터는 메인 페이지가 아니라 iframe(entryJongmok)에서 제공됨
    res = requests.get(ENTRY_URL, params=params, headers=headers, timeout=10)
    res.raise_for_status()
    # 페이지 인코딩이 바뀌어도 깨지지 않도록 자동 추정 인코딩 사용
    res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.text, "html.parser")

    # iframe 내 편입종목상위 테이블
    table = soup.select_one("table.type_1")

    if table is None:
        raise ValueError("편입종목상위 테이블을 찾지 못했습니다.")

    result = []
    rows = table.select("tr")

    for row in rows:
        tds = row.find_all("td")
        if len(tds) != 7:
            continue  # 공백 행, 페이지네이션 행 제외

        cols = [td.get_text(" ", strip=True) for td in tds]
        if not cols[0]:
            continue

        item = {
            "종목별": cols[0],
            "현재가": cols[1],
            "전일비": cols[2],
            "등락률": cols[3],
            "거래량": cols[4],
            "거래대금(백만)": cols[5],
            "시가총액(억)": cols[6],
        }
        result.append(item)

    return result


def crawl_kpi200_top_items_all(max_page=20):
    """
    편입종목상위 1~max_page 페이지를 모두 수집해서 하나의 리스트로 반환
    """
    all_items = []

    for page in range(1, max_page + 1):
        page_items = crawl_kpi200_top_items(page=page)
        for item in page_items:
            item["페이지"] = page
        all_items.extend(page_items)

    return all_items


def save_to_excel(data, file_name="kospi200.xlsx"):
    """
    수집한 편입종목상위 데이터를 엑셀 파일로 저장
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "KOSPI200"

    headers = ["페이지", "종목별", "현재가", "전일비", "등락률", "거래량", "거래대금(백만)", "시가총액(억)"]
    ws.append(headers)

    for row in data:
        ws.append(
            [
                row.get("페이지", ""),
                row.get("종목별", ""),
                row.get("현재가", ""),
                row.get("전일비", ""),
                row.get("등락률", ""),
                row.get("거래량", ""),
                row.get("거래대금(백만)", ""),
                row.get("시가총액(억)", ""),
            ]
        )

    wb.save(file_name)


if __name__ == "__main__":
    data = crawl_kpi200_top_items_all(max_page=20)
    save_to_excel(data, file_name="kospi200.xlsx")

    print(f"총 수집 건수: {len(data)}")
    print("저장 파일: kospi200.xlsx")

    for i, row in enumerate(data[:10], 1):
        print(
            f"{i:03d}. [p{row['페이지']:02d}] {row['종목별']:10s} | 현재가: {row['현재가']:>10s} | "
            f"등락률: {row['등락률']:>8s} | 거래량: {row['거래량']:>10s}"
        )