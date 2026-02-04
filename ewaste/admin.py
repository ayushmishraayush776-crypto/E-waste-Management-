from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import EWasteCategory, EWasteItem, PickupRequest, RecyclingFacility, Feedback, Company, Notification, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('is_company', 'company', 'created_at')
    readonly_fields = ('created_at',)


class CustomUserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)

    def is_company_member(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile and profile.is_company
    is_company_member.boolean = True
    is_company_member.short_description = 'Company Member'

    list_display = list(DjangoUserAdmin.list_display) + ['is_company_member']


# Unregister and re-register User admin to include profile inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(EWasteCategory)
class EWasteCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(EWasteItem)
class EWasteItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'user', 'category', 'condition', 'is_collected', 'created_at']
    list_filter = ['condition', 'is_collected', 'category', 'created_at']
    search_fields = ['item_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Item Information', {
            'fields': ('user', 'category', 'item_name', 'description', 'condition')
        }),
        ('Quantity & Pickup', {
            'fields': ('quantity', 'pickup_location', 'preferred_date', 'contact_phone')
        }),
        ('Status', {
            'fields': ('is_collected', 'created_at', 'updated_at')
        }),
    )


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ['ewaste_item', 'status', 'assigned_to', 'scheduled_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['ewaste_item__item_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RecyclingFacility)
class RecyclingFacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'email', 'operating_hours']
    search_fields = ['name', 'address']
    fieldsets = (
        ('Facility Information', {
            'fields': ('name', 'address', 'phone', 'email')
        }),
        ('Operations', {
            'fields': ('accepted_items', 'operating_hours')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'subject', 'message']
    readonly_fields = ['created_at']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_email', 'contact_phone', 'created_at']
    search_fields = ['name', 'contact_email']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'company', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['message', 'user__username', 'company__name']
