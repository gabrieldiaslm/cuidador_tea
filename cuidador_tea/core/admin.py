from django.contrib import admin
from .models import (
    Profile, Assessment, Section, Question, 
    AssessmentResult
)

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'assessment', 'order')
    list_filter = ('assessment',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'info_text', 'section')
    list_filter = ('section__assessment', 'section') 
    search_fields = ('text',) 

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('profile', 'assessment', 'completed_at')
    readonly_fields = ('profile', 'assessment', 'completed_at')

admin.site.register(Profile)