import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .models import Assessment, Section, AssessmentResult, SectionResult, Profile
from .forms import ProfileForm 

def profile_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'selected_profile_id' not in request.session:
            return redirect('profile_select')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

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
            return redirect('profile_create') 
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def profile_select(request):
    profiles = request.user.profiles.filter(is_active=True)
    return render(request, 'core/profile_select.html', {'profiles': profiles})

@login_required
def select_profile_and_redirect(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    request.session['selected_profile_id'] = profile.id
    return redirect('home')

@login_required
def profile_create(request):
    """Cria um novo perfil para o usuário logado."""
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        # Limita o número de perfis por usuário
        if request.user.profiles.count() >= 5:
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
@profile_required
def home(request):
    """Página principal, acessível apenas após selecionar um perfil."""
    try:
        selected_profile_id = request.session.get('selected_profile_id')
        profile = Profile.objects.get(id=selected_profile_id, user=request.user)
        return render(request, 'core/home.html', {'profile': profile})
    except Profile.DoesNotExist:
        # Previne KeyError ao tentar deletar uma chave que não existe
        if 'selected_profile_id' in request.session:
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

# CRUD PERFIL --------

# READ - Ver Detalhes do Perfil
@login_required
def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user, is_active=True)
    return render(request, 'core/profile_detail.html', {'profile': profile})

# UPDATE - Editar Perfil
@login_required
def profile_update(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user, is_active=True)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_select') 
    else:
        form = ProfileForm(instance=profile)
        
    return render(request, 'core/profile_form.html', {'form': form, 'is_editing': True})

# DELETE - Agora funciona como "Arquivar" Perfil
@login_required
def profile_delete(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user, is_active=True)
    
    if request.method == 'POST':
        profile.is_active = False
        profile.save()
        return redirect('profile_select')
        
    return render(request, 'core/profile_delete_confirm.html', {'profile': profile})

def offline(request):
    """Página exibida pelo Service Worker quando o utilizador está sem internet."""
    return render(request, 'core/offline.html')

@login_required
@profile_required
def sync_offline_assessment(request):
    """
    API para receber os dados da avaliação guardados no modo offline.
    Espera receber um JSON com o ID da avaliação e as respostas.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assessment_id = data.get('assessment_id')
            answers = data.get('answers', {})

            profile = Profile.objects.get(id=request.session['selected_profile_id'])
            assessment = get_object_or_404(Assessment, id=assessment_id)

            assessment_result = AssessmentResult.objects.create(
                profile=profile,
                assessment=assessment
            )

            for section in assessment.sections.all():
                section_score = 0
                for question in section.questions.all():
                    answer_value = answers.get(f'question_{question.id}')
                    if answer_value is not None:
                        section_score += int(answer_value)
                
                SectionResult.objects.create(
                    assessment_result=assessment_result,
                    section=section,
                    score=section_score
                )

            return JsonResponse({
                'status': 'success', 
                'message': 'Avaliação sincronizada com sucesso!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=400)

    return JsonResponse({'status': 'invalid_method'}, status=405)