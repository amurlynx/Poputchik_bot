"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .echo import echo_router
from .manage_announcements import my_announcements
from .new_announcement import new_Announcement_router
#from .publish import publish_router
from .simple_menu import menu_router
from .user import user_router

routers_list = [
    admin_router,
#   publish_router,
#    manage_announcements,
     new_Announcement_router,
#    menu_router,
    user_router,
    echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]
