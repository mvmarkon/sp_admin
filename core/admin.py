from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base admin class with common configurations for models
    that inherit from BaseModel.
    """
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'is_deleted')
    
    def get_queryset(self, request):
        """
        Override to show only non-deleted objects by default.
        """
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    def delete_model(self, request, obj):
        """
        Override to use soft delete.
        """
        obj.delete()

    def delete_queryset(self, request, queryset):
        """
        Override to use soft delete for bulk operations.
        """
        for obj in queryset:
            obj.delete()

    actions = ['restore_objects']

    def restore_objects(self, request, queryset):
        """
        Admin action to restore soft-deleted objects.
        """
        count = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                count += 1
        
        self.message_user(
            request,
            f'{count} objetos restaurados exitosamente.'
        )
    
    restore_objects.short_description = "Restaurar objetos seleccionados"