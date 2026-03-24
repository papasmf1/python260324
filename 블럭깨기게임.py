import random
import tkinter as tk


class BreakoutGame:
	def __init__(self, root):
		self.root = root
		self.root.title("블럭깨기 게임")
		self.root.resizable(False, False)

		self.width = 900
		self.height = 650
		self.bg = "#0d1321"

		self.canvas = tk.Canvas(
			self.root,
			width=self.width,
			height=self.height,
			bg=self.bg,
			highlightthickness=0,
		)
		self.canvas.pack()

		self.running = False
		self.left_pressed = False
		self.right_pressed = False

		self.paddle = None
		self.ball = None
		self.bricks = []
		self.items = []
		self.bullets = []
		self.hud_text = None
		self.message_text = None

		self.paddle_speed = 12
		self.ball_radius = 10
		self.ball_speed = 6
		self.dx = 0
		self.dy = 0

		self.score = 0
		self.lives = 3
		self.total_bricks = 0
		self.can_shoot = False
		self.bullet_count = 0

		self._bind_keys()
		self.start_game()

	def _bind_keys(self):
		self.root.bind("<Left>", self._on_left_press)
		self.root.bind("<Right>", self._on_right_press)
		self.root.bind("<KeyRelease-Left>", self._on_left_release)
		self.root.bind("<KeyRelease-Right>", self._on_right_release)
		self.root.bind("<a>", self._on_left_press)
		self.root.bind("<d>", self._on_right_press)
		self.root.bind("<KeyRelease-a>", self._on_left_release)
		self.root.bind("<KeyRelease-d>", self._on_right_release)
		self.root.bind("<space>", self._on_space)
		self.root.bind("<Return>", self._on_space)
		self.root.bind("f", self._on_shoot)
		self.root.bind("<Up>", self._on_shoot)

	def start_game(self):
		self.canvas.delete("all")
		self.running = True
		self.score = 0
		self.lives = 3
		self.bricks = []
		self.items = []
		self.bullets = []
		self.message_text = None
		self.can_shoot = False
		self.bullet_count = 0

		self._create_paddle()
		self._create_ball(reset_only=False)
		self._create_bricks(rows=7, cols=12)
		self._create_hud()

		self.loop()

	def _create_paddle(self):
		paddle_width = 420
		paddle_height = 16
		x1 = (self.width - paddle_width) / 2
		y1 = self.height - 48
		x2 = x1 + paddle_width
		y2 = y1 + paddle_height

		self.paddle = self.canvas.create_rectangle(
			x1, y1, x2, y2, fill="#f6ae2d", outline=""
		)

	def _create_ball(self, reset_only=True):
		if self.ball is not None:
			self.canvas.delete(self.ball)

		px1, py1, px2, _ = self.canvas.coords(self.paddle)
		ball_x = (px1 + px2) / 2
		ball_y = py1 - self.ball_radius - 2

		self.ball = self.canvas.create_oval(
			ball_x - self.ball_radius,
			ball_y - self.ball_radius,
			ball_x + self.ball_radius,
			ball_y + self.ball_radius,
			fill="#e0fbfc",
			outline="",
		)

		direction = random.choice([-1, 1])
		self.dx = direction * self.ball_speed
		self.dy = -self.ball_speed

	def _create_bricks(self, rows, cols):
		top_margin = 70
		side_margin = 30
		gap = 6
		brick_h = 24

		usable_width = self.width - side_margin * 2 - gap * (cols - 1)
		brick_w = usable_width / cols

		palette = [
			"#ff006e",
			"#fb5607",
			"#ffbe0b",
			"#00f5d4",
			"#3a86ff",
			"#8338ec",
			"#ff4d6d",
		]

		for row in range(rows):
			for col in range(cols):
				x1 = side_margin + col * (brick_w + gap)
				y1 = top_margin + row * (brick_h + gap)
				x2 = x1 + brick_w
				y2 = y1 + brick_h
				color = palette[row % len(palette)]

				brick_id = self.canvas.create_rectangle(
					x1, y1, x2, y2, fill=color, outline=""
				)
				self.bricks.append(brick_id)

		self.total_bricks = len(self.bricks)

	def _create_hud(self):
		self.hud_text = self.canvas.create_text(
			12,
			18,
			anchor="w",
			fill="#ffffff",
			font=("Consolas", 14, "bold"),
			text=self._hud_content(),
		)

	def _hud_content(self):
		shoot_status = "ON" if self.can_shoot else "OFF"
		return (
			f"점수: {self.score}   목숨: {self.lives}   남은 블럭: {len(self.bricks)}"
			f"   발사: {shoot_status}   총알: {self.bullet_count}"
		)

	def _update_hud(self):
		self.canvas.itemconfig(self.hud_text, text=self._hud_content())

	def _on_left_press(self, _event):
		self.left_pressed = True

	def _on_right_press(self, _event):
		self.right_pressed = True

	def _on_left_release(self, _event):
		self.left_pressed = False

	def _on_right_release(self, _event):
		self.right_pressed = False

	def _on_space(self, _event):
		if not self.running:
			self.start_game()

	def _on_shoot(self, _event):
		if not self.running:
			return
		if not self.can_shoot or self.bullet_count <= 0:
			return

		px1, py1, px2, _ = self.canvas.coords(self.paddle)
		cx = (px1 + px2) / 2
		bullet = self.canvas.create_rectangle(
			cx - 3, py1 - 14, cx + 3, py1 - 2, fill="#f8f32b", outline=""
		)
		self.bullets.append(bullet)
		self.bullet_count -= 1
		self._update_hud()

	def _move_paddle(self):
		if self.paddle is None:
			return

		move_x = 0
		if self.left_pressed and not self.right_pressed:
			move_x = -self.paddle_speed
		elif self.right_pressed and not self.left_pressed:
			move_x = self.paddle_speed

		if move_x == 0:
			return

		x1, _, x2, _ = self.canvas.coords(self.paddle)
		if x1 + move_x < 0:
			move_x = -x1
		if x2 + move_x > self.width:
			move_x = self.width - x2

		self.canvas.move(self.paddle, move_x, 0)

	def _move_ball(self):
		self.canvas.move(self.ball, self.dx, self.dy)
		x1, y1, x2, y2 = self.canvas.coords(self.ball)

		if x1 <= 0:
			self.dx = abs(self.dx)
		elif x2 >= self.width:
			self.dx = -abs(self.dx)

		if y1 <= 0:
			self.dy = abs(self.dy)

		if y2 >= self.height:
			self.lives -= 1
			self._update_hud()
			if self.lives <= 0:
				self._game_over("게임 오버")
				return
			self._create_ball(reset_only=True)

	def _move_items(self):
		for item in self.items[:]:
			self.canvas.move(item, 0, 4)
			x1, y1, x2, y2 = self.canvas.coords(item)

			if y1 >= self.height:
				self.canvas.delete(item)
				self.items.remove(item)
				continue

			overlap = self.canvas.find_overlapping(x1, y1, x2, y2)
			if self.paddle in overlap:
				self.canvas.delete(item)
				self.items.remove(item)
				self.can_shoot = True
				self.bullet_count += 10
				self._update_hud()

	def _move_bullets(self):
		for bullet in self.bullets[:]:
			self.canvas.move(bullet, 0, -12)
			x1, y1, x2, y2 = self.canvas.coords(bullet)

			if y2 <= 0:
				self.canvas.delete(bullet)
				self.bullets.remove(bullet)
				continue

			overlap = self.canvas.find_overlapping(x1, y1, x2, y2)
			hit_brick = None
			for item in overlap:
				if item in self.bricks:
					hit_brick = item
					break

			if hit_brick is not None:
				self.canvas.delete(bullet)
				self.bullets.remove(bullet)
				self._destroy_brick(hit_brick)

	def _check_collisions(self):
		if not self.running:
			return

		ball_coords = self.canvas.coords(self.ball)
		overlap = self.canvas.find_overlapping(*ball_coords)

		for item in overlap:
			if item == self.ball:
				continue

			if item == self.paddle:
				self._bounce_from_paddle()
				continue

			if item in self.bricks:
				self._hit_brick(item)
				break

	def _bounce_from_paddle(self):
		px1, _, px2, _ = self.canvas.coords(self.paddle)
		bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
		ball_center_x = (bx1 + bx2) / 2
		paddle_center_x = (px1 + px2) / 2
		paddle_half = (px2 - px1) / 2

		# 패들 중심 대비 충돌 위치로 반사 각도를 조금 바꿔 조작감을 높인다.
		offset = (ball_center_x - paddle_center_x) / paddle_half
		offset = max(-1.0, min(1.0, offset))

		self.dx = offset * (self.ball_speed + 2)
		if abs(self.dx) < 1.5:
			self.dx = 1.5 if self.dx >= 0 else -1.5

		self.dy = -abs(self.ball_speed)

		# 패들 내부에 공이 겹쳐 박히는 현상을 막기 위해 살짝 위로 밀어낸다.
		if by2 > self.canvas.coords(self.paddle)[1]:
			overlap_y = by2 - self.canvas.coords(self.paddle)[1]
			self.canvas.move(self.ball, 0, -overlap_y - 1)

	def _hit_brick(self, brick):
		bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
		rx1, ry1, rx2, ry2 = self.canvas.coords(brick)

		overlap_left = bx2 - rx1
		overlap_right = rx2 - bx1
		overlap_top = by2 - ry1
		overlap_bottom = ry2 - by1

		min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

		if min_overlap in (overlap_left, overlap_right):
			self.dx = -self.dx
		else:
			self.dy = -self.dy

		self._destroy_brick(brick)

	def _destroy_brick(self, brick):
		if brick not in self.bricks:
			return

		rx1, ry1, rx2, ry2 = self.canvas.coords(brick)
		cx = (rx1 + rx2) / 2
		cy = (ry1 + ry2) / 2

		self.canvas.delete(brick)
		self.bricks.remove(brick)
		self.score += 10

		# 벽돌이 깨질 때 일정 확률로 총알 아이템을 떨어뜨린다.
		if random.random() < 0.25:
			item = self.canvas.create_oval(
				cx - 10, cy - 10, cx + 10, cy + 10, fill="#80ed99", outline=""
			)
			self.items.append(item)

		self._update_hud()

		if not self.bricks:
			self._game_over("승리! 모든 블럭을 깼습니다")

	def _game_over(self, message):
		self.running = False
		self.message_text = self.canvas.create_text(
			self.width / 2,
			self.height / 2,
			text=f"{message}\n\n이동: 방향키/A,D  |  발사: F 또는 위쪽키\n스페이스 또는 엔터로 다시 시작",
			fill="#ffffff",
			font=("Malgun Gothic", 24, "bold"),
			justify="center",
		)

	def loop(self):
		if self.running:
			self._move_paddle()
			self._move_ball()
			self._move_items()
			self._move_bullets()
			self._check_collisions()
		self.root.after(16, self.loop)


def main():
	root = tk.Tk()
	game = BreakoutGame(root)
	root.mainloop()


if __name__ == "__main__":
	main()
