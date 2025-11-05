from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QTextEdit)
from PyQt5.QtCore import pyqtSignal, Qt
from database import Database

class ClientDialog(QDialog):
    
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Редактирование клиента" if self.client_data else "Новый клиент")
        self.setModal(True)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.surname_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.patronymic_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        
        form.addRow("Фамилия:", self.surname_edit)
        form.addRow("Имя:", self.name_edit)
        form.addRow("Отчество:", self.patronymic_edit)
        form.addRow("Телефон:", self.phone_edit)
        form.addRow("Email:", self.email_edit)
        
        if self.client_data:
            self.surname_edit.setText(self.client_data.get('surname') or '')
            self.name_edit.setText(self.client_data.get('name') or '')
            self.patronymic_edit.setText(self.client_data.get('patronymic') or '')
            self.phone_edit.setText(self.client_data.get('phone') or '')
            self.email_edit.setText(self.client_data.get('email') or '')
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        phone = self.phone_edit.text().strip()
        email = self.email_edit.text().strip()
        
        if not phone and not email:
            QMessageBox.warning(self, "Ошибка", "Необходимо указать хотя бы телефон или email!")
            return
        
        if email and '@' not in email:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат email!")
            return
        
        self.accept()
    
    def get_data(self):
        return {
            'surname': self.surname_edit.text().strip() or None,
            'name': self.name_edit.text().strip() or None,
            'patronymic': self.patronymic_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None,
            'email': self.email_edit.text().strip() or None
        }

class ClientsWidget(QWidget):
    
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
        self.search_edit.setPlaceholderText("Поиск по ФИО, телефону, email...")
        self.search_edit.textChanged.connect(self.refresh_data)
        
        add_btn = QPushButton("➕ Добавить клиента")
        add_btn.clicked.connect(self.add_client)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_client)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_client)
        
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество", "Телефон", "Email"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlaceholderText("Выберите клиента для просмотра связанных данных...")
        layout.addWidget(self.info_text)
        
        self.table.itemSelectionChanged.connect(self.show_client_info)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        search = self.search_edit.text().strip()
        clients = self.db.get_clients(search if search else None)
        
        self.table.setRowCount(len(clients))
        for i, client in enumerate(clients):
            self.table.setItem(i, 0, QTableWidgetItem(str(client['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(client.get('surname') or ''))
            self.table.setItem(i, 2, QTableWidgetItem(client.get('name') or ''))
            self.table.setItem(i, 3, QTableWidgetItem(client.get('patronymic') or ''))
            self.table.setItem(i, 4, QTableWidgetItem(client.get('phone') or ''))
            self.table.setItem(i, 5, QTableWidgetItem(client.get('email') or ''))
            
            for col in range(6):
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_client_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None
    
    def add_client(self):
        dialog = ClientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_client(**data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Клиент успешно добавлен!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить клиента:\n{str(e)}")
    
    def edit_client(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите клиента для редактирования!")
            return
        
        client_data = self.db.get_client(client_id)
        if not client_data:
            QMessageBox.warning(self, "Ошибка", "Клиент не найден!")
            return
        
        dialog = ClientDialog(self, client_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_client(client_id, **data)
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Успех", "Клиент успешно обновлен!")
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить клиента:\n{str(e)}")
    
    def delete_client(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите клиента для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить этого клиента?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.delete_client(client_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Успех", "Клиент успешно удален!")
                else:
                    QMessageBox.warning(
                        self, "Ошибка", 
                        "Нельзя удалить клиента, связанного с предложениями или потребностями!"
                    )
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить клиента:\n{str(e)}")
    
    def show_client_info(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            self.info_text.clear()
            return
        
        info = []
        info.append("=== Связанные данные ===\n")
        
        offers = self.db.get_offers_by_client(client_id)
        info.append(f"Предложения: {len(offers)}")
        for offer in offers[:5]:
            info.append(f"  - Предложение
        if len(offers) > 5:
            info.append(f"  ... и еще {len(offers) - 5}")
        
        info.append("")
        
        demands = self.db.get_demands_by_client(client_id)
        info.append(f"Потребности: {len(demands)}")
        for demand in demands[:5]:
            info.append(f"  - Потребность
        if len(demands) > 5:
            info.append(f"  ... и еще {len(demands) - 5}")
        
        self.info_text.setText("\n".join(info))

