# 상속02.py 
# Person클래스를 정의하는데 id, name변수가 있고 
# printInfo()라는 메서드로 해당 정보를 출력
class Person:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def printInfo(self):
        print(f"ID: {self.id}, Name: {self.name}")

#해당 클래스의 인스턴스를 생성
person1 = Person(1, "Alice")
person1.printInfo()  # ID: 1, Name: Alice




