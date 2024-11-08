from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser,Logs

class UserAdmin(BaseUserAdmin):
    model = CustomUser
    # You may need to create these forms
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    list_display = ('phone', 'name','device_token', 'user_type', 'is_staff', 'is_on_duty')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_on_duty')
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('name', 'email', 'dob', 'profile_picture', 'thana', 'batch', 'bp', 'rank', 'lat', 'lon', 'district', 'address', 'nid', 'device_token','is_on_duty')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)

admin.site.register(CustomUser, UserAdmin)

@admin.register(Logs)
class LogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'police', 'time', 'user_lat', 'user_lon', 'police_lat', 'police_lon')
    search_fields = ('user__phone', 'police__phone')
    list_filter = ('time',)