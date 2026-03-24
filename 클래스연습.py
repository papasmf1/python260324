# 클래스연습.py 

#1)클래스를 정의
class Person:
    #초기화 메서드
    def __init__(self):
        self.name = "default name"
    def print(self):
        print("My name is {0}".format(self.name))

#2)객체 생성
p1 = Person()
p2 = Person() 

p1.name = "전우치" 
p1.print() 
p2.print()