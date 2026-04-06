from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profil, Challenge, Yechim, Urinish, BloklanganChallenge, Contest
from .forms import ProfilOzgertirishForm, FoydalanuvchiRoYXatgaOlishForm
from django.contrib import messages

MAX_URINISH = 3

def contest_list(request):
    contests = Contest.objects.all().order_by('-start_date')
    return render(request, 'contests/contest_list.html', {'contests': contests})


def asosiy_sahifa(request):
    return render(request, 'asosiy/asosiy_sahifa.html')


def users_list(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'asosiy/user_list.html', context)


@login_required
def profil(request):
    profil = Profil.objects.get(user=request.user)
    context = {'profil': profil}
    return render(request, 'asosiy/profil.html', context)


@login_required
def profil_ozgartirish(request):
    profil = request.user.profil
    if request.method == 'POST':
        form = ProfilOzgertirishForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(request.path)
    else:
        form = ProfilOzgertirishForm(instance=profil)
    return render(request, 'asosiy/profil_ozgartirish.html', {'form': form})


@login_required
def challenge_list(request):
    challenges = Challenge.objects.all()
    solved_challenges_ids = Yechim.objects.filter(user=request.user).values_list('challenge_id', flat=True)

    qiyinlik_tanlovlari = Challenge.qiyinlik_choices
    ochko_tanlovlari = Challenge.objects.values_list('ochko', flat=True).distinct().order_by('ochko')
    kategoriya_tanlovlari = Challenge.objects.values_list('kategoriya', flat=True).distinct()

    qiyinlik = request.GET.get('qiyinlik')
    ochko = request.GET.get('ochko')
    kategoriya = request.GET.get('kategoriya')

    if qiyinlik:
        challenges = challenges.filter(qiyinlik=qiyinlik)
    if ochko:
        challenges = challenges.filter(ochko=ochko)
    if kategoriya:
        challenges = challenges.filter(kategoriya=kategoriya)

    context = {
        'challenges': challenges,
        'solved_challenges': list(solved_challenges_ids),
        'qiyinlik_tanlovlari': qiyinlik_tanlovlari,
        'ochko_tanlovlari': ochko_tanlovlari,
        'kategoriya_tanlovlari': kategoriya_tanlovlari,
    }
    return render(request, 'asosiy/challenge_list.html', context)


@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    urinishlar_soni = Urinish.objects.filter(user=request.user, challenge=challenge).count()
    bloklangan = BloklanganChallenge.objects.filter(user=request.user, challenge=challenge).exists()

    first_solvers = Yechim.objects.filter(challenge=challenge).order_by('yechilgan_vaqt')[:5]
    solvers_data = []

    for i, yechim in enumerate(first_solvers):
        try:
            p = Profil.objects.get(user=yechim.user)
            solvers_data.append({
                'id': i + 1,
                'img': p.img.url if p.img else '/static/default_user.png',
                'username': yechim.user.username,
                'email': yechim.user.email,
                'country': p.country,
            })
        except Profil.DoesNotExist:
            solvers_data.append({
                'id': i + 1,
                'img': '/static/default_user.png',
                'username': yechim.user.username,
                'email': yechim.user.email,
                'country': '',
            })

    return render(request, 'asosiy/challenge_detail.html', {
        'challenge': challenge,
        'urinishlar_soni': urinishlar_soni,
        'max_urinish': MAX_URINISH,
        'bloklangan': bloklangan,
        'first_solvers_data': solvers_data,
    })


@login_required
def yechish(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if BloklanganChallenge.objects.filter(user=request.user, challenge=challenge).exists():
        messages.warning(request, "Bu challenge siz uchun bloklangan.")
        return redirect('challenge_detail', challenge_id=challenge_id)

    if Yechim.objects.filter(user=request.user, challenge=challenge).exists():
        messages.info(request, "Siz buni allaqachon yechgansiz.")
        return redirect('challenge_list')

    urinishlar_soni = Urinish.objects.filter(user=request.user, challenge=challenge).count()

    if request.method == 'POST':
        flag = request.POST.get('flag')
        Urinish.objects.create(user=request.user, challenge=challenge, javob=flag)

        if flag == challenge.flag:
            avvalgi_yechimlar = Yechim.objects.filter(challenge=challenge).count()
            olingan_ball = max(1, challenge.ochko - avvalgi_yechimlar)

            Yechim.objects.create(user=request.user, challenge=challenge)
            challenge.solved_count = Yechim.objects.filter(challenge=challenge).count()
            challenge.save()

            messages.success(request, f"Tabriklaymiz! Siz {olingan_ball} ball oldingiz.")
            return redirect('challenge_list')
        else:
            if urinishlar_soni + 1 >= MAX_URINISH:
                BloklanganChallenge.objects.create(user=request.user, challenge=challenge)
                messages.error(request, f"Xato! {MAX_URINISH} ta urinish tugadi. Bloklandingiz.")
            else:
                messages.error(request, "Xato flag! Umumiy balingizdan -1 chegirildi.")
            return redirect('challenge_detail', challenge_id=challenge_id)

    return redirect('challenge_detail', challenge_id=challenge_id)


def scoreboard(request):
    users = User.objects.all()
    scoreboard_list = []

    for user in users:
        total_points = 0
        yechimlar = Yechim.objects.filter(user=user).select_related('challenge')

        for y in yechimlar:
            rank_in_challenge = Yechim.objects.filter(
                challenge=y.challenge,
                yechilgan_vaqt__lt=y.yechilgan_vaqt
            ).count()
            total_points += max(1, y.challenge.ochko - rank_in_challenge)

        xato_soni = 0
        barcha_urinishlar = Urinish.objects.filter(user=user).select_related('challenge')
        for u in barcha_urinishlar:
            if u.javob != u.challenge.flag:
                xato_soni += 1

        final_score = total_points - xato_soni

        scoreboard_list.append({
            'user': user,
            'total_score': final_score,
            'solved_count': yechimlar.count(),
            'penalty': xato_soni,
        })

    ranked_data = sorted(scoreboard_list, key=lambda x: x['total_score'], reverse=True)

    for index, data in enumerate(ranked_data):
        data['rank'] = index + 1

    return render(request, 'asosiy/scoreboard.html', {'scoreboard_data': ranked_data})


def register(request):
    if request.method == 'POST':
        form = FoydalanuvchiRoYXatgaOlishForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = FoydalanuvchiRoYXatgaOlishForm()
    return render(request, 'registration/register.html', {'form': form})
