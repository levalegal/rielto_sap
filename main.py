import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from database import Database
from commission_calculator import CommissionCalculator
from widgets.clients_widget import ClientsWidget
from widgets.realtors_widget import RealtorsWidget
from widgets.properties_widget import PropertiesWidget
from widgets.offers_widget import OffersWidget
from widgets.demands_widget import DemandsWidget
from widgets.deals_widget import DealsWidget

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.commission_calculator = CommissionCalculator()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Информационная система агентства недвижимости")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        title_label = QPushButton("🏠 Информационная система агентства недвижимости")
        title_label.setEnabled(False)
        title_label.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border: none;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(title_label)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #bdc3c7;
            }
        """)
        
        self.clients_widget = ClientsWidget(self.db)
        self.realtors_widget = RealtorsWidget(self.db)
        self.properties_widget = PropertiesWidget(self.db)
        self.offers_widget = OffersWidget(self.db)
        self.demands_widget = DemandsWidget(self.db)
        self.deals_widget = DealsWidget(self.db, self.commission_calculator)
        
        self.tabs.addTab(self.clients_widget, "👥 Клиенты")
        self.tabs.addTab(self.realtors_widget, "👔 Риэлторы")
        self.tabs.addTab(self.properties_widget, "🏘️ Объекты недвижимости")
        self.tabs.addTab(self.offers_widget, "📋 Предложения")
        self.tabs.addTab(self.demands_widget, "🔍 Потребности")
        self.tabs.addTab(self.deals_widget, "💼 Сделки")
        
        main_layout.addWidget(self.tabs)
        
        self.clients_widget.data_changed.connect(self.refresh_all)
        self.realtors_widget.data_changed.connect(self.refresh_all)
        self.properties_widget.data_changed.connect(self.refresh_all)
        self.offers_widget.data_changed.connect(self.refresh_all)
        self.demands_widget.data_changed.connect(self.refresh_all)
        self.deals_widget.data_changed.connect(self.refresh_all)
    
    def refresh_all(self):
        self.clients_widget.refresh_data()
        self.realtors_widget.refresh_data()
        self.properties_widget.refresh_data()
        self.offers_widget.refresh_data()
        self.demands_widget.refresh_data()
        self.deals_widget.refresh_data()
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
