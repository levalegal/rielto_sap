from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QComboBox, QDoubleSpinBox, QSpinBox,
                             QGroupBox)
from PyQt5.QtCore import pyqtSignal, Qt
from database import Database

class PropertyDialog(QDialog):
    
    def __init__(self, parent=None, property_data=None):
        super().__init__(parent)
        self.property_data = property_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Редактирование объекта" if self.property_data else "Новый объект")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
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
        
        coord_group = QGroupBox("Координаты")
        coord_layout = QFormLayout()
        self.latitude_spin = QDoubleSpinBox()
        self.latitude_spin.setRange(-90, 90)
        self.latitude_spin.setDecimals(6)
        self.latitude_spin.setSpecialValueText("Не указано")
        self.longitude_spin = QDoubleSpinBox()
        self.longitude_spin.setRange(-180, 180)
        self.longitude_spin.setDecimals(6)
        self.longitude_spin.setSpecialValueText("Не указано")
        coord_layout.addRow("Широта:", self.latitude_spin)
        coord_layout.addRow("Долгота:", self.longitude_spin)
        coord_group.setLayout(coord_layout)
        form.addRow(coord_group)
        
        self.specific_group = QGroupBox("Характеристики")
        self.specific_layout = QFormLayout()
        self.create_specific_fields()
        self.specific_group.setLayout(self.specific_layout)
        form.addRow(self.specific_group)
        
        layout.addLayout(form)
        
        if self.property_data:
            self.load_data()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def create_specific_fields(self):
        while self.specific_layout.count():
            item = self.specific_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        prop_type = self.type_combo.currentData() if hasattr(self.type_combo, 'currentData') else self.type_combo.currentText()
        
        if prop_type == "apartment" or prop_type == 0:
            self.floor_spin = QSpinBox()
            self.floor_spin.setRange(0, 200)
            self.floor_spin.setSpecialValueText("Не указано")
            self.rooms_spin = QSpinBox()
            self.rooms_spin.setRange(0, 50)
            self.rooms_spin.setSpecialValueText("Не указано")
            self.area_spin = QDoubleSpinBox()
            self.area_spin.setRange(0, 10000)
            self.area_spin.setDecimals(2)
            self.area_spin.setSuffix(" м²")
            self.area_spin.setSpecialValueText("Не указано")
            
            self.specific_layout.addRow("Этаж:", self.floor_spin)
            self.specific_layout.addRow("Количество комнат:", self.rooms_spin)
            self.specific_layout.addRow("Площадь:", self.area_spin)
        elif prop_type == "house" or prop_type == 1:
            self.floors_spin = QSpinBox()
            self.floors_spin.setRange(0, 50)
            self.floors_spin.setSpecialValueText("Не указано")
            self.rooms_spin = QSpinBox()
            self.rooms_spin.setRange(0, 50)
            self.rooms_spin.setSpecialValueText("Не указано")
            self.area_spin = QDoubleSpinBox()
            self.area_spin.setRange(0, 10000)
            self.area_spin.setDecimals(2)
            self.area_spin.setSuffix(" м²")
            self.area_spin.setSpecialValueText("Не указано")
            
            self.specific_layout.addRow("Этажность:", self.floors_spin)
            self.specific_layout.addRow("Количество комнат:", self.rooms_spin)
            self.specific_layout.addRow("Площадь:", self.area_spin)
        elif prop_type == "land" or prop_type == 2:
            self.area_spin = QDoubleSpinBox()
            self.area_spin.setRange(0, 1000000)
            self.area_spin.setDecimals(2)
            self.area_spin.setSuffix(" м²")
            self.area_spin.setSpecialValueText("Не указано")
            
            self.specific_layout.addRow("Площадь:", self.area_spin)
    
    def on_type_changed(self):
        self.create_specific_fields()
    
    def load_data(self):
        if not self.property_data:
            return
        
        prop_type = self.property_data.get('type', 'apartment')
        type_map = {'apartment': 0, 'house': 1, 'land': 2}
        self.type_combo.setCurrentIndex(type_map.get(prop_type, 0))
        self.create_specific_fields()
        
        self.city_edit.setText(self.property_data.get('city') or '')
        self.street_edit.setText(self.property_data.get('street') or '')
        self.house_edit.setText(self.property_data.get('house_number') or '')
        self.apartment_edit.setText(self.property_data.get('apartment_number') or '')
        
        lat = self.property_data.get('latitude')
        lon = self.property_data.get('longitude')
        if lat is not None:
            self.latitude_spin.setValue(lat)
        if lon is not None:
            self.longitude_spin.setValue(lon)
        
        if prop_type == 'apartment':
            if self.property_data.get('floor') is not None:
                self.floor_spin.setValue(self.property_data['floor'])
            if self.property_data.get('rooms') is not None:
                self.rooms_spin.setValue(self.property_data['rooms'])
            if self.property_data.get('area') is not None:
                self.area_spin.setValue(self.property_data['area'])
        elif prop_type == 'house':
            if self.property_data.get('floors') is not None:
                self.floors_spin.setValue(self.property_data['floors'])
            if self.property_data.get('rooms') is not None:
                self.rooms_spin.setValue(self.property_data['rooms'])
            if self.property_data.get('area') is not None:
                self.area_spin.setValue(self.property_data['area'])
        elif prop_type == 'land':
            if self.property_data.get('area') is not None:
                self.area_spin.setValue(self.property_data['area'])
    
    def get_data(self):
        prop_type = ["apartment", "house", "land"][self.type_combo.currentIndex()]
        
        data = {
            'property_type': prop_type,
            'city': self.city_edit.text().strip() or None,
            'street': self.street_edit.text().strip() or None,
            'house_number': self.house_edit.text().strip() or None,
            'apartment_number': self.apartment_edit.text().strip() or None,
            'latitude': self.latitude_spin.value() if self.latitude_spin.value() != 0 else None,
            'longitude': self.longitude_spin.value() if self.longitude_spin.value() != 0 else None
        }
        
        if prop_type == 'apartment':
            data['floor'] = self.floor_spin.value() if self.floor_spin.value() > 0 else None
            data['rooms'] = self.rooms_spin.value() if self.rooms_spin.value() > 0 else None
            data['area'] = self.area_spin.value() if self.area_spin.value() > 0 else None
        elif prop_type == 'house':
            data['floors'] = self.floors_spin.value() if self.floors_spin.value() > 0 else None
            data['rooms'] = self.rooms_spin.value() if self.rooms_spin.value() > 0 else None
            data['area'] = self.area_spin.value() if self.area_spin.value() > 0 else None
        elif prop_type == 'land':
            data['area'] = self.area_spin.value() if self.area_spin.value() > 0 else None
        
        return data

