import random
from openpyxl import Workbook


def create_product_excel(file_name: str = "ProductList.xlsx", count: int = 100) -> None:
	wb = Workbook()
	ws = wb.active
	ws.title = "제품목록"

	ws.append(["제품ID", "제품명", "가격", "수량"])

	product_names = [
		"스마트폰",
		"노트북",
		"태블릿",
		"스마트워치",
		"무선이어폰",
		"블루투스스피커",
		"게이밍마우스",
		"기계식키보드",
		"모니터",
		"외장하드",
	]

	for i in range(1, count + 1):
		product_id = f"P{i:03d}"
		product_name = f"{random.choice(product_names)}_{i}"
		price = random.randrange(50000, 3000001, 1000)
		quantity = random.randint(1, 200)

		ws.append([product_id, product_name, price, quantity])

	wb.save(file_name)
	print(f"{file_name} 파일이 생성되었습니다. (총 {count}개 데이터)")


if __name__ == "__main__":
	create_product_excel()
