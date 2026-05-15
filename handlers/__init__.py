from .admin import register_admin_handlers
from .protection import register_protection_handlers
from .autodelete import register_autodelete_handlers
from .purge import register_purge_handlers
from .settings import register_settings_handlers

def register_all_handlers(app, db):
    """Register all bot handlers"""
    register_admin_handlers(app, db)
    register_protection_handlers(app, db)
    register_autodelete_handlers(app, db)
    register_purge_handlers(app, db)
    register_settings_handlers(app, db)
    
    print("✅ All handlers registered successfully!")