class PropertiesWidget(QWidget):
    
    data_changed = pyqtSignal()
    
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "Квартира", "Дом", "Земля"])
        self.type_filter.currentIndexChanged.connect(self.refresh_data)
        
        self.city_filter = QLineEdit()
        self.city_filter.setPlaceholderText("Фильтр по городу...")
        self.city_filter.textChanged.connect(self.refresh_data)
        
        self.street_filter = QLineEdit()
        self.street_filter.setPlaceholderText("Фильтр по улице...")
        self.street_filter.textChanged.connect(self.refresh_data)
        
        add_btn = QPushButton("➕ Добавить объект")
        add_btn.clicked.connect(self.add_property)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_property)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_property)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_data)
        
        toolbar.addWidget(QLabel("Тип:"))
        toolbar.addWidget(self.type_filter)
        toolbar.addWidget(QLabel("Город:"))
        toolbar.addWidget(self.city_filter)
        toolbar.addWidget(QLabel("Улица:"))
        toolbar.addWidget(self.street_filter)
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Тип", "Город", "Улица", "Дом", "Квартира", "Характеристики", "Координаты"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        type_filter = None
        type_index = self.type_filter.currentIndex()
        if type_index > 0:
            type_map = {1: 'apartment', 2: 'house', 3: 'land'}
            type_filter = type_map[type_index]
        
        city = self.city_filter.text().strip() or None
        street = self.street_filter.text().strip() or None
        
        properties = self.db.get_properties(type_filter, city, street)
        
        self.table.setRowCount(len(properties))
        for i, prop in enumerate(properties):
            self.table.setItem(i, 0, QTableWidgetItem(str(prop['id'])))
            
            type_map = {'apartment': 'Квартира', 'house': 'Дом', 'land': 'Земля'}
            self.table.setItem(i, 1, QTableWidgetItem(type_map.get(prop['type'], prop['type'])))
            
            self.table.setItem(i, 2, QTableWidgetItem(prop.get('city') or ''))
            self.table.setItem(i, 3, QTableWidgetItem(prop.get('street') or ''))
            self.table.setItem(i, 4, QTableWidgetItem(prop.get('house_number') or ''))
            self.table.setItem(i, 5, QTableWidgetItem(prop.get('apartment_number') or ''))
            
            char_text = []
            if prop['type'] == 'apartment':
                if prop.get('floor'):
                    char_text.append(f"Этаж: {prop['floor']}")
                if prop.get('rooms'):
                    char_text.append(f"Комнат: {prop['rooms']}")
                if prop.get('area'):
                    char_text.append(f"Пл: {prop['area']} м²")
            elif prop['type'] == 'house':
                if prop.get('floors'):
                    char_text.append(f"Этажей: {prop['floors']}")
                if prop.get('rooms'):
                    char_text.append(f"Комнат: {prop['rooms']}")
                if prop.get('area'):
                    char_text.append(f"Пл: {prop['area']} м²")
            elif prop['type'] == 'land':
                if prop.get('area'):
                    char_text.append(f"Пл: {prop['area']} м²")
            self.table.setItem(i, 6, QTableWidgetItem(", ".join(char_text)))
            
            coord_text = ""
            if prop.get('latitude') and prop.get('longitude'):
                coord_text = f"{prop['latitude']:.4f}, {prop['longitude']:.4f}"
            self.table.setItem(i, 7, QTableWidgetItem(coord_text))
            
            for col in range(8):
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_property_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None
    
    def add_property(self):
        dialog = PropertyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                prop_type = data.pop('property_type')
                self.db.add_property(prop_type, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Объект успешно добавлен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить объект:\n{str(e)}")
    
    def edit_property(self):
        property_id = self.get_selected_property_id()
        if not property_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите объект для редактирования!")
            return
        
        property_data = self.db.get_property(property_id)
        if not property_data:
            QMessageBox.warning(self, "Ошибка", "Объект не найден!")
            return
        
        dialog = PropertyDialog(self, property_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                property_id = property_data['id']
                prop_type = data.pop('property_type')
                self.db.update_property(property_id, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Объект успешно обновлен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить объект:\n{str(e)}")
    
    def delete_property(self):
        property_id = self.get_selected_property_id()
        if not property_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите объект для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить этот объект?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.delete_property(property_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Успех", "Объект успешно удален!")
                else:
                    QMessageBox.warning(
                        self, "Ошибка", 
                        "Нельзя удалить объект, связанный с предложениями!"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить объект:\n{str(e)}")

