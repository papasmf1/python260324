# demoDict.py 

#형식 변환 
a = {1,2,3}
b = tuple(a)
print(b)
c = list(b)
c.append(4)
print(c)

#딕셔너리 형식 연습
color = {"apple":"red", "banana":"yellow"}
print(color)
print(len(color))
#입력 
color["cherry"] = "red"
print(color)
#검색
print(color["apple"])
#삭제
del color["apple"]
print(color)
#반복구문
for item in color.items():
    print(item)