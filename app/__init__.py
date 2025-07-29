from flask import Flask
from .extensions import db
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from .services.data_loader import DataLoader
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Явная инициализация расширений
    db.init_app(app)
    
    with app.app_context():
        # Проверка подключения к БД
        try:
            db.engine.connect()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
        
        # Создание таблиц
        db.create_all()
        print("✅ Tables created:", db.metadata.tables.keys())
        from .routes import bp
        app.register_blueprint(bp)
        # Планировщик для обновления данных
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            scheduler = BackgroundScheduler()
            scheduler.add_job(
            lambda: DataLoader.load_initial_data(),
            'interval',
            minutes=60
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())       
        
    return app