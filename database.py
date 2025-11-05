import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Database:
    
    def __init__(self, db_path: str = "real_estate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                surname TEXT NOT NULL,
                name TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                commission_share REAL DEFAULT 45.0,
                CHECK(commission_share >= 0 AND commission_share <= 100)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                surname TEXT,
                name TEXT,
                patronymic TEXT,
                phone TEXT,
                email TEXT,
                CHECK(phone IS NOT NULL OR email IS NOT NULL)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('apartment', 'house', 'land')),
                city TEXT,
                street TEXT,
                house_number TEXT,
                apartment_number TEXT,
                latitude REAL,
                longitude REAL,
                CHECK(latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
                CHECK(longitude IS NULL OR (longitude >= -180 AND longitude <= 180))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apartments (
                property_id INTEGER PRIMARY KEY,
                floor INTEGER,
                rooms INTEGER,
                area REAL,
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS houses (
                property_id INTEGER PRIMARY KEY,
                floors INTEGER,
                rooms INTEGER,
                area REAL,
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lands (
                property_id INTEGER PRIMARY KEY,
                area REAL,
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                realtor_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                price INTEGER NOT NULL CHECK(price > 0),
                rental_period INTEGER NOT NULL CHECK(rental_period > 0),
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (realtor_id) REFERENCES realtors(id),
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                realtor_id INTEGER NOT NULL,
                property_type TEXT NOT NULL CHECK(property_type IN ('apartment', 'house', 'land')),
                city TEXT,
                street TEXT,
                house_number TEXT,
                apartment_number TEXT,
                min_price INTEGER NOT NULL CHECK(min_price > 0),
                max_price INTEGER NOT NULL CHECK(max_price > 0),
                min_rental_period INTEGER NOT NULL CHECK(min_rental_period > 0),
                max_rental_period INTEGER NOT NULL CHECK(max_rental_period > 0),
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (realtor_id) REFERENCES realtors(id),
                CHECK(max_price >= min_price),
                CHECK(max_rental_period >= min_rental_period)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apartment_demands (
                demand_id INTEGER PRIMARY KEY,
                min_area REAL,
                max_area REAL,
                min_rooms INTEGER,
                max_rooms INTEGER,
                min_floor INTEGER,
                max_floor INTEGER,
                FOREIGN KEY (demand_id) REFERENCES demands(id) ON DELETE CASCADE,
                CHECK(max_area IS NULL OR min_area IS NULL OR max_area >= min_area),
                CHECK(max_rooms IS NULL OR min_rooms IS NULL OR max_rooms >= min_rooms),
                CHECK(max_floor IS NULL OR min_floor IS NULL OR max_floor >= min_floor)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS house_demands (
                demand_id INTEGER PRIMARY KEY,
                min_area REAL,
                max_area REAL,
                min_rooms INTEGER,
                max_rooms INTEGER,
                min_floors INTEGER,
                max_floors INTEGER,
                FOREIGN KEY (demand_id) REFERENCES demands(id) ON DELETE CASCADE,
                CHECK(max_area IS NULL OR min_area IS NULL OR max_area >= min_area),
                CHECK(max_rooms IS NULL OR min_rooms IS NULL OR max_rooms >= min_rooms),
                CHECK(max_floors IS NULL OR min_floors IS NULL OR max_floors >= min_floors)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS land_demands (
                demand_id INTEGER PRIMARY KEY,
                min_area REAL,
                max_area REAL,
                FOREIGN KEY (demand_id) REFERENCES demands(id) ON DELETE CASCADE,
                CHECK(max_area IS NULL OR min_area IS NULL OR max_area >= min_area)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                demand_id INTEGER NOT NULL UNIQUE,
                offer_id INTEGER NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (demand_id) REFERENCES demands(id),
                FOREIGN KEY (offer_id) REFERENCES offers(id)
            )
        """)
        
        self.conn.commit()
    
    def add_realtor(self, surname: str, name: str, patronymic: str, commission_share: Optional[float] = None) -> int:
        try:
            cursor = self.conn.cursor()
            if not surname or not name or not patronymic:
                raise ValueError("Фамилия, имя и отчество обязательны для заполнения")
            if commission_share is not None and (commission_share < 0 or commission_share > 100):
                raise ValueError("Доля от комиссии должна быть от 0 до 100")
            
            cursor.execute("""
                INSERT INTO realtors (surname, name, patronymic, commission_share)
                VALUES (?, ?, ?, ?)
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM realtors WHERE id = ?", (realtor_id,))
            if not cursor.fetchone():
                raise ValueError(f"Риэлтор с ID {realtor_id} не найден")
            
            if not surname or not name or not patronymic:
                raise ValueError("Фамилия, имя и отчество обязательны для заполнения")
            if commission_share is not None and (commission_share < 0 or commission_share > 100):
                raise ValueError("Доля от комиссии должна быть от 0 до 100")
            
            cursor.execute("""
                UPDATE realtors 
                SET surname = ?, name = ?, patronymic = ?, commission_share = ?
                WHERE id = ?
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM realtors WHERE id = ?", (realtor_id,))
            if not cursor.fetchone():
                raise ValueError(f"Риэлтор с ID {realtor_id} не найден")
            
            cursor.execute("SELECT COUNT(*) FROM offers WHERE realtor_id = ?", (realtor_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("SELECT COUNT(*) FROM demands WHERE realtor_id = ?", (realtor_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("DELETE FROM realtors WHERE id = ?", (realtor_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Ошибка при удалении риэлтора: {e}")
            raise
        except ValueError as e:
            raise
    
    def get_realtors(self, search: Optional[str] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if search:
            search_pattern = f"%{search}%"
            cursor.execute("""
                SELECT * FROM realtors 
                WHERE surname LIKE ? OR name LIKE ? OR patronymic LIKE ?
                ORDER BY surname, name, patronymic
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM realtors WHERE id = ?", (realtor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_client(self, surname: Optional[str], name: Optional[str], patronymic: Optional[str],
                   phone: Optional[str], email: Optional[str]) -> int:
        try:
            phone = phone.strip() if phone else None
            email = email.strip() if email else None
            
            if not phone and not email:
                raise ValueError("Необходимо указать хотя бы телефон или email")
            
            if email and '@' not in email:
                raise ValueError("Некорректный формат email")
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO clients (surname, name, patronymic, phone, email)
                VALUES (?, ?, ?, ?, ?)
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
            if not cursor.fetchone():
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            phone = phone.strip() if phone else None
            email = email.strip() if email else None
            
            if not phone and not email:
                raise ValueError("Необходимо указать хотя бы телефон или email")
            
            if email and '@' not in email:
                raise ValueError("Некорректный формат email")
            
            cursor.execute("""
                UPDATE clients 
                SET surname = ?, name = ?, patronymic = ?, phone = ?, email = ?
                WHERE id = ?
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
            if not cursor.fetchone():
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            cursor.execute("SELECT COUNT(*) FROM offers WHERE client_id = ?", (client_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("SELECT COUNT(*) FROM demands WHERE client_id = ?", (client_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Ошибка при удалении клиента: {e}")
            raise
        except ValueError as e:
            raise
    
    def get_clients(self, search: Optional[str] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if search:
            search_pattern = f"%{search}%"
            cursor.execute("""
                SELECT * FROM clients 
                WHERE surname LIKE ? OR name LIKE ? OR patronymic LIKE ? 
                   OR phone LIKE ? OR email LIKE ?
                ORDER BY surname, name, patronymic
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_property(self, property_type: str, city: Optional[str] = None, street: Optional[str] = None,
                    house_number: Optional[str] = None, apartment_number: Optional[str] = None,
                    latitude: Optional[float] = None, longitude: Optional[float] = None,
                    **kwargs) -> int:
        try:
            if property_type not in ['apartment', 'house', 'land']:
                raise ValueError(f"Некорректный тип объекта: {property_type}")
            
            if latitude is not None and (latitude < -90 or latitude > 90):
                raise ValueError("Широта должна быть от -90 до +90")
            if longitude is not None and (longitude < -180 or longitude > 180):
                raise ValueError("Долгота должна быть от -180 до +180")
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO properties (type, city, street, house_number, apartment_number, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                    INSERT INTO apartments (property_id, floor, rooms, area)
                    VALUES (?, ?, ?, ?)
                    INSERT INTO houses (property_id, floors, rooms, area)
                    VALUES (?, ?, ?, ?)
                    INSERT INTO lands (property_id, area)
                    VALUES (?, ?)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE properties 
            SET city = ?, street = ?, house_number = ?, apartment_number = ?, latitude = ?, longitude = ?
            WHERE id = ?
                UPDATE apartments SET floor = ?, rooms = ?, area = ? WHERE property_id = ?
                UPDATE houses SET floors = ?, rooms = ?, area = ? WHERE property_id = ?
                UPDATE lands SET area = ? WHERE property_id = ?
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM offers WHERE property_id = ?", (property_id,))
        if cursor.fetchone()[0] > 0:
            return False
        cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
        self.conn.commit()
        return True
    
    def get_properties(self, property_type: Optional[str] = None, city: Optional[str] = None,
                      street: Optional[str] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = "SELECT p.* FROM properties p WHERE 1=1"
        params = []
        
        if property_type:
            query += " AND p.type = ?"
            params.append(property_type)
        if city:
            query += " AND p.city LIKE ?"
            params.append(f"%{city}%")
        if street:
            query += " AND p.street LIKE ?"
            params.append(f"%{street}%")
        
        query += " ORDER BY p.id"
        cursor.execute(query, params)
        properties = [dict(row) for row in cursor.fetchall()]
        
        for prop in properties:
            prop_id = prop['id']
            prop_type = prop['type']
            if prop_type == 'apartment':
                cursor.execute("SELECT * FROM apartments WHERE property_id = ?", (prop_id,))
                row = cursor.fetchone()
                if row:
                    prop.update(dict(row))
            elif prop_type == 'house':
                cursor.execute("SELECT * FROM houses WHERE property_id = ?", (prop_id,))
                row = cursor.fetchone()
                if row:
                    prop.update(dict(row))
            elif prop_type == 'land':
                cursor.execute("SELECT * FROM lands WHERE property_id = ?", (prop_id,))
                row = cursor.fetchone()
                if row:
                    prop.update(dict(row))
        
        return properties
    
    def get_property(self, property_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        prop = dict(row)
        prop_type = prop['type']
        
        if prop_type == 'apartment':
            cursor.execute("SELECT * FROM apartments WHERE property_id = ?", (property_id,))
            row = cursor.fetchone()
            if row:
                prop.update(dict(row))
        elif prop_type == 'house':
            cursor.execute("SELECT * FROM houses WHERE property_id = ?", (property_id,))
            row = cursor.fetchone()
            if row:
                prop.update(dict(row))
        elif prop_type == 'land':
            cursor.execute("SELECT * FROM lands WHERE property_id = ?", (property_id,))
            row = cursor.fetchone()
            if row:
                prop.update(dict(row))
        
        return prop
    
    def add_offer(self, client_id: int, realtor_id: int, property_id: int, price: int, rental_period: int) -> int:
        try:
            cursor = self.conn.cursor()
            if price <= 0:
                raise ValueError("Цена должна быть положительным числом")
            if rental_period <= 0:
                raise ValueError("Срок сдачи должен быть положительным числом")
            
            cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
            if not cursor.fetchone():
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            cursor.execute("SELECT id FROM realtors WHERE id = ?", (realtor_id,))
            if not cursor.fetchone():
                raise ValueError(f"Риэлтор с ID {realtor_id} не найден")
            
            cursor.execute("SELECT id FROM properties WHERE id = ?", (property_id,))
            if not cursor.fetchone():
                raise ValueError(f"Объект недвижимости с ID {property_id} не найден")
            
            cursor.execute("""
                INSERT INTO offers (client_id, realtor_id, property_id, price, rental_period)
                VALUES (?, ?, ?, ?, ?)
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM offers WHERE id = ?", (offer_id,))
            if not cursor.fetchone():
                raise ValueError(f"Предложение с ID {offer_id} не найдено")
            
            if price <= 0:
                raise ValueError("Цена должна быть положительным числом")
            if rental_period <= 0:
                raise ValueError("Срок сдачи должен быть положительным числом")
            
            cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
            if not cursor.fetchone():
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            cursor.execute("SELECT id FROM realtors WHERE id = ?", (realtor_id,))
            if not cursor.fetchone():
                raise ValueError(f"Риэлтор с ID {realtor_id} не найден")
            
            cursor.execute("SELECT id FROM properties WHERE id = ?", (property_id,))
            if not cursor.fetchone():
                raise ValueError(f"Объект недвижимости с ID {property_id} не найден")
            
            cursor.execute("""
                UPDATE offers 
                SET client_id = ?, realtor_id = ?, property_id = ?, price = ?, rental_period = ?
                WHERE id = ?
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM offers WHERE id = ?", (offer_id,))
            if not cursor.fetchone():
                raise ValueError(f"Предложение с ID {offer_id} не найдено")
            
            cursor.execute("SELECT COUNT(*) FROM deals WHERE offer_id = ?", (offer_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("DELETE FROM offers WHERE id = ?", (offer_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Ошибка при удалении предложения: {e}")
            raise
        except ValueError as e:
            raise
    
    def get_offers(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT o.*, 
                   c.surname || ' ' || c.name || ' ' || COALESCE(c.patronymic, '') as client_name,
                   r.surname || ' ' || r.name || ' ' || COALESCE(r.patronymic, '') as realtor_name,
                   p.type as property_type
            FROM offers o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN realtors r ON o.realtor_id = r.id
            LEFT JOIN properties p ON o.property_id = p.id
            ORDER BY o.id
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT o.*, 
                   c.surname || ' ' || c.name || ' ' || COALESCE(c.patronymic, '') as client_name,
                   r.surname || ' ' || r.name || ' ' || COALESCE(r.patronymic, '') as realtor_name,
                   p.*
            FROM offers o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN realtors r ON o.realtor_id = r.id
            LEFT JOIN properties p ON o.property_id = p.id
            WHERE o.id = ?
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM offers WHERE client_id = ?", (client_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_offers_by_realtor(self, realtor_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM offers WHERE realtor_id = ?", (realtor_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_demand(self, client_id: int, realtor_id: int, property_type: str,
                   city: Optional[str], street: Optional[str], house_number: Optional[str],
                   apartment_number: Optional[str], min_price: int, max_price: int,
                   min_rental_period: int, max_rental_period: int, **kwargs) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO demands (client_id, realtor_id, property_type, city, street, 
                               house_number, apartment_number, min_price, max_price,
                               min_rental_period, max_rental_period)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                INSERT INTO apartment_demands (demand_id, min_area, max_area, min_rooms, max_rooms, min_floor, max_floor)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                INSERT INTO house_demands (demand_id, min_area, max_area, min_rooms, max_rooms, min_floors, max_floors)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                INSERT INTO land_demands (demand_id, min_area, max_area)
                VALUES (?, ?, ?)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE demands 
            SET client_id = ?, realtor_id = ?, property_type = ?, city = ?, street = ?,
                house_number = ?, apartment_number = ?, min_price = ?, max_price = ?,
                min_rental_period = ?, max_rental_period = ?
            WHERE id = ?
                UPDATE apartment_demands 
                SET min_area = ?, max_area = ?, min_rooms = ?, max_rooms = ?, min_floor = ?, max_floor = ?
                WHERE demand_id = ?
                UPDATE house_demands 
                SET min_area = ?, max_area = ?, min_rooms = ?, max_rooms = ?, min_floors = ?, max_floors = ?
                WHERE demand_id = ?
                UPDATE land_demands 
                SET min_area = ?, max_area = ?
                WHERE demand_id = ?
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deals WHERE demand_id = ?", (demand_id,))
        if cursor.fetchone()[0] > 0:
            return False
        cursor.execute("DELETE FROM demands WHERE id = ?", (demand_id,))
        self.conn.commit()
        return True
    
    def get_demands(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.*, 
                   c.surname || ' ' || c.name || ' ' || COALESCE(c.patronymic, '') as client_name,
                   r.surname || ' ' || r.name || ' ' || COALESCE(r.patronymic, '') as realtor_name
            FROM demands d
            LEFT JOIN clients c ON d.client_id = c.id
            LEFT JOIN realtors r ON d.realtor_id = r.id
            ORDER BY d.id
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM demands WHERE id = ?", (demand_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        demand = dict(row)
        prop_type = demand['property_type']
        
        if prop_type == 'apartment':
            cursor.execute("SELECT * FROM apartment_demands WHERE demand_id = ?", (demand_id,))
            row = cursor.fetchone()
            if row:
                demand.update(dict(row))
        elif prop_type == 'house':
            cursor.execute("SELECT * FROM house_demands WHERE demand_id = ?", (demand_id,))
            row = cursor.fetchone()
            if row:
                demand.update(dict(row))
        elif prop_type == 'land':
            cursor.execute("SELECT * FROM land_demands WHERE demand_id = ?", (demand_id,))
            row = cursor.fetchone()
            if row:
                demand.update(dict(row))
        
        return demand
    
    def get_demands_by_client(self, client_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM demands WHERE client_id = ?", (client_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_demands_by_realtor(self, realtor_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM demands WHERE realtor_id = ?", (realtor_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_deal(self, demand_id: int, offer_id: int) -> int:
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT id FROM demands WHERE id = ?", (demand_id,))
            if not cursor.fetchone():
                raise ValueError(f"Потребность с ID {demand_id} не найдена")
            
            cursor.execute("SELECT id FROM offers WHERE id = ?", (offer_id,))
            if not cursor.fetchone():
                raise ValueError(f"Предложение с ID {offer_id} не найдено")
            
            if self.is_demand_satisfied(demand_id):
                raise ValueError(f"Потребность с ID {demand_id} уже удовлетворена")
            
            if self.is_offer_satisfied(offer_id):
                raise ValueError(f"Предложение с ID {offer_id} уже удовлетворено")
            
            cursor.execute("""
                INSERT INTO deals (demand_id, offer_id)
                VALUES (?, ?)
            """, (demand_id, offer_id))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Ошибка при добавлении сделки: {e}")
            raise
        except ValueError as e:
            raise
    
    def update_deal(self, deal_id: int, demand_id: int, offer_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE deals 
            SET demand_id = ?, offer_id = ?
            WHERE id = ?
        """, (demand_id, offer_id, deal_id))
        self.conn.commit()
    
    def delete_deal(self, deal_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM deals WHERE id = ?", (deal_id,))
        self.conn.commit()
    
    def get_deals(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.*,
                   dem.client_id as demand_client_id,
                   dem.realtor_id as demand_realtor_id,
                   off.client_id as offer_client_id,
                   off.realtor_id as offer_realtor_id,
                   off.property_id,
                   off.price,
                   off.rental_period
            FROM deals d
            LEFT JOIN demands dem ON d.demand_id = dem.id
            LEFT JOIN offers off ON d.offer_id = off.id
            ORDER BY d.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_deal(self, deal_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.*,
                   dem.*,
                   off.*,
                   dem.client_id as demand_client_id,
                   dem.realtor_id as demand_realtor_id,
                   off.client_id as offer_client_id,
                   off.realtor_id as offer_realtor_id
            FROM deals d
            LEFT JOIN demands dem ON d.demand_id = dem.id
            LEFT JOIN offers off ON d.offer_id = off.id
            WHERE d.id = ?
        """, (deal_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        deal = dict(row)
        deal['demand'] = self.get_demand(deal['demand_id'])
        deal['offer'] = self.get_offer(deal['offer_id'])
        
        return deal
    
    def is_demand_satisfied(self, demand_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deals WHERE demand_id = ?", (demand_id,))
        return cursor.fetchone()[0] > 0
    
    def is_offer_satisfied(self, offer_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deals WHERE offer_id = ?", (offer_id,))
        return cursor.fetchone()[0] > 0
    
    def get_matching_offers(self, demand_id: int) -> List[Dict]:
        demand = self.get_demand(demand_id)
        if not demand:
            return []
        
        all_offers = self.get_offers()
        matching = []
        
        for offer in all_offers:
            if self.is_offer_satisfied(offer['id']):
                continue
            
            property_data = self.get_property(offer['property_id'])
            if not property_data:
                continue
            
            if self.check_match(demand, property_data, offer):
                matching.append(offer)
        
        return matching
    
    def check_match(self, demand: Dict, property_data: Dict, offer: Dict) -> bool:
        if demand['property_type'] != property_data['type']:
            return False
        
        if demand['city'] and property_data['city'] != demand['city']:
            return False
        if demand['street'] and property_data['street'] != demand['street']:
            return False
        if demand['house_number'] and property_data['house_number'] != demand['house_number']:
            return False
        if demand['apartment_number'] and property_data['apartment_number'] != demand['apartment_number']:
            return False
        
        if not (demand['min_price'] <= offer['price'] <= demand['max_price']):
            return False
        
        if not (demand['min_rental_period'] <= offer['rental_period'] <= demand['max_rental_period']):
            return False
        
        prop_type = demand['property_type']
        if prop_type == 'apartment':
            if demand.get('min_floor') is not None and property_data.get('floor') is not None:
                max_floor = demand.get('max_floor')
                if max_floor is not None:
                    if not (demand['min_floor'] <= property_data['floor'] <= max_floor):
                        return False
                else:
                    if property_data['floor'] < demand['min_floor']:
                        return False
            if demand.get('min_rooms') is not None and property_data.get('rooms') is not None:
                max_rooms = demand.get('max_rooms')
                if max_rooms is not None:
                    if not (demand['min_rooms'] <= property_data['rooms'] <= max_rooms):
                        return False
                else:
                    if property_data['rooms'] < demand['min_rooms']:
                        return False
            if demand.get('min_area') is not None and property_data.get('area') is not None:
                max_area = demand.get('max_area')
                if max_area is not None:
                    if not (demand['min_area'] <= property_data['area'] <= max_area):
                        return False
                else:
                    if property_data['area'] < demand['min_area']:
                        return False
        elif prop_type == 'house':
            if demand.get('min_floors') is not None and property_data.get('floors') is not None:
                max_floors = demand.get('max_floors')
                if max_floors is not None:
                    if not (demand['min_floors'] <= property_data['floors'] <= max_floors):
                        return False
                else:
                    if property_data['floors'] < demand['min_floors']:
                        return False
            if demand.get('min_rooms') is not None and property_data.get('rooms') is not None:
                max_rooms = demand.get('max_rooms')
                if max_rooms is not None:
                    if not (demand['min_rooms'] <= property_data['rooms'] <= max_rooms):
                        return False
                else:
                    if property_data['rooms'] < demand['min_rooms']:
                        return False
            if demand.get('min_area') is not None and property_data.get('area') is not None:
                max_area = demand.get('max_area')
                if max_area is not None:
                    if not (demand['min_area'] <= property_data['area'] <= max_area):
                        return False
                else:
                    if property_data['area'] < demand['min_area']:
                        return False
        elif prop_type == 'land':
            if demand.get('min_area') is not None and property_data.get('area') is not None:
                max_area = demand.get('max_area')
                if max_area is not None:
                    if not (demand['min_area'] <= property_data['area'] <= max_area):
                        return False
                else:
                    if property_data['area'] < demand['min_area']:
                        return False
        
        return True
    
    def close(self):
        self.conn.close()

