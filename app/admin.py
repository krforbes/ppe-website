from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

from .models import *




class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    fields = ['pref_updated', 'availability_updated']

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

class PieceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Information', {'fields': ['title', 'composer','arrangers','num_pianists','num_hard_parts','num_pianos','extras', 'length','color']}),
    ]

class ScheduleAdmin(admin.ModelAdmin):
    fields = ['pref_reset', 'availability_reset']

admin.site.register(Piece, PieceAdmin)
admin.site.register(Schedule, ScheduleAdmin)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
