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
#print( soup.find_all("p") )
#첫번째 <p> 태그만 검색하기
#print( soup.find("p") )
#조건검색: <p> 태그 중에서 class 속성이 "outer-text"인 것만 검색하기
#print( soup.find_all("p", class_="outer-text") )
#조건검색: attrs 속성으로 검색하기
#print( soup.find_all("p", attrs={"class":"outer-text"}) )
#id검색: id=first 
#print( soup.find_all(id="first") )
#태그 내부의 문자열: .text 
for tag in soup.find_all("p"):
    title = tag.text.strip() 
    title = title.replace("\n", "")
    print(title)

#문자열처리 메서드와 정규표현식 
strA = "<<< python >>>"
result = strA.strip("<> ")
print(result)
strB = result.replace("python", "python javascript")
print(strB) 
result = "spam ham egg banana".split()
print(result)
print(":)".join(result))

#정규표현식: 특정한 패턴(규칙)문자열
import re

result = re.search(r"\d{4}", "올해는 2026년입니다.")
print(result.group())

result = re.search("apple", "this is apple")
print(result.group())
