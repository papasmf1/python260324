# 분기구문.py 
#블럭 주석 처리: ctrl + / 
# score = int(input("점수를 입력:"))

# if 90 <= score <= 100:
#     grade = "A"
# elif 80 <= score < 90:
#     grade = "B"
# elif 70 <= score < 80:
#     grade = "C"
# else:
#     grade = "D"

# print("등급은 ", grade)

value = 5 
while value > 0:
    print(value)
    value -= 1

lst = [100, 3.14, "apple"]
for item in lst:
    print(item)

colors = {"apple":"red", "banana":"yellow", "grape":"purple"}
for item in colors.items():
    print(item)

for k,v in colors.items():
    print(k,v)

print("---range()함수---")
print(list(range(10)))
print(list(range(2000,2027)))
print(list(range(1,32)))
print(list(range(10,0,-1)))

print("---리스트 컴프리헨션---")
lst = [1,2,3,4,5,6,7,8,9,10]
print([i**2 for i in lst if i>5])
tp = ("apple", "banana")
print([len(i) for i in tp])

print("---필터링함수---")
lst = [10, 25, 30]
itemL = filter(None, lst)
for item in itemL:
    print(item)

print("---필터링함수 사용---")
def getBiggerThan20(x):
    return x > 20

itemL = filter(getBiggerThan20, lst)
for item in itemL:
    print(item)

print("---람다함수 사용---")
itemL = filter(lambda x: x > 20, lst)
for item in itemL:
    print(item)
