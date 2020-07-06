
from django.contrib import admin
from django.urls import path
from events.admin import event_admin_site
from entities.admin import entities_admin_site

admin.site.site_header = "E-recruitment Admin"
admin.site.site_title = "E-recruitment Admin Portal"
admin.site.index_title = "Welcome to E-recruitment Researcher Portal"

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
urlpatterns = [
    path('admin/', admin.site.urls),
    path('event-admin/', event_admin_site.urls),
    path('entity-admin/', entities_admin_site.urls),
]
