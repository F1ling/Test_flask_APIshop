from ..extensions import db
from ..models import Product, Category
import logging

logger = logging.getLogger(__name__)

class BackupData:
    @staticmethod
    def load_from_backup():
        try:
            if Product.query.count() > 0:
                logger.info("Data already exists")
                return True

            sample_data = [
                {"name": "Sample Product 1", "price": 100.0, "category": "Electronics"},
                {"name": "Sample Product 2", "price": 50.0, "category": "Clothing"}
            ]
            
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
            
            logger.info(f"Loaded {len(products)} backup products, {len(categories)} categories")
            return True
            
        except Exception as e:
            logger.error(f"Backup loading failed: {str(e)}")
            db.session.rollback()
            return False