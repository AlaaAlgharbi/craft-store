from django.apps import AppConfig
import threading
from .auction_watcher import auction_watcher

class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'

    def ready(self):
        threading.Thread(target=auction_watcher, daemon=True).start()
