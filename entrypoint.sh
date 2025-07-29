#!/bin/bash

# Ожидание PostgreSQL
until pg_isready -h db -p 5432 -U user -d mydb; do
    echo "⌛ Waiting for PostgreSQL... ($(date))"
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Инициализация БД и загрузка данных
python <<EOF
import logging
from app import create_app
from app.extensions import db
from app.services.data_loader import DataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

with app.app_context():
    logger.info("Creating database tables...")
    db.create_all()
    
    logger.info("Loading initial data...")
    if DataLoader.load_initial_data():
        from app.models import Product, Category
        logger.info(f"Data loaded: {Product.query.count()} products, {Category.query.count()} categories")
    else:
        logger.error("Failed to load initial data")
EOF

# Запуск приложения
exec flask run --host=0.0.0.0 --port=5555