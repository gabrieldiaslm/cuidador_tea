# core/admin.py

from django.contrib import admin
from .models import (
    Profile, Assessment, Section, Question, 
    AssessmentResult
)

# 1. Registamos o modelo Assessment de forma simples.
@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

# 2. Criamos uma página de admin para as Secções.
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    # Mostra colunas úteis na lista de secções.
    list_display = ('title', 'assessment', 'order')
    # Permite filtrar as secções pela avaliação a que pertencem.
    list_filter = ('assessment',)

# 3. Criamos uma página de admin para as Perguntas.
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'info_text', 'section')
    list_filter = ('section__assessment', 'section') # Permite filtrar por avaliação ou secção
    search_fields = ('text',) # Adiciona uma barra de pesquisa

# O resto do ficheiro permanece igual.
@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('profile', 'assessment', 'completed_at')
    readonly_fields = ('profile', 'assessment', 'completed_at')

admin.site.register(Profile)