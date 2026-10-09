from django.contrib import admin
from .models import TrustedFile


class DownloadAdmin(admin.ModelAdmin):
    fieldsets = [
                ("Availability", {"fields": ["is_available", "last_update_date", "publication_date"], "classes": ["collapses"]}),
                ("Content", {"fields": ["title", "file", "image", "description", "developer_notes"]}),
            ]
    list_display = ["title", "file", "is_available", "publication_date"]
    list_filter = ["is_available", "publication_date"]
    search_fields = ["title", "file"]

admin.site.register(TrustedFile, DownloadAdmin)
