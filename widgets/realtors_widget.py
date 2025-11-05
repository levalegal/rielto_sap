from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QDoubleSpinBox, QTextEdit)
from PyQt5.QtCore import pyqtSignal, Qt
from database import Database

class RealtorDialog(QDialog):
    
    def __init__(self, parent=None, realtor_data=None):
        super().__init__(parent)
        self.realtor_data = realtor_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Редактирование риэлтора" if self.realtor_data else "Новый риэлтор")
        self.setModal(True)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.surname_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.patronymic_edit = QLineEdit()
        self.commission_spin = QDoubleSpinBox()
        self.commission_spin.setRange(0, 100)
        self.commission_spin.setSuffix(" %")
        self.commission_spin.setSpecialValueText("По умолчанию (45%)")
        
        form.addRow("Фамилия *:", self.surname_edit)
        form.addRow("Имя *:", self.name_edit)
        form.addRow("Отчество *:", self.patronymic_edit)
        form.addRow("Доля от комиссии:", self.commission_spin)
        
        if self.realtor_data:
            self.surname_edit.setText(self.realtor_data.get('surname') or '')
            self.name_edit.setText(self.realtor_data.get('name') or '')
            self.patronymic_edit.setText(self.realtor_data.get('patronymic') or '')
            commission = self.realtor_data.get('commission_share')
            if commission is not None:
                self.commission_spin.setValue(commission)
            else:
                self.commission_spin.setValue(0)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        surname = self.surname_edit.text().strip()
        name = self.name_edit.text().strip()
        patronymic = self.patronymic_edit.text().strip()
        
        if not surname or not name or not patronymic:
            QMessageBox.warning(self, "Ошибка", "Необходимо указать фамилию, имя и отчество!")
            return
        
        self.accept()
    
    def get_data(self):
        commission = self.commission_spin.value()
        return {
            'surname': self.surname_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'patronymic': self.patronymic_edit.text().strip(),
            'commission_share': commission if commission > 0 else None
        }

class RealtorsWidget(QWidget):
    
    data_changed = pyqtSignal()
    
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по ФИО...")
        self.search_edit.textChanged.connect(self.refresh_data)
        
        add_btn = QPushButton("➕ Добавить риэлтора")
        add_btn.clicked.connect(self.add_realtor)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_realtor)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_realtor)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_data)
        
        toolbar.addWidget(QLabel("Поиск:"))
        toolbar.addWidget(self.search_edit)
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество", "Доля от комиссии (%)"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlaceholderText("Выберите риэлтора для просмотра связанных данных...")
        layout.addWidget(self.info_text)
        
        self.table.itemSelectionChanged.connect(self.show_realtor_info)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        search = self.search_edit.text().strip()
        realtors = self.db.get_realtors(search if search else None)
        
        self.table.setRowCount(len(realtors))
        for i, realtor in enumerate(realtors):
            self.table.setItem(i, 0, QTableWidgetItem(str(realtor['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(realtor.get('surname') or ''))
            self.table.setItem(i, 2, QTableWidgetItem(realtor.get('name') or ''))
            self.table.setItem(i, 3, QTableWidgetItem(realtor.get('patronymic') or ''))
            commission = realtor.get('commission_share')
            commission_text = f"{commission:.1f}" if commission else "45.0 (по умолчанию)"
            self.table.setItem(i, 4, QTableWidgetItem(commission_text))
            
            for col in range(5):
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_realtor_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None
    
    def add_realtor(self):
        dialog = RealtorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_realtor(**data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Риэлтор успешно добавлен!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить риэлтора:\n{str(e)}")
    
    def edit_realtor(self):
        realtor_id = self.get_selected_realtor_id()
        if not realtor_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите риэлтора для редактирования!")
            return
        
        realtor_data = self.db.get_realtor(realtor_id)
        if not realtor_data:
            QMessageBox.warning(self, "Ошибка", "Риэлтор не найден!")
            return
        
        dialog = RealtorDialog(self, realtor_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_realtor(realtor_id, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Риэлтор успешно обновлен!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить риэлтора:\n{str(e)}")
    
    def delete_realtor(self):
        realtor_id = self.get_selected_realtor_id()
        if not realtor_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите риэлтора для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить этого риэлтора?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.delete_realtor(realtor_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Успех", "Риэлтор успешно удален!")
                else:
                    QMessageBox.warning(
                        self, "Ошибка", 
                        "Нельзя удалить риэлтора, связанного с предложениями или потребностями!"
                    )
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить риэлтора:\n{str(e)}")
    
    def show_realtor_info(self):
        realtor_id = self.get_selected_realtor_id()
        if not realtor_id:
            self.info_text.clear()
            return
        
        info = []
        info.append("=== Связанные данные ===\n")
        
        offers = self.db.get_offers_by_realtor(realtor_id)
        info.append(f"Предложения: {len(offers)}")
        for offer in offers[:5]:
            info.append(f"  - Предложение
        if len(offers) > 5:
            info.append(f"  ... и еще {len(offers) - 5}")
        
        info.append("")
        
        demands = self.db.get_demands_by_realtor(realtor_id)
        info.append(f"Потребности: {len(demands)}")
        for demand in demands[:5]:
            info.append(f"  - Потребность
        if len(demands) > 5:
            info.append(f"  ... и еще {len(demands) - 5}")
        
        self.info_text.setText("\n".join(info))

