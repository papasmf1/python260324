# io는 글자를 담아두는 작은 상자(메모장)처럼 쓸 수 있어요.
import io
# unittest는 "내 코드가 잘 되는지" 자동으로 확인해 주는 도구예요.
import unittest
# redirect_stdout은 print로 나온 글자를 화면 대신 다른 곳에 담게 해줘요.
from contextlib import redirect_stdout


# Person은 "사람"을 나타내는 기본 설계도(클래스)예요.
class Person:
	# __init__은 객체를 만들 때 딱 한 번 자동으로 불려요.
	# id는 번호, name은 이름을 저장해요.
	def __init__(self, id, name):
		# self.id는 "이 사람의 번호"를 뜻해요.
		self.id = id
		# self.name은 "이 사람의 이름"을 뜻해요.
		self.name = name

	# printInfo는 저장된 정보를 화면에 보여주는 함수예요.
	def printInfo(self):
		# f문자열을 쓰면 중괄호 { } 안에 있는 값을 쉽게 넣을 수 있어요.
		print(f"ID: {self.id}, Name: {self.name}")


# Manager는 Person을 물려받은(상속한) 클래스예요.
# 그래서 id, name을 그대로 가지고, title(직함)만 하나 더 가져요.
class Manager(Person):
	# manager를 만들 때 번호, 이름, 직함을 함께 받아요.
	def __init__(self, id, name, title):
		# super().__init__은 부모(Person)의 준비 코드를 먼저 실행해요.
		super().__init__(id, name)
		# self.title은 "이 관리자의 직함"이에요.
		self.title = title

	# 부모의 printInfo를 "관리자용"으로 다시 만들어서 더 자세히 보여줘요.
	def printInfo(self):
		print(f"ID: {self.id}, Name: {self.name}, Title: {self.title}")


# Employee도 Person을 상속받아요.
# id, name은 그대로 쓰고, skill(잘하는 기술)만 추가해요.
class Employee(Person):
	# employee를 만들 때 번호, 이름, 기술을 받아요.
	def __init__(self, id, name, skill):
		# 부모(Person)에서 id, name 준비를 먼저 해요.
		super().__init__(id, name)
		# self.skill은 "이 직원의 기술"이에요.
		self.skill = skill

	# 직원 정보에 맞게 skill까지 함께 출력해요.
	def printInfo(self):
		print(f"ID: {self.id}, Name: {self.name}, Skill: {self.skill}")


# 아래는 "정말 잘 동작하는지" 확인하는 테스트 묶음이에요.
class TestInheritance(unittest.TestCase):
	# print 결과를 글자로 받아서 비교하기 위한 도우미 함수예요.
	def _capture_output(self, obj):
		# 빈 메모장을 하나 만들어요.
		buffer = io.StringIO()
		# 이 안에서는 print가 화면 대신 buffer에 저장돼요.
		with redirect_stdout(buffer):
			# 객체의 printInfo를 실행해요.
			obj.printInfo()
		# 저장된 글자를 꺼내고 양쪽 공백(줄바꿈 포함)을 정리해서 돌려줘요.
		return buffer.getvalue().strip()

	# 1번 테스트: Person의 id가 잘 저장되는지 확인해요.
	def test_01_person_id(self):
		person = Person(1, "Alice")
		self.assertEqual(person.id, 1)

	# 2번 테스트: Person의 name이 잘 저장되는지 확인해요.
	def test_02_person_name(self):
		person = Person(1, "Alice")
		self.assertEqual(person.name, "Alice")

	# 3번 테스트: Person의 printInfo 출력 글자가 맞는지 확인해요.
	def test_03_person_print_info(self):
		person = Person(1, "Alice")
		self.assertEqual(self._capture_output(person), "ID: 1, Name: Alice")

	# 4번 테스트: Manager가 Person의 한 종류인지(상속 관계) 확인해요.
	def test_04_manager_is_person(self):
		manager = Manager(2, "Bob", "Team Lead")
		self.assertIsInstance(manager, Person)

	# 5번 테스트: Manager의 title이 잘 들어갔는지 확인해요.
	def test_05_manager_title(self):
		manager = Manager(2, "Bob", "Team Lead")
		self.assertEqual(manager.title, "Team Lead")

	# 6번 테스트: Manager의 printInfo가 title까지 잘 출력하는지 확인해요.
	def test_06_manager_print_info(self):
		manager = Manager(2, "Bob", "Team Lead")
		self.assertEqual(
			self._capture_output(manager),
			"ID: 2, Name: Bob, Title: Team Lead",
		)

	# 7번 테스트: Employee도 Person의 한 종류인지 확인해요.
	def test_07_employee_is_person(self):
		employee = Employee(3, "Charlie", "Python")
		self.assertIsInstance(employee, Person)

	# 8번 테스트: Employee의 skill이 잘 저장되는지 확인해요.
	def test_08_employee_skill(self):
		employee = Employee(3, "Charlie", "Python")
		self.assertEqual(employee.skill, "Python")

	# 9번 테스트: Employee의 printInfo가 skill까지 잘 보여주는지 확인해요.
	def test_09_employee_print_info(self):
		employee = Employee(3, "Charlie", "Python")
		self.assertEqual(
			self._capture_output(employee),
			"ID: 3, Name: Charlie, Skill: Python",
		)

	# 10번 테스트: Person은 Manager가 아니므로 title이 없어야 맞아요.
	def test_10_person_not_manager_title(self):
		person = Person(4, "Diana")
		self.assertFalse(hasattr(person, "title"))


# 이 파일을 직접 실행하면 테스트를 시작해요.
if __name__ == "__main__":
	unittest.main()
