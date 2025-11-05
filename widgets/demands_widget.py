from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QComboBox, QSpinBox, QGroupBox,
                             QDoubleSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt
from database import Database

class DemandDialog(QDialog):
    
    def __init__(self, parent=None, demand_data=None, db: Database = None):
        super().__init__(parent)
        self.demand_data = demand_data
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Редактирование потребности" if self.demand_data else "Новая потребность")
        self.setModal(True)
        self.resize(500, 600)
        
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
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["apartment", "house", "land"])
        self.type_combo.setItemText(0, "Квартира")
        self.type_combo.setItemText(1, "Дом")
        self.type_combo.setItemText(2, "Земля")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form.addRow("Тип объекта *:", self.type_combo)
        
        address_group = QGroupBox("Адрес")
        address_layout = QFormLayout()
        self.city_edit = QLineEdit()
        self.street_edit = QLineEdit()
        self.house_edit = QLineEdit()
        self.apartment_edit = QLineEdit()
        address_layout.addRow("Город:", self.city_edit)
        address_layout.addRow("Улица:", self.street_edit)
        address_layout.addRow("Номер дома:", self.house_edit)
        address_layout.addRow("Номер квартиры:", self.apartment_edit)
        address_group.setLayout(address_layout)
        form.addRow(address_group)
        
        price_group = QGroupBox("Цена (руб/мес)")
        price_layout = QFormLayout()
        self.min_price_spin = QSpinBox()
        self.min_price_spin.setRange(1, 100000000)
        self.max_price_spin = QSpinBox()
        self.max_price_spin.setRange(1, 100000000)
        price_layout.addRow("Минимальная:", self.min_price_spin)
        price_layout.addRow("Максимальная:", self.max_price_spin)
        price_group.setLayout(price_layout)
        form.addRow(price_group)
        
        period_group = QGroupBox("Срок аренды (мес)")
        period_layout = QFormLayout()
        self.min_period_spin = QSpinBox()
        self.min_period_spin.setRange(1, 1000)
        self.max_period_spin = QSpinBox()
        self.max_period_spin.setRange(1, 1000)
        period_layout.addRow("Минимальный:", self.min_period_spin)
        period_layout.addRow("Максимальный:", self.max_period_spin)
        period_group.setLayout(period_layout)
        form.addRow(period_group)
        
        self.specific_group = QGroupBox("Дополнительные требования")
        self.specific_layout = QFormLayout()
        self.create_specific_fields()
        self.specific_group.setLayout(self.specific_layout)
        form.addRow(self.specific_group)
        
        layout.addLayout(form)
        
        if self.demand_data:
            self.load_data()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def create_specific_fields(self):
        while self.specific_layout.count():
            item = self.specific_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        prop_type = self.type_combo.currentIndex()
        
        if prop_type == 0:
            self.min_area_spin = QDoubleSpinBox()
            self.min_area_spin.setRange(0, 10000)
            self.min_area_spin.setDecimals(2)
            self.min_area_spin.setSuffix(" м²")
            self.min_area_spin.setSpecialValueText("Не указано")
            self.max_area_spin = QDoubleSpinBox()
            self.max_area_spin.setRange(0, 10000)
            self.max_area_spin.setDecimals(2)
            self.max_area_spin.setSuffix(" м²")
            self.max_area_spin.setSpecialValueText("Не указано")
            self.min_rooms_spin = QSpinBox()
            self.min_rooms_spin.setRange(0, 50)
            self.min_rooms_spin.setSpecialValueText("Не указано")
            self.max_rooms_spin = QSpinBox()
            self.max_rooms_spin.setRange(0, 50)
            self.max_rooms_spin.setSpecialValueText("Не указано")
            self.min_floor_spin = QSpinBox()
            self.min_floor_spin.setRange(0, 200)
            self.min_floor_spin.setSpecialValueText("Не указано")
            self.max_floor_spin = QSpinBox()
            self.max_floor_spin.setRange(0, 200)
            self.max_floor_spin.setSpecialValueText("Не указано")
            
            self.specific_layout.addRow("Мин. площадь:", self.min_area_spin)
            self.specific_layout.addRow("Макс. площадь:", self.max_area_spin)
            self.specific_layout.addRow("Мин. комнат:", self.min_rooms_spin)
            self.specific_layout.addRow("Макс. комнат:", self.max_rooms_spin)
            self.specific_layout.addRow("Мин. этаж:", self.min_floor_spin)
            self.specific_layout.addRow("Макс. этаж:", self.max_floor_spin)
        elif prop_type == 1:
            self.min_area_spin = QDoubleSpinBox()
            self.min_area_spin.setRange(0, 10000)
            self.min_area_spin.setDecimals(2)
            self.min_area_spin.setSuffix(" м²")
            self.min_area_spin.setSpecialValueText("Не указано")
            self.max_area_spin = QDoubleSpinBox()
            self.max_area_spin.setRange(0, 10000)
            self.max_area_spin.setDecimals(2)
            self.max_area_spin.setSuffix(" м²")
            self.max_area_spin.setSpecialValueText("Не указано")
            self.min_rooms_spin = QSpinBox()
            self.min_rooms_spin.setRange(0, 50)
            self.min_rooms_spin.setSpecialValueText("Не указано")
            self.max_rooms_spin = QSpinBox()
            self.max_rooms_spin.setRange(0, 50)
            self.max_rooms_spin.setSpecialValueText("Не указано")
            self.min_floors_spin = QSpinBox()
            self.min_floors_spin.setRange(0, 50)
            self.min_floors_spin.setSpecialValueText("Не указано")
            self.max_floors_spin = QSpinBox()
            self.max_floors_spin.setRange(0, 50)
            self.max_floors_spin.setSpecialValueText("Не указано")
            
            self.specific_layout.addRow("Мин. площадь:", self.min_area_spin)
            self.specific_layout.addRow("Макс. площадь:", self.max_area_spin)
            self.specific_layout.addRow("Мин. комнат:", self.min_rooms_spin)
            self.specific_layout.addRow("Макс. комнат:", self.max_rooms_spin)
            self.specific_layout.addRow("Мин. этажей:", self.min_floors_spin)
            self.specific_layout.addRow("Макс. этажей:", self.max_floors_spin)
        elif prop_type == 2:
            self.min_area_spin = QDoubleSpinBox()
            self.min_area_spin.setRange(0, 1000000)
            self.min_area_spin.setDecimals(2)
            self.min_area_spin.setSuffix(" м²")
            self.min_area_spin.setSpecialValueText("Не указано")
            self.max_area_spin = QDoubleSpinBox()
            self.max_area_spin.setRange(0, 1000000)
            self.max_area_spin.setDecimals(2)
            self.max_area_spin.setSuffix(" м²")
            self.max_area_spin.setSpecialValueText("Не указано")
            
            self.specific_layout.addRow("Мин. площадь:", self.min_area_spin)
            self.specific_layout.addRow("Макс. площадь:", self.max_area_spin)
    
    def on_type_changed(self):
        self.create_specific_fields()
    
    def load_data(self):
        if not self.demand_data:
            return
        
        client_id = self.demand_data.get('client_id')
        for i in range(self.client_combo.count()):
            if self.client_combo.itemData(i) == client_id:
                self.client_combo.setCurrentIndex(i)
                break
        
        realtor_id = self.demand_data.get('realtor_id')
        for i in range(self.realtor_combo.count()):
            if self.realtor_combo.itemData(i) == realtor_id:
                self.realtor_combo.setCurrentIndex(i)
                break
        
        prop_type = self.demand_data.get('property_type', 'apartment')
        type_map = {'apartment': 0, 'house': 1, 'land': 2}
        self.type_combo.setCurrentIndex(type_map.get(prop_type, 0))
        self.create_specific_fields()
        
        self.city_edit.setText(self.demand_data.get('city') or '')
        self.street_edit.setText(self.demand_data.get('street') or '')
        self.house_edit.setText(self.demand_data.get('house_number') or '')
        self.apartment_edit.setText(self.demand_data.get('apartment_number') or '')
        
        self.min_price_spin.setValue(self.demand_data.get('min_price', 0))
        self.max_price_spin.setValue(self.demand_data.get('max_price', 0))
        self.min_period_spin.setValue(self.demand_data.get('min_rental_period', 0))
        self.max_period_spin.setValue(self.demand_data.get('max_rental_period', 0))
        
        if prop_type == 'apartment':
            if self.demand_data.get('min_area') is not None:
                self.min_area_spin.setValue(self.demand_data['min_area'])
            if self.demand_data.get('max_area') is not None:
                self.max_area_spin.setValue(self.demand_data['max_area'])
            if self.demand_data.get('min_rooms') is not None:
                self.min_rooms_spin.setValue(self.demand_data['min_rooms'])
            if self.demand_data.get('max_rooms') is not None:
                self.max_rooms_spin.setValue(self.demand_data['max_rooms'])
            if self.demand_data.get('min_floor') is not None:
                self.min_floor_spin.setValue(self.demand_data['min_floor'])
            if self.demand_data.get('max_floor') is not None:
                self.max_floor_spin.setValue(self.demand_data['max_floor'])
        elif prop_type == 'house':
            if self.demand_data.get('min_area') is not None:
                self.min_area_spin.setValue(self.demand_data['min_area'])
            if self.demand_data.get('max_area') is not None:
                self.max_area_spin.setValue(self.demand_data['max_area'])
            if self.demand_data.get('min_rooms') is not None:
                self.min_rooms_spin.setValue(self.demand_data['min_rooms'])
            if self.demand_data.get('max_rooms') is not None:
                self.max_rooms_spin.setValue(self.demand_data['max_rooms'])
            if self.demand_data.get('min_floors') is not None:
                self.min_floors_spin.setValue(self.demand_data['min_floors'])
            if self.demand_data.get('max_floors') is not None:
                self.max_floors_spin.setValue(self.demand_data['max_floors'])
        elif prop_type == 'land':
            if self.demand_data.get('min_area') is not None:
                self.min_area_spin.setValue(self.demand_data['min_area'])
            if self.demand_data.get('max_area') is not None:
                self.max_area_spin.setValue(self.demand_data['max_area'])
    
    def validate_and_accept(self):
        if self.max_price_spin.value() < self.min_price_spin.value():
            QMessageBox.warning(self, "Ошибка", "Максимальная цена должна быть больше или равна минимальной!")
            return
        
        if self.max_period_spin.value() < self.min_period_spin.value():
            QMessageBox.warning(self, "Ошибка", "Максимальный срок должен быть больше или равен минимальному!")
            return
        
        self.accept()
    
    def get_data(self):
        prop_type = ["apartment", "house", "land"][self.type_combo.currentIndex()]
        
        data = {
            'client_id': self.client_combo.currentData(),
            'realtor_id': self.realtor_combo.currentData(),
            'property_type': prop_type,
            'city': self.city_edit.text().strip() or None,
            'street': self.street_edit.text().strip() or None,
            'house_number': self.house_edit.text().strip() or None,
            'apartment_number': self.apartment_edit.text().strip() or None,
            'min_price': self.min_price_spin.value(),
            'max_price': self.max_price_spin.value(),
            'min_rental_period': self.min_period_spin.value(),
            'max_rental_period': self.max_period_spin.value()
        }
        
        if prop_type == 'apartment':
            data['min_area'] = self.min_area_spin.value() if self.min_area_spin.value() > 0 else None
            data['max_area'] = self.max_area_spin.value() if self.max_area_spin.value() > 0 else None
            data['min_rooms'] = self.min_rooms_spin.value() if self.min_rooms_spin.value() > 0 else None
            data['max_rooms'] = self.max_rooms_spin.value() if self.max_rooms_spin.value() > 0 else None
            data['min_floor'] = self.min_floor_spin.value() if self.min_floor_spin.value() > 0 else None
            data['max_floor'] = self.max_floor_spin.value() if self.max_floor_spin.value() > 0 else None
        elif prop_type == 'house':
            data['min_area'] = self.min_area_spin.value() if self.min_area_spin.value() > 0 else None
            data['max_area'] = self.max_area_spin.value() if self.max_area_spin.value() > 0 else None
            data['min_rooms'] = self.min_rooms_spin.value() if self.min_rooms_spin.value() > 0 else None
            data['max_rooms'] = self.max_rooms_spin.value() if self.max_rooms_spin.value() > 0 else None
            data['min_floors'] = self.min_floors_spin.value() if self.min_floors_spin.value() > 0 else None
            data['max_floors'] = self.max_floors_spin.value() if self.max_floors_spin.value() > 0 else None
        elif prop_type == 'land':
            data['min_area'] = self.min_area_spin.value() if self.min_area_spin.value() > 0 else None
            data['max_area'] = self.max_area_spin.value() if self.max_area_spin.value() > 0 else None
        
        return data

