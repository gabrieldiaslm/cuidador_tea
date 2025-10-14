# core/admin.py

from django.contrib import admin
from .models import (
    Profile, Assessment, Section, Question, 
    AssessmentResult, SectionResult
)

# ------------------------------------------------------------------
# VERIFIQUE ESTA PARTE COM MUITA ATENÇÃO
# ------------------------------------------------------------------

# PRIMEIRO: A classe QuestionInline tem de ser definida.
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5

# SEGUNDO: A classe SectionInline tem de ser definida E
# DEVE conter a linha 'inlines = [QuestionInline]'
class SectionInline(admin.StackedInline):
    model = Section
    inlines = [QuestionInline]  # <-- ESTA LINHA É A MAIS IMPORTANTE!
    extra = 1

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    inlines = [SectionInline] # Esta parte parece estar a funcionar, pois vê as secções.
    list_display = ('title', 'description')

# ------------------------------------------------------------------
# O resto do ficheiro
# ------------------------------------------------------------------

class SectionResultInline(admin.TabularInline):
    model = SectionResult
    readonly_fields = ('section', 'score')
    can_delete = False
    extra = 0

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    inlines = [SectionResultInline]
    list_display = ('profile', 'assessment', 'completed_at')
    list_filter = ('assessment', 'profile__user')
    readonly_fields = ('profile', 'assessment', 'completed_at')

admin.site.register(Profile)