# core/models.py

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        # user unico
        unique_together = ('user', 'name')

class Assessment(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    def __str__(self):
        return self.title

class Section(models.Model):
    """Representa uma seção dentro de uma avaliação (ex: "Seção 1 de 4")."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name="Título da Seção")
    order = models.PositiveIntegerField(help_text="A ordem em que a seção aparece (1, 2, 3...).")

    class Meta:
        ordering = ['order'] # Garante que as seções sempre apareçam na ordem correta

    def __str__(self):
        return f"{self.assessment.title} - {self.title}"

class Question(models.Model):
    """Uma pergunta, agora pertencente a uma Secção."""
    # A linha abaixo é essencial. Confirme que a relação aponta para 'Section'.
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500, verbose_name="Texto da Pergunta")

    def __str__(self):
        return self.text

class AssessmentResult(models.Model):
    """Um registro de que um perfil completou uma avaliação."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado de {self.profile.name} em {self.assessment.title}"

    def get_total_score(self):
        """Calcula a pontuação total somando as pontuações das seções."""
        return sum(result.score for result in self.section_results.all())

class SectionResult(models.Model):
    """Armazena a pontuação de uma seção específica para um resultado de avaliação."""
    assessment_result = models.ForeignKey(AssessmentResult, on_delete=models.CASCADE, related_name='section_results')
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    score = models.IntegerField(verbose_name="Pontuação da Seção")

    def __str__(self):
        return f"{self.section.title}: {self.score} pontos"