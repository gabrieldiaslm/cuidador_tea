# core/views.py
from .models import Assessment, Section, AssessmentResult, SectionResult
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from .forms import ProfileForm # Criaremos este formulário a seguir
from .models import Assessment, AssessmentResult, SectionResult


def index(request):
    """Redireciona para a home se estiver logado, senão para o login."""
    if request.user.is_authenticated:
        return redirect('profile_select')
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Ao se cadastrar, cria um perfil padrão e redireciona para a home
            Profile.objects.create(user=user, name=user.username)
            return redirect('profile_select')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def profile_select(request):
    """Exibe a tela 'selecionar perfil?'."""
    profiles = request.user.profiles.all()
    return render(request, 'core/profile_select.html', {'profiles': profiles})

@login_required
def select_profile_and_redirect(request, profile_id):
    """Salva o perfil na sessão e redireciona para a home."""
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    request.session['selected_profile_id'] = profile.id
    return redirect('home')

@login_required
def profile_create(request):
    """Cria um novo perfil para o usuário logado."""
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        # Limita o número de perfis por usuário (ex: 5)
        if request.user.profiles.count() >= 5:
            # Adicionar uma mensagem de erro aqui seria uma boa prática
            return redirect('profile_select')
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile_select')
    else:
        form = ProfileForm()
    return render(request, 'core/profile_form.html', {'form': form})

@login_required
def home(request):
    """Página principal, acessível apenas após selecionar um perfil."""
    try:
        selected_profile_id = request.session.get('selected_profile_id')
        if not selected_profile_id:
            return redirect('profile_select') # Se não houver perfil na sessão, volta pra seleção
        
        profile = Profile.objects.get(id=selected_profile_id, user=request.user)
        # Agora você pode usar o objeto 'profile' para filtrar conteúdo, etc.
        return render(request, 'core/home.html', {'profile': profile})
    except Profile.DoesNotExist:
        # Caso o perfil na sessão seja inválido
        del request.session['selected_profile_id']
        return redirect('profile_select')
# Decorator auxiliar para garantir que um perfil foi selecionado
def profile_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'selected_profile_id' not in request.session:
            return redirect('profile_select')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Modifique a view 'home' para usar o decorator
@login_required
@profile_required
def home(request):
    try:
        selected_profile_id = request.session.get('selected_profile_id')
        profile = Profile.objects.get(id=selected_profile_id, user=request.user)
        return render(request, 'core/home.html', {'profile': profile})
    except Profile.DoesNotExist:
        del request.session['selected_profile_id']
        return redirect('profile_select')


# Novas views para avaliações
@login_required
@profile_required
def assessment_list(request):
    """Lista todas as avaliações disponíveis."""
    assessments = Assessment.objects.all()
    profile = Profile.objects.get(id=request.session['selected_profile_id'])
    return render(request, 'core/assessment_list.html', {'assessments': assessments, 'profile': profile})

@login_required
@profile_required
def take_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment.objects.prefetch_related('sections__questions'), id=assessment_id)
    profile = Profile.objects.get(id=request.session['selected_profile_id'])

    if request.method == 'POST':
        assessment_result = AssessmentResult.objects.create(
            profile=profile,
            assessment=assessment
        )
        for section in assessment.sections.all():
            section_score = 0
            for question in section.questions.all():
                answer_value = request.POST.get(f'question_{question.id}')
                if answer_value:
                    section_score += int(answer_value)
            
            SectionResult.objects.create(
                assessment_result=assessment_result,
                section=section,
                score=section_score
            )
        return redirect('assessment_history')

    return render(request, 'core/take_assessment.html', {'assessment': assessment, 'profile': profile})

@login_required
@profile_required
def assessment_history(request):
    profile = Profile.objects.get(id=request.session['selected_profile_id'])
    results = profile.assessment_results.prefetch_related('section_results__section').all()
    return render(request, 'core/assessment_history.html', {'results': results, 'profile': profile})