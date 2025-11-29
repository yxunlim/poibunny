import sys
import random
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QStackedWidget,
    QPushButton, QHBoxLayout
)

from cards_tab import CardsTab


class FeaturedCarousel(QWidget):
    def __init__(self, cards, interval=5000, count=5):
        super().__init__()
        self.cards = random.sample(cards, min(count, len(cards)))
        self.current_index = 0

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Featured Card")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 18px;")
        self.layout.addWidget(self.name_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.desc_label)

        # Rotating every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_card)
        self.timer.start(interval)

        self.update_card()

    def update_card(self):
        if not self.cards:
            self.name_label.setText("No featured cards available.")
            return

        card = self.cards[self.current_index]

        self.name_label.setText(card["name"])
        self.desc_label.setText(card["description"])

        pixmap = QPixmap(card["image_path"])
        if not pixmap.isNull():
            scaled = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)

    def next_card(self):
        self.current_index = (self.current_index + 1) % len(self.cards)
        self.update_card()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Card App")
        self.resize(900, 600)

        self.stack = QStackedWidget()

        # Load full card list from CardsTab
        self.cards_tab = CardsTab()
        self.all_cards = self.cards_tab.cards

        # Main page with featured card carousel
        self.main_page = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_page.setLayout(self.main_layout)

        self.carousel = FeaturedCarousel(self.all_cards)
        self.main_layout.addWidget(self.carousel)

        # Navigation button
        go_cards_btn = QPushButton("Go to Cards")
        go_cards_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.main_layout.addWidget(go_cards_btn)

        # Add pages
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.cards_tab)

        # Final window layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
