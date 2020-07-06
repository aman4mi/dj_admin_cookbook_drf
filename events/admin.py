from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Epic, Event, EventHero, EventVillain
from django.contrib.auth.models import User, Group

admin.site.unregister(User)
admin.site.unregister(Group)

class EventAdminSite(AdminSite):
    site_header = "E-recruitment Events Admin"
    site_title = "E-recruitment Events Admin Portal"
    index_title = "Welcome to E-recruitment Researcher Events Portal"

event_admin_site = EventAdminSite(name='event_admin')

event_admin_site.register(Epic)
event_admin_site.register(Event)
event_admin_site.register(EventHero)
event_admin_site.register(EventVillain)
