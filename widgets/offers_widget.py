from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QComboBox, QSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt
from database import Database

class OfferDialog(QDialog):
    
    def __init__(self, parent=None, offer_data=None, db: Database = None):
        super().__init__(parent)
        self.offer_data = offer_data
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Редактирование предложения" if self.offer_data else "Новое предложение")
        self.setModal(True)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.client_combo = QComboBox()
        clients = self.db.get_clients() if self.db else []
        for client in clients:
            name = f"{client.get('surname') or ''} {client.get('name') or ''} {client.get('patronymic') or ''}".strip()
            if not name:
                name = f"ID: {client['id']}"
            self.client_combo.addItem(name, client['id'])
        form.addRow("Клиент *:", self.client_combo)
        
        self.realtor_combo = QComboBox()
        realtors = self.db.get_realtors() if self.db else []
        for realtor in realtors:
            name = f"{realtor.get('surname')} {realtor.get('name')} {realtor.get('patronymic')}"
            self.realtor_combo.addItem(name, realtor['id'])
        form.addRow("Риэлтор *:", self.realtor_combo)
        
        self.property_combo = QComboBox()
        properties = self.db.get_properties() if self.db else []
        for prop in properties:
            prop_type = {'apartment': 'Квартира', 'house': 'Дом', 'land': 'Земля'}.get(prop['type'], prop['type'])
            address = f"{prop.get('city') or ''}, {prop.get('street') or ''}, {prop.get('house_number') or ''}".strip(', ')
            text = f"{prop_type}
            if address:
                text += f" - {address}"
            self.property_combo.addItem(text, prop['id'])
        form.addRow("Объект недвижимости *:", self.property_combo)
        
        self.price_spin = QSpinBox()
        self.price_spin.setRange(1, 100000000)
        self.price_spin.setSuffix(" руб/мес")
        form.addRow("Цена *:", self.price_spin)
        
        self.rental_period_spin = QSpinBox()
        self.rental_period_spin.setRange(1, 1000)
        self.rental_period_spin.setSuffix(" мес")
        form.addRow("Срок сдачи *:", self.rental_period_spin)
        
        if self.offer_data:
            client_id = self.offer_data.get('client_id')
            for i in range(self.client_combo.count()):
                if self.client_combo.itemData(i) == client_id:
                    self.client_combo.setCurrentIndex(i)
                    break
            
            realtor_id = self.offer_data.get('realtor_id')
            for i in range(self.realtor_combo.count()):
                if self.realtor_combo.itemData(i) == realtor_id:
                    self.realtor_combo.setCurrentIndex(i)
                    break
            
            property_id = self.offer_data.get('property_id')
            for i in range(self.property_combo.count()):
                if self.property_combo.itemData(i) == property_id:
                    self.property_combo.setCurrentIndex(i)
                    break
            
            self.price_spin.setValue(self.offer_data.get('price', 0))
            self.rental_period_spin.setValue(self.offer_data.get('rental_period', 0))
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'client_id': self.client_combo.currentData(),
            'realtor_id': self.realtor_combo.currentData(),
            'property_id': self.property_combo.currentData(),
            'price': self.price_spin.value(),
            'rental_period': self.rental_period_spin.value()
        }

class OffersWidget(QWidget):
    
    data_changed = pyqtSignal()
    
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Добавить предложение")
        add_btn.clicked.connect(self.add_offer)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_offer)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_offer)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_data)
        
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Клиент", "Риэлтор", "Объект", "Цена (руб/мес)", "Срок (мес)"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        offers = self.db.get_offers()
        
        self.table.setRowCount(len(offers))
        for i, offer in enumerate(offers):
            self.table.setItem(i, 0, QTableWidgetItem(str(offer['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(offer.get('client_name', '')))
            self.table.setItem(i, 2, QTableWidgetItem(offer.get('realtor_name', '')))
            
            prop_type = offer.get('property_type', '')
            type_map = {'apartment': 'Квартира', 'house': 'Дом', 'land': 'Земля'}
            self.table.setItem(i, 3, QTableWidgetItem(type_map.get(prop_type, prop_type)))
            
            self.table.setItem(i, 4, QTableWidgetItem(str(offer.get('price', 0))))
            self.table.setItem(i, 5, QTableWidgetItem(str(offer.get('rental_period', 0))))
            
            for col in range(6):
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_offer_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None
    
    def add_offer(self):
        dialog = OfferDialog(self, db=self.db)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_offer(**data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Предложение успешно добавлено!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить предложение:\n{str(e)}")
    
    def edit_offer(self):
        offer_id = self.get_selected_offer_id()
        if not offer_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите предложение для редактирования!")
            return
        
        offer_data = self.db.get_offer(offer_id)
        if not offer_data:
            QMessageBox.warning(self, "Ошибка", "Предложение не найдено!")
            return
        
        dialog = OfferDialog(self, offer_data, self.db)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_offer(offer_id, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Предложение успешно обновлено!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить предложение:\n{str(e)}")
    
    def delete_offer(self):
        offer_id = self.get_selected_offer_id()
        if not offer_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите предложение для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить это предложение?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.delete_offer(offer_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Успех", "Предложение успешно удалено!")
                else:
                    QMessageBox.warning(
                        self, "Ошибка", 
                        "Нельзя удалить предложение, участвующее в сделке!"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить предложение:\n{str(e)}")

