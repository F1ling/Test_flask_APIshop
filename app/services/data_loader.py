import requests
from ..extensions import db
from ..models import Product, Category
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    @staticmethod
    def load_sample_data():
        """Загрузка тестовых данных, если API недоступно"""
        sample_data = [
            {"name": "Телевизор", "price": 29999, "category": "Техника"},
            {"name": "Смартфон", "price": 19999, "category": "Техника"},
            {"name": "Наушники", "price": 4999, "category": "Аксессуары"}
        ]
        
        try:
            categories = {}
            products = []
            
            for item in sample_data:
                cat_name = item['category']
                if cat_name not in categories:
                    categories[cat_name] = Category(name=cat_name)
                
                products.append(Product(
                    name=item['name'],
                    price=item['price'],
                    category=categories[cat_name]
                ))
            
            db.session.add_all(categories.values())
            db.session.add_all(products)
            db.session.commit()
            logger.info("Loaded sample data successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load sample data: {str(e)}")
            db.session.rollback()
            return False

    @classmethod
    def load_initial_data(cls):
        """Основной метод загрузки данных"""
        if Product.query.count() > 0:
            logger.info("Data already exists in DB")
            return True
            
        # Сначала пробуем загрузить из API
        api_loaded = cls._try_load_from_api()
        
        # Если не получилось, загружаем тестовые данные
        if not api_loaded:
            return cls.load_sample_data()
        
        return True

    @classmethod
    def _try_load_from_api(cls):
        """Попытка загрузки данных из API"""
        try:
            response = requests.get(
                "https://bot-igor.ru/api/products?on_main=true",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            categories = {}
            products = []
            
            for item in data.get('products', []):
                cat_name = item.get('category', 'Другое')
                if cat_name not in categories:
                    categories[cat_name] = Category(name=cat_name)
                
                products.append(Product(
                    name=item.get('product_name', item.get('title', 'Без названия')),
                    price=float(item.get('price', 0)),
                    category=categories[cat_name]
                ))
            
            db.session.add_all(categories.values())
            db.session.add_all(products)
            db.session.commit()
            logger.info(f"Loaded {len(products)} products from API")
            return True
            
        except Exception as e:
            logger.error(f"API load failed: {str(e)}")
            return False