class DemandsWidget(QWidget):
    
    data_changed = pyqtSignal()
    
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Добавить потребность")
        add_btn.clicked.connect(self.add_demand)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_demand)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_demand)
        
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
            "ID", "Клиент", "Риэлтор", "Тип", "Цена (мин-макс)", "Срок (мин-макс)"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        demands = self.db.get_demands()
        
        self.table.setRowCount(len(demands))
        for i, demand in enumerate(demands):
            self.table.setItem(i, 0, QTableWidgetItem(str(demand['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(demand.get('client_name', '')))
            self.table.setItem(i, 2, QTableWidgetItem(demand.get('realtor_name', '')))
            
            prop_type = demand.get('property_type', '')
            type_map = {'apartment': 'Квартира', 'house': 'Дом', 'land': 'Земля'}
            self.table.setItem(i, 3, QTableWidgetItem(type_map.get(prop_type, prop_type)))
            
            price_text = f"{demand.get('min_price', 0)} - {demand.get('max_price', 0)}"
            self.table.setItem(i, 4, QTableWidgetItem(price_text))
            
            period_text = f"{demand.get('min_rental_period', 0)} - {demand.get('max_rental_period', 0)}"
            self.table.setItem(i, 5, QTableWidgetItem(period_text))
            
            for col in range(6):
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_demand_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None
    
    def add_demand(self):
        dialog = DemandDialog(self, db=self.db)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_demand(**data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Потребность успешно добавлена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить потребность:\n{str(e)}")
    
    def edit_demand(self):
        demand_id = self.get_selected_demand_id()
        if not demand_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите потребность для редактирования!")
            return
        
        demand_data = self.db.get_demand(demand_id)
        if not demand_data:
            QMessageBox.warning(self, "Ошибка", "Потребность не найдена!")
            return
        
        dialog = DemandDialog(self, demand_data, self.db)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_demand(demand_id, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Потребность успешно обновлена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить потребность:\n{str(e)}")
    
    def delete_demand(self):
        demand_id = self.get_selected_demand_id()
        if not demand_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите потребность для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить эту потребность?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.delete_demand(demand_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Успех", "Потребность успешно удалена!")
                else:
                    QMessageBox.warning(
                        self, "Ошибка", 
                        "Нельзя удалить потребность, участвующую в сделке!"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить потребность:\n{str(e)}")

