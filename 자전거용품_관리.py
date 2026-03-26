import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QGroupBox, QFormLayout, QStatusBar,
    QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QGradient, QPixmap, QIcon
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


DB_NAME = "bicycle_products.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS MyProduct (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT    NOT NULL,
                price INTEGER NOT NULL
            )
        """)
        conn.commit()


# ── 전역 스타일시트 ──────────────────────────────────────────────────
APP_STYLE = """
    QMainWindow, QWidget#central {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0D1B2A,
            stop:0.5 #1A2744,
            stop:1 #0A0E1A
        );
    }
    QGroupBox {
        color: #00E5FF;
        font-size: 11pt;
        font-weight: bold;
        border: 2px solid #00B8D4;
        border-radius: 12px;
        margin-top: 14px;
        padding-top: 8px;
        background: rgba(0, 180, 212, 0.06);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 12px;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #006064, stop:1 #00B8D4
        );
        border-radius: 6px;
        color: #FFFFFF;
        letter-spacing: 1px;
    }
    QLabel {
        color: #B0BEC5;
        font-size: 10pt;
    }
    QLineEdit {
        background-color: #132035;
        color: #E0F7FA;
        border: 1.5px solid #37474F;
        border-radius: 8px;
        padding: 7px 12px;
        font-size: 10pt;
        selection-background-color: #00B8D4;
    }
    QLineEdit:focus {
        border: 1.5px solid #00E5FF;
        background-color: #1A2E45;
        color: #FFFFFF;
    }
    QLineEdit::placeholder {
        color: #546E7A;
    }
    QScrollBar:vertical {
        background: #132035;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #00B8D4;
        min-height: 30px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QStatusBar {
        background: #0A0E1A;
        color: #546E7A;
        font-size: 9pt;
        border-top: 1px solid #1E2A3A;
    }
"""

BTN_STYLE = """
    QPushButton {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {c1}, stop:1 {c2}
        );
        color: #FFFFFF;
        border: 1px solid {border};
        border-radius: 8px;
        padding: 9px 20px;
        font-size: 10pt;
        font-weight: bold;
        letter-spacing: 0.5px;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {hv1}, stop:1 {hv2}
        );
        border: 1px solid {hvborder};
    }}
    QPushButton:pressed {{
        background: {pressed};
        padding-top: 11px;
        padding-bottom: 7px;
    }}
