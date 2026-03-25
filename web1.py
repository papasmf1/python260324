# web1.py 
#크롤링 작업을 위한 라이브러리 
from bs4 import BeautifulSoup

#페이지를 로딩
page = open("Chap09_test.html", "rt", encoding="utf-8").read()
#전체 페이지를 BeautifulSoup 객체로 변환
soup = BeautifulSoup(page, "html.parser")
#전체 보기 
#print(soup.prettify())
#<p>를 몽땅 검색하기 
print( soup.find_all("p") )


