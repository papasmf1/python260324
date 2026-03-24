#내부모듈.py 
import random

print(random.random())
print(random.random())
print(random.uniform(2.0, 5.0))
print([random.randrange(20) for i in range(10)])
print([random.randrange(20) for i in range(10)])
print(random.sample(range(20), 10))
print(random.sample(range(20), 10))
lst = list(range(1,46))
random.shuffle(lst)
print(lst)

#운영체제 정보 
#파일정보 
import os
from os.path import * 
print("운영체제명:", os.name)
#raw string 표기법: r"c:\python313\python.exe"
fileName = "c:\\python313\\python.exe"

if exists(fileName):
    print("파일명:", basename(fileName))
    print("디렉토리명:", dirname(fileName))
    print("파일크기:", getsize(fileName), "bytes")
else:
    print("파일이 존재하지 않습니다.")

