from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QComboBox, QTextEdit, QGroupBox)
from PyQt5.QtCore import pyqtSignal, Qt
from database import Database
from commission_calculator import CommissionCalculator

class DealDialog(QDialog):
    
    def __init__(self, parent=None, deal_data=None, db: Database = None):
        super().__init__(parent)
        self.deal_data = deal_data
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Редактирование сделки" if self.deal_data else "Новая сделка")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.demand_combo = QComboBox()
        demands = self.db.get_demands() if self.db else []
        for demand in demands:
            if not self.db.is_demand_satisfied(demand['id']):
                prop_type = demand.get('property_type', '')
                type_map = {'apartment': 'Квартира', 'house': 'Дом', 'land': 'Земля'}
                text = f"Потребность
                self.demand_combo.addItem(text, demand['id'])
        form.addRow("Потребность *:", self.demand_combo)
        
        self.offer_combo = QComboBox()
        offers = self.db.get_offers() if self.db else []
        for offer in offers:
            if not self.db.is_offer_satisfied(offer['id']):
                prop_type = offer.get('property_type', '')
                type_map = {'apartment': 'Квартира', 'house': 'Дом', 'land': 'Земля'}
                text = f"Предложение
                self.offer_combo.addItem(text, offer['id'])
        form.addRow("Предложение *:", self.offer_combo)
        
        if self.deal_data:
            demand_id = self.deal_data.get('demand_id')
            for i in range(self.demand_combo.count()):
                if self.demand_combo.itemData(i) == demand_id:
                    self.demand_combo.setCurrentIndex(i)
                    break
            
            offer_id = self.deal_data.get('offer_id')
            for i in range(self.offer_combo.count()):
                if self.offer_combo.itemData(i) == offer_id:
                    self.offer_combo.setCurrentIndex(i)
                    break
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'demand_id': self.demand_combo.currentData(),
            'offer_id': self.offer_combo.currentData()
        }

class DealsWidget(QWidget):
    
    data_changed = pyqtSignal()
    
    def __init__(self, db: Database, commission_calculator: CommissionCalculator):
        super().__init__()
        self.db = db
        self.commission_calculator = commission_calculator
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Добавить сделку")
        add_btn.clicked.connect(self.add_deal)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_deal)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_deal)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_data)
        
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "Потребность", "Предложение", "Дата создания"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        self.commission_text = QTextEdit()
        self.commission_text.setReadOnly(True)
        self.commission_text.setMaximumHeight(200)
        self.commission_text.setPlaceholderText("Выберите сделку для просмотра информации о комиссиях...")
        layout.addWidget(self.commission_text)
        
        self.table.itemSelectionChanged.connect(self.show_commission_info)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        deals = self.db.get_deals()
        
        self.table.setRowCount(len(deals))
        for i, deal in enumerate(deals):
            self.table.setItem(i, 0, QTableWidgetItem(str(deal['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(f"Потребность
            self.table.setItem(i, 2, QTableWidgetItem(f"Предложение
            
            created_at = deal.get('created_at', '')
            self.table.setItem(i, 3, QTableWidgetItem(created_at))
            
            for col in range(4):
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_deal_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None
    
    def add_deal(self):
        dialog = DealDialog(self, db=self.db)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                demand = self.db.get_demand(data['demand_id'])
                offer = self.db.get_offer(data['offer_id'])
                
                if not demand or not offer:
                    QMessageBox.warning(self, "Ошибка", "Потребность или предложение не найдены!")
                    return
                
                property_data = self.db.get_property(offer['property_id'])
                if not self.db.check_match(demand, property_data, offer):
                    reply = QMessageBox.warning(
                        self, "Предупреждение",
                        "Предложение не соответствует требованиям потребности!\n"
                        "Все равно создать сделку?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
                
                self.db.add_deal(**data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Сделка успешно создана!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать сделку:\n{str(e)}")
    
    def edit_deal(self):
        deal_id = self.get_selected_deal_id()
        if not deal_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите сделку для редактирования!")
            return
        
        deal_data = self.db.get_deal(deal_id)
        if not deal_data:
            QMessageBox.warning(self, "Ошибка", "Сделка не найдена!")
            return
        
        dialog = DealDialog(self, deal_data, self.db)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_deal(deal_id, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Сделка успешно обновлена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить сделку:\n{str(e)}")
    
    def delete_deal(self):
        deal_id = self.get_selected_deal_id()
        if not deal_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите сделку для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить эту сделку?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_deal(deal_id)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Сделка успешно удалена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить сделку:\n{str(e)}")
    
    def show_commission_info(self):
        deal_id = self.get_selected_deal_id()
        if not deal_id:
            self.commission_text.clear()
            return
        
        deal = self.db.get_deal(deal_id)
        if not deal:
            self.commission_text.clear()
            return
        
        commissions = self.commission_calculator.calculate_deal_commissions(deal, self.db)
        
        info = []
        info.append("=== Расчет комиссий и отчислений ===\n")
        info.append(f"Комиссия для клиента-продавца (арендодателя): {commissions['seller_commission']:.2f} руб")
        info.append(f"Комиссия для клиента-покупателя (арендатора): {commissions['buyer_commission']:.2f} руб")
        info.append("")
        info.append("--- Отчисления ---")
        info.append(f"Риэлтору клиента-продавца: {commissions['seller_realtor_share']:.2f} руб")
        info.append(f"Риэлтору клиента-покупателя: {commissions['buyer_realtor_share']:.2f} руб")
        info.append(f"Компании: {commissions['company_share']:.2f} руб")
        
        self.commission_text.setText("\n".join(info))

