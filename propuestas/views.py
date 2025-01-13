import requests
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, PropuestaForm, PropuestaFormEmpresa, UserUpdateForm, EmailUpdateForm, EmpresaRegistroForm, FinanciarForm, CommentForm
from .models import Usuario, Propuesta, Comment
from django.views.generic import DetailView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, login
from django.urls import reverse_lazy
from django.http import JsonResponse

API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"

def fetch_provincias():
    url = f"{API_BASE_URL}provincias"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        provincias = sorted([(provincia['id'], provincia['nombre']) for provincia in data.get('provincias', [])], key=lambda x: x[1])
        return provincias
    return []


def register(request):
    context = {
        'comun_form': RegistroForm(),
        'empresa_form': EmpresaRegistroForm(),
        'show_comun_form': request.GET.get('type') == 'comun',
        'show_empresa_form': request.GET.get('type') == 'empresa'
    }
    return render(request, 'registration/register.html', context)

def register_comun(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'comun'
            user.save()
            messages.success(request, 'Registro exitoso. Por favor, inicie sesión.')
            return redirect('login')  # Redirect to login page
        else:
            return render(request, 'registration/register.html', {
                'comun_form': form,
                'empresa_form': EmpresaRegistroForm(),
                'show_comun_form': True
            })
    else:
        form = RegistroForm()
    return render(request, 'registration/register.html', {
        'comun_form': form,
        'empresa_form': EmpresaRegistroForm(),
        'show_comun_form': True
    })

def register_empresa(request):
    if request.method == 'POST':
        form = EmpresaRegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'empresa'
            user.save()
            messages.success(request, 'Registro exitoso. Por favor, inicie sesión.')
            return redirect('login')  # Redirect to login page
        else:
            return render(request, 'registration/register.html', {
                'empresa_form': form,
                'comun_form': RegistroForm(),
                'show_empresa_form': True
            })
    else:
        form = EmpresaRegistroForm()
    return render(request, 'registration/register.html', {
        'empresa_form': form,
        'comun_form': RegistroForm(),
        'show_empresa_form': True
    })

@login_required
def register_redirect(request):
    messages.warning(request, 'Ya estás logueado.')
    return redirect('index')


@login_required
def proponer(request):
    if request.method == 'POST':
        if request.user.tipo_usuario == 'empresa':
            form = PropuestaFormEmpresa(request.POST, request.FILES)
        else:
            form = PropuestaForm(request.POST, request.FILES)

        if form.is_valid():
            propuesta = form.save(commit=False)
            propuesta.creador = request.user
            if request.user.tipo_usuario == 'empresa' and propuesta.FORMULARIO_FINANCIAMIENTO:
                propuesta.buscando_inversiones = False
                propuesta.llamado_a_licitacion = False  # Assuming you want to set this to False initially.
            propuesta.save()
            messages.success(request, 'Propuesta creada correctamente.')
            return redirect('propuestas')
    else:
        if request.user.tipo_usuario == 'empresa':
            form = PropuestaFormEmpresa()
        else:
            form = PropuestaForm()

    return render(request, 'proponer.html', {'form': form})

@login_required
def propuestas(request):
    provincia = request.GET.get('provincia', '')
    if provincia:
        propuestas = Propuesta.objects.filter(PROVINCIA=provincia)
    else:
        propuestas = Propuesta.objects.all()

    for propuesta in propuestas:
        propuesta.ya_rateado = request.user in propuesta.usuarios_que_han_rateado.all()

    propuestas_in_votacion = []
    propuestas_inversiones = []

    for propuesta in propuestas:
        if not propuesta.buscando_inversiones:
            if propuesta.votos_positivos >= 10000 and propuesta.votos_negativos < (propuesta.votos_positivos / 2):
                propuesta.buscando_inversiones = True
                propuesta.save()
                propuestas_inversiones.append(propuesta)
            else:
                propuestas_in_votacion.append(propuesta)

    context = {
        'propuestas': propuestas_in_votacion,
        'provincia': provincia,
        'propuestas_inversiones': propuestas_inversiones
    }

    return render(request, 'propuestas.html', context)

def propuesta_detail(request, pk):
    propuesta = get_object_or_404(Propuesta, pk=pk)
    comments = Comment.objects.filter(propuesta=propuesta)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.propuesta = propuesta
            comment.user = request.user
            comment.save()
            return redirect('propuesta_detail', pk=pk)  # Redirect to avoid re-posting on refresh
    else:
        form = CommentForm()

    comments_data = [
        {
            'comment': comment.comment,
            'display_name': comment.user.nombre_empresa if comment.user.tipo_usuario == 'empresa' else comment.user.username
        }
        for comment in comments
    ]

    return render(request, 'propuesta_detail.html', {
        'propuesta': propuesta,
        'comments': comments_data,
        'form': form
    })

@login_required
def rate_propuesta(request, propuesta_id):
    propuesta = get_object_or_404(Propuesta, pk=propuesta_id)
    provincia = request.POST.get('provincia', '')
    voto = request.POST.get('voto')

    if request.method == 'POST' and request.user not in propuesta.usuarios_que_han_rateado.all():
        if voto == '+':
            propuesta.votos_positivos += 1
        elif voto == '-':
            propuesta.votos_negativos += 1
        else:
            messages.warning(request, 'Voto inválido. Debe elegir positivo (+) o negativo (-)')
            return redirect(f'/propuestas/?provincia={provincia}')

        propuesta.usuarios_que_han_rateado.add(request.user)
        propuesta.save()

        # Redirect based on the type of Propuesta
        if propuesta.votos_positivos >= 10000 and propuesta.votos_negativos < (propuesta.votos_positivos / 2):
            if propuesta.creador.tipo_usuario == 'empresa' and propuesta.FORMULARIO_FINANCIAMIENTO:
                propuesta.llamado_a_licitacion = True  # Mark as ready for "Llamado a Licitación"
                propuesta.save()
                messages.success(request, 'La propuesta ha sido movida a Llamado a Licitación.')
                return redirect('llamado_a_licitacion', propuesta_id=propuesta.id)
            else:
                propuesta.buscando_inversiones = True  # Default behavior
                propuesta.save()
                messages.success(request, 'La propuesta ha sido movida a Buscando Inversiones.')

    return redirect(f'/propuestas/?provincia={provincia}')


@login_required
def propuestas_inversiones(request):
    provincia = request.GET.get('provincia')
    if provincia:
        propuestas = Propuesta.objects.filter(
            PROVINCIA=provincia,
            votos_positivos__gte=10000,
            votos_negativos__lte=5000
        )
    else:
        propuestas = Propuesta.objects.filter(
            votos_positivos__gte=10000,
            votos_negativos__lte=5000
        )
    return render(request, 'propuestas_inversiones.html', {'propuestas': propuestas})

@login_required
def financiar_propuesta(request, propuesta_id):
    propuesta = get_object_or_404(Propuesta, pk=propuesta_id)
    user = request.user

    if user.tipo_usuario != 'empresa':
        messages.warning(request, 'Solo las empresas pueden financiar propuestas.')
        return redirect('propuestas')

    # Prevent financing if the proposal was created by another Usuario Empresa
    if propuesta.creador.tipo_usuario == 'empresa':
        messages.warning(request, 'No puedes financiar una propuesta creada por otra empresa.')
        return redirect('propuesta_detail', pk=propuesta_id)

    # Check if the user has already financed this proposal
    if propuesta.empresas_que_financian.filter(id=user.id).exists():
        messages.warning(request, 'Ya has financiado esta propuesta.')
        return redirect('propuesta_detail', pk=propuesta_id)

    if request.method == 'POST':
        form = FinanciarForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            propuesta.FORMULARIO_FINANCIAMIENTO = archivo
            propuesta.empresas_que_financian.add(user)
            propuesta.save()
            messages.success(request, 'Has financiado la propuesta correctamente.')
            return redirect('propuesta_detail', pk=propuesta_id)
    else:
        form = FinanciarForm()

    return render(request, 'financiar_propuesta.html', {'form': form, 'propuesta': propuesta})

@login_required
def llamado_a_licitacion(request):
    propuestas = Propuesta.objects.filter(llamado_a_licitacion=True)
    return render(request, 'llamado_a_licitacion.html', {'propuestas': propuestas})


@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        email_form = EmailUpdateForm(request.POST, instance=user)
        user_form = UserUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if email_form.is_valid():
            email_form.save()
        if user_form.is_valid():
            user_form.save()
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in after password change
        return redirect('profile')
    else:
        email_form = EmailUpdateForm(instance=user)
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    user_proposals = Propuesta.objects.filter(creador=user)  # Changed to filter by creator

    context = {
        'email_form': email_form,
        'user_form': user_form,
        'password_form': password_form,
        'user_proposals': user_proposals
    }

    return render(request, 'profile.html', context)


def index(request):
    return render(request, 'index.html')

class PropuestaDetailView(DetailView):
    model = Propuesta
    template_name = 'propuesta_detail.html'
    context_object_name = 'propuesta'


# Login View
login_view = LoginView.as_view(template_name='registration/login.html')

# Logout View
logout_view = LogoutView.as_view(template_name='registration/logged_out.html')
