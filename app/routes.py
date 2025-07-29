from flask import Blueprint, jsonify
from .extensions import db
from .models import Product, Category

bp = Blueprint('api', __name__)  

@bp.route('/info')
def info():
    try:
        categories = Category.query.all()
        products = Product.query.limit(100).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'products': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'price': p.price,
                        'category': p.category.name
                    } for p in products
                ],
                'statistics': {
                    'total_products': Product.query.count(),
                    'total_categories': Category.query.count()
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in /info: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500