"""


def make_shadow(radius=18, color="#00E5FF", x=0, y=4):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setColor(QColor(color))
    shadow.setOffset(x, y)
    return shadow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚴 자전거 용품 관리 시스템")
        self.setMinimumSize(820, 660)
        self.setStyleSheet(APP_STYLE)

        # ── 상태바 ────────────────────────────────────────────────
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비")

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 16, 20, 16)

        # ── 타이틀 헤더 ───────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #006064, stop:0.4 #0097A7,
                    stop:0.7 #00ACC1, stop:1 #006064
                );
                border-radius: 12px;
            }
        """)
        header_frame.setFixedHeight(68)
        header_frame.setGraphicsEffect(make_shadow(30, "#00E5FF", 0, 6))

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        icon_label = QLabel("🚴")
        icon_label.setStyleSheet("font-size: 28pt; background: transparent;")

        title_label = QLabel("자전거 용품 관리 시스템")
        title_label.setStyleSheet("""
            font-size: 20pt;
            font-weight: bold;
            color: #FFFFFF;
            letter-spacing: 2px;
            background: transparent;
        """)

        sub_label = QLabel("Bicycle Product Manager")
        sub_label.setStyleSheet("""
            font-size: 9pt;
            color: #B2EBF2;
            background: transparent;
        """)
        sub_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(icon_label)
        header_layout.addSpacing(10)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(sub_label)
        main_layout.addWidget(header_frame)

        # ── 입력 폼 ──────────────────────────────────────────────
        form_group = QGroupBox("  상품 정보 입력")
        form_group.setGraphicsEffect(make_shadow(20, "#00B8D4", 0, 3))
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(20, 20, 20, 16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("수정/삭제 시 ID 입력")
        self.id_edit.setFixedWidth(130)
        self.id_edit.setFixedHeight(36)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("상품명을 입력하세요")
        self.name_edit.setFixedHeight(36)

        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("가격을 입력하세요 (숫자만)")
        self.price_edit.setFixedHeight(36)

        lbl_style = "color: #80DEEA; font-size: 10pt; font-weight: bold;"
        id_lbl    = QLabel("🔑  ID (수정/삭제용):")
        name_lbl  = QLabel("📦  상품명:")
        price_lbl = QLabel("💰  가격 (원):")
        for lbl in (id_lbl, name_lbl, price_lbl):
            lbl.setStyleSheet(lbl_style)

        form_layout.addRow(id_lbl,    self.id_edit)
        form_layout.addRow(name_lbl,  self.name_edit)
        form_layout.addRow(price_lbl, self.price_edit)
        main_layout.addWidget(form_group)

        # ── 버튼 영역 ────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_defs = [
            ("btn_insert", "➕  입력",   "#00897B", "#00695C", "#26A69A", "#4DB6AC", "#00796B"),
            ("btn_update", "✏️  수정",   "#1976D2", "#1565C0", "#2196F3", "#42A5F5", "#0D47A1"),
            ("btn_delete", "🗑️  삭제",   "#E53935", "#C62828", "#EF5350", "#FF7043", "#B71C1C"),
            ("btn_search", "🔍  검색",   "#F57C00", "#E65100", "#FB8C00", "#FFA726", "#BF360C"),
            ("btn_clear",  "📋  전체 목록","#5E35B1", "#4527A0", "#7E57C2", "#9575CD", "#311B92"),
        ]
        self._buttons = []
        for attr, label, c1, c2, hv1, hv2, pressed in btn_defs:
            btn = QPushButton(label)
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(BTN_STYLE.format(
                c1=c1, c2=c2, border=hv1,
                hv1=hv1, hv2=hv2, hvborder="#FFFFFF",
                pressed=pressed
            ))
            btn.setGraphicsEffect(make_shadow(14, c1, 0, 3))
            setattr(self, attr, btn)
            btn_layout.addWidget(btn)
        main_layout.addLayout(btn_layout)

        # ── 테이블 ───────────────────────────────────────────────
        table_group = QGroupBox("  상품 목록")
        table_group.setGraphicsEffect(make_shadow(20, "#00B8D4", 0, 3))
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(12, 16, 12, 12)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["  ID  ", "상품명", "가격 (원)"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setRowHeight(0, 36)
        self.table.horizontalHeader().setDefaultSectionSize(100)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0D1B2A;
                alternate-background-color: #132035;
                color: #E0F7FA;
                font-size: 10pt;
                border: none;
                gridline-color: transparent;
                selection-background-color: rgba(0, 229, 255, 0.22);
                selection-color: #FFFFFF;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid #1A2744;
            }
            QTableWidget::item:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,188,212,0.35),
                    stop:1 rgba(0,229,255,0.15)
                );
                color: #FFFFFF;
                border-left: 3px solid #00E5FF;
            }
            QTableWidget::item:hover {
                background: rgba(0, 188, 212, 0.12);
            }
            QHeaderView::section {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #006064, stop:1 #00838F
                );
                color: #E0F7FA;
                font-weight: bold;
                font-size: 10pt;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #004D40;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 6px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 6px;
                border-right: none;
            }
        """)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_group)

        # ── 시그널 연결 ──────────────────────────────────────────
        self.btn_insert.clicked.connect(self.insert_product)
        self.btn_update.clicked.connect(self.update_product)
        self.btn_delete.clicked.connect(self.delete_product)
        self.btn_search.clicked.connect(self.search_product)
        self.btn_clear.clicked.connect(self.load_all)
        self.table.cellClicked.connect(self.on_row_clicked)

        self.load_all()

    # ── DB 헬퍼 ─────────────────────────────────────────────────
    def load_all(self):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, name, price FROM MyProduct ORDER BY id"
            ).fetchall()
        self._populate_table(rows)
        self.status_bar.showMessage(f"총 {len(rows)}개 상품")

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 38)
            for col, value in enumerate(row_data):
                if col == 2:
                    display = f"{int(value):,} 원"
                else:
                    display = str(value)
                item = QTableWidgetItem(display)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col, item)

    # ── CRUD ────────────────────────────────────────────────────
    def insert_product(self):
        name  = self.name_edit.text().strip()
        price = self.price_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "입력 오류", "상품명을 입력해주세요.")
            return
        if not self._is_valid_price(price):
            QMessageBox.warning(self, "입력 오류", "가격은 0 이상의 숫자여야 합니다.")
            return

        with get_connection() as conn:
            conn.execute(
                "INSERT INTO MyProduct (name, price) VALUES (?, ?)",
                (name, int(price))
            )
            conn.commit()

        QMessageBox.information(self, "완료", f"'{name}' 상품이 등록되었습니다.")
        self.status_bar.showMessage(f"'{name}' 상품 등록 완료")
        self._clear_form()
        self.load_all()

    def update_product(self):
        prod_id = self.id_edit.text().strip()
        name    = self.name_edit.text().strip()
        price   = self.price_edit.text().strip()

        if not prod_id.isdigit():
            QMessageBox.warning(self, "입력 오류", "수정할 상품의 ID를 입력해주세요.")
            return
        if not name:
            QMessageBox.warning(self, "입력 오류", "상품명을 입력해주세요.")
            return
        if not self._is_valid_price(price):
            QMessageBox.warning(self, "입력 오류", "가격은 0 이상의 숫자여야 합니다.")
            return

        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE MyProduct SET name=?, price=? WHERE id=?",
                (name, int(price), int(prod_id))
            )
            conn.commit()
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "없는 ID", f"ID {prod_id}에 해당하는 상품이 없습니다.")
                return

        QMessageBox.information(self, "완료", f"ID {prod_id} 상품이 수정되었습니다.")
        self.status_bar.showMessage(f"ID {prod_id} 상품 수정 완료")
        self._clear_form()
        self.load_all()

    def delete_product(self):
        prod_id = self.id_edit.text().strip()

        if not prod_id.isdigit():
            QMessageBox.warning(self, "입력 오류", "삭제할 상품의 ID를 입력해주세요.")
            return

        reply = QMessageBox.question(
            self, "삭제 확인",
            f"ID {prod_id} 상품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM MyProduct WHERE id=?", (int(prod_id),)
            )
            conn.commit()
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "없는 ID", f"ID {prod_id}에 해당하는 상품이 없습니다.")
                return

        QMessageBox.information(self, "완료", f"ID {prod_id} 상품이 삭제되었습니다.")
        self.status_bar.showMessage(f"ID {prod_id} 상품 삭제 완료")
        self._clear_form()
        self.load_all()

    def search_product(self):
        keyword = self.name_edit.text().strip()

        if not keyword:
            QMessageBox.warning(self, "입력 오류", "검색할 상품명을 입력해주세요.")
            return

        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, name, price FROM MyProduct WHERE name LIKE ? ORDER BY id",
                (f"%{keyword}%",)
            ).fetchall()

        if rows:
            self._populate_table(rows)
            self.status_bar.showMessage(f"'{keyword}' 검색 결과: {len(rows)}개")
        else:
            QMessageBox.information(self, "검색 결과", f"'{keyword}'에 해당하는 상품이 없습니다.")
            self.load_all()

    # ── 유틸 ────────────────────────────────────────────────────
    def on_row_clicked(self, row, _col):
        id_item    = self.table.item(row, 0)
        name_item  = self.table.item(row, 1)
        price_item = self.table.item(row, 2)
        if id_item:
            self.id_edit.setText(id_item.text())
        if name_item:
            self.name_edit.setText(name_item.text())
        if price_item:
            self.price_edit.setText(price_item.text())

    def _clear_form(self):
        self.id_edit.clear()
        self.name_edit.clear()
        self.price_edit.clear()

    @staticmethod
    def _is_valid_price(value: str) -> bool:
        try:
            return int(value) >= 0
        except ValueError:
            return False


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setFont(QFont("맑은 고딕", 10))
    # 전체 앱 다크 팔레트 적용
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#0D1B2A"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#E0F7FA"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#132035"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#1A2744"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#E0F7FA"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#00B8D4"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
