# core/models.py

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Esta linha garante que cada perfil PERTENCE a um único usuário.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(max_length=255, verbose_name="Nome Completo")

    GRAU_AUTISMO_CHOICES = [
        ('1', 'Nível 1 - Leve'),
        ('2', 'Nível 2 - Moderado'),
        ('3', 'Nível 3 - Severo'),
    ]

    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    grau_autismo = models.CharField(
        max_length=1,
        choices=GRAU_AUTISMO_CHOICES,
        verbose_name="Grau de Autismo"
    )
    tem_laudo = models.BooleanField(default=False, verbose_name="Possui laudo médico?")
    is_active = models.BooleanField(default=True, verbose_name="Está ativo?")
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
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name="Título da Secção")
    order = models.PositiveIntegerField()

    # --- NOVOS CAMPOS PARA AS DICAS ---
    tip_low = models.TextField(verbose_name="Dica para nota baixa (0-4)", blank=True)
    tip_medium = models.TextField(verbose_name="Dica para nota média (5-6)", blank=True)
    tip_high = models.TextField(verbose_name="Dica para nota alta (7-10)", blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500, verbose_name="Texto da Pergunta")
    info_text = models.TextField(
        blank=True, # O campo é opcional
        null=True,  # Permite que o campo seja nulo na base de dados
        verbose_name="Texto de Informação (Ajuda)",
        help_text="Este texto aparecerá quando o utilizador clicar no botão 'i'."
    )
    def __str__(self):
        return self.text

class AssessmentResult(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado de {self.profile.name} em {self.assessment.title}"

    def get_total_score(self):
        return sum(result.score for result in self.section_results.all())
    
def get_previous_result(self):
        """Busca a última avaliação deste perfil antes da atual"""
        return AssessmentResult.objects.filter(
            profile=self.profile,
            assessment=self.assessment,
            completed_at__lt=self.completed_at
        ).order_by('-completed_at').first()

class SectionResult(models.Model):
    assessment_result = models.ForeignKey(AssessmentResult, on_delete=models.CASCADE, related_name='section_results')
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    score = models.IntegerField(verbose_name="Pontuação")

    def get_tip(self):
        """Retorna a dica baseada na pontuação obtida na secção"""
        if self.score <= 4:
            return self.section.tip_low
        elif self.score <= 6:
            return self.section.tip_medium
        else:
            return self.section.tip_high
    
def get_comparison(self):
        """Calcula a diferença de nota com a avaliação anterior"""
        prev_assessment = self.assessment_result.get_previous_result()
        if prev_assessment:
            prev_sec_res = SectionResult.objects.filter(
                assessment_result=prev_assessment,
                section=self.section
            ).first()
            if prev_sec_res:
                return self.score - prev_sec_res.score
        return None