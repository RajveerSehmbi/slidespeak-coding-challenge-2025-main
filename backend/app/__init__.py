import logging
from flask import Flask
from flask_cors import CORS
from .extensions import celery_init_app, init_redis
from .ppt_converter_routes import ppt_converter
from .services.s3Service import S3Service

def create_app():
    app = Flask(__name__)
    CORS(app)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.logger.setLevel(logging.INFO)

    app.redis = init_redis(app)
    app.s3_service = S3Service(app.logger)

    app.config["CELERY"] = {
        "broker_url": "redis://redis:6379",
        "result_backend": "redis://redis:6379"
        }
    celery_init_app(app)
    
    app.register_blueprint(ppt_converter)
    return app