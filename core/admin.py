from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Appointment, GalleryImage

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Approval', {'fields': ('role',)}),

        # ⭐⭐ Doctor Additional Fields added here ⭐⭐ #type: ignore
        ('Doctor Details', {
            'fields': (
                'speciality',
                'qualification',
                'experience',
                'work_from',
                'about',
                'image',
            )
        }),
    )

    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id','patient','doctor','date','time','status','created_at')
    list_filter = ('status','date','doctor')
    search_fields = ('patient__username','doctor__username','symptoms')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('id','uploader','caption','created_at')
    search_fields = ('uploader__username','caption')
