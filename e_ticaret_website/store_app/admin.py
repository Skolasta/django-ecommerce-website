from django.contrib import admin
from . import models

# Register your models here.

# Review Admin Configuration
@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'product__category')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'comment')
        }),
        ('Date Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# Admin registration
admin.site.register(models.Product)
admin.site.register(models.Category)


