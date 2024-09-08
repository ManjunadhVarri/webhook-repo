from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    try:
        app.config["MONGO_URI"] = "mongodb://localhost:27017/webhookDB"
        mongo.init_app(app)
    except Exception as e:
        print(f"Error initializing MongoDB: {str(e)}")



