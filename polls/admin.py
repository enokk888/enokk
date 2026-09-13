from django.contrib import admin
from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
                ("Content", {"fields": ["text"]}),
                ("Date Information", {"fields": ["publication_date"], "classes": ["collapses"]})
            ]
    list_display = ["text", "publication_date", "was_published_recently"]
    list_filter = ["publication_date"]
    search_fields = ["text"]
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)
