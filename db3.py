import sqlite3
from typing import Iterable, Optional


class ProductDB:
	def __init__(self, db_name: str = "MyProduct.db") -> None:
		self.db_name = db_name
		self.conn = sqlite3.connect(self.db_name)
		self.create_table()

	def create_table(self) -> None:
		query = """
		CREATE TABLE IF NOT EXISTS Products (
			productID INTEGER PRIMARY KEY,
			productName TEXT NOT NULL,
			productPrice INTEGER NOT NULL
		)
		"""
		self.conn.execute(query)
		self.conn.commit()

	def insert_product(self, product_id: int, product_name: str, product_price: int) -> None:
		query = """
		INSERT INTO Products (productID, productName, productPrice)
		VALUES (?, ?, ?)
		"""
		self.conn.execute(query, (product_id, product_name, product_price))
		self.conn.commit()

	def insert_many_products(self, products: Iterable[tuple[int, str, int]]) -> None:
		query = """
		INSERT INTO Products (productID, productName, productPrice)
		VALUES (?, ?, ?)
		"""
		self.conn.executemany(query, products)
		self.conn.commit()

	def update_product(
		self,
		product_id: int,
		new_name: Optional[str] = None,
		new_price: Optional[int] = None,
	) -> int:
		fields = []
		values = []

		if new_name is not None:
			fields.append("productName = ?")
			values.append(new_name)
		if new_price is not None:
			fields.append("productPrice = ?")
			values.append(new_price)

		if not fields:
			return 0

		query = f"UPDATE Products SET {', '.join(fields)} WHERE productID = ?"
		values.append(product_id)
		cursor = self.conn.execute(query, values)
		self.conn.commit()
		return cursor.rowcount

	def delete_product(self, product_id: int) -> int:
		query = "DELETE FROM Products WHERE productID = ?"
		cursor = self.conn.execute(query, (product_id,))
		self.conn.commit()
		return cursor.rowcount

	def select_product(self, product_id: int) -> Optional[tuple[int, str, int]]:
		query = "SELECT productID, productName, productPrice FROM Products WHERE productID = ?"
		cursor = self.conn.execute(query, (product_id,))
		return cursor.fetchone()

	def select_products(self, limit: int = 10) -> list[tuple[int, str, int]]:
		query = "SELECT productID, productName, productPrice FROM Products ORDER BY productID LIMIT ?"
		cursor = self.conn.execute(query, (limit,))
		return cursor.fetchall()

	def count_products(self) -> int:
		query = "SELECT COUNT(*) FROM Products"
		cursor = self.conn.execute(query)
		return cursor.fetchone()[0]

	def seed_sample_data(self, total_count: int = 100_000, batch_size: int = 1_000) -> None:
		# 이미 데이터가 있으면 중복 입력을 피하기 위해 추가 생성하지 않습니다.
		if self.count_products() >= total_count:
			return

		self.conn.execute("DELETE FROM Products")
		self.conn.commit()

		insert_query = """
		INSERT INTO Products (productID, productName, productPrice)
		VALUES (?, ?, ?)
		"""

		for start_id in range(1, total_count + 1, batch_size):
			end_id = min(start_id + batch_size - 1, total_count)
			batch = [
				(pid, f"전자제품{pid:06d}", 10000 + (pid % 5000) * 10)
				for pid in range(start_id, end_id + 1)
			]
			self.conn.executemany(insert_query, batch)

		self.conn.commit()

	def close(self) -> None:
		self.conn.close()


if __name__ == "__main__":
	db = ProductDB("MyProduct.db")

	# 10만 건 샘플 데이터 생성
	db.seed_sample_data(total_count=100_000)

	# INSERT 예시
	db.insert_product(100001, "한정판이어폰", 159000)

	# UPDATE 예시
	updated_rows = db.update_product(100001, new_price=149000)
	print("UPDATE 적용 행 수:", updated_rows)

	# SELECT 예시
	one_product = db.select_product(100001)
	print("단일 조회:", one_product)

	first_five = db.select_products(limit=5)
	print("상위 5개 조회:", first_five)

	# DELETE 예시
	deleted_rows = db.delete_product(100001)
	print("DELETE 적용 행 수:", deleted_rows)

	print("전체 데이터 수:", db.count_products())
	db.close()