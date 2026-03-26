import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

URL = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%EB%B0%98%EB%8F%84%EC%B2%B4&ackey=9cbp62vl"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.naver.com/"
}

response = requests.get(URL, headers=headers, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# 보내주신 태그 구조 기준: videoItem 블록의 제목 링크(.glink) 추출
news_list = []
for item in soup.select('div[data-template-id="videoItem"]'):
    title_link = item.select_one('a[data-heatmap-target=".glink"]')
    if not title_link:
        continue

    title = title_link.get_text(" ", strip=True)
    link = title_link.get("href")
    if title and link:
        news_list.append((title, link))

# 일반 뉴스 영역 선택자도 함께 시도 (페이지 구조가 다를 때 대비)
if not news_list:
    for a_tag in soup.select("a.news_tit"):
        title = a_tag.get("title") or a_tag.get_text(strip=True)
        link = a_tag.get("href")
        if title and link:
            news_list.append((title, link))

# 중복 제거
unique_news = list(dict.fromkeys(news_list))

print(f"수집된 기사 수: {len(unique_news)}")
for i, (title, link) in enumerate(unique_news, 1):
    print(f"{i}. {title}")
    print(f"   {link}")

# 엑셀 파일 저장
workbook = Workbook()
sheet = workbook.active
sheet.title = "naver_news"

sheet.append(["번호", "제목", "링크"])
for i, (title, link) in enumerate(unique_news, 1):
    sheet.append([i, title, link])

output_file = "naver_result.xlsx"
workbook.save(output_file)
print(f"엑셀 저장 완료: {output_file}")