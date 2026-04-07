from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profil, Challenge, Yechim, Urinish, BloklanganChallenge, Contest, ContestParticipant
from .forms import ProfilOzgertirishForm, FoydalanuvchiRoYXatgaOlishForm
from django.contrib import messages
from django.db.models import Sum

MAX_URINISH = 3


# --- CONTEST LIST ---
def contest_list(request):
    contests = Contest.objects.all().order_by('-start_date')
    return render(request, 'contests/contest_list.html', {'contests': contests})


# --- CONTEST DETAIL (JOIN PAGE) ---
@login_required
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    is_joined = ContestParticipant.objects.filter(user=request.user, contest=contest).exists()
    return render(request, 'contests/contest_detail.html', {
        'contest': contest,
        'is_joined': is_joined
    })


# --- JOIN LOGIC ---
@login_required
def join_contest(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    ContestParticipant.objects.get_or_create(user=request.user, contest=contest)
    messages.success(request, f"Welcome to {contest.nomi}!")
    return redirect('contest_challenges', contest_id=contest.id)


# --- CONTEST CHALLENGES ---
@login_required
def contest_challenges(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # Faqat shu contestga tegishli challengelar
    challenges = Challenge.objects.filter(contest=contest)

    solved_ids = Yechim.objects.filter(
        user=request.user,
        challenge__contest=contest
    ).values_list('challenge_id', flat=True)

    return render(request, 'contests/contest_challenges.html', {
        'contest': contest,
        'challenges': challenges,
        'solved_challenges': list(solved_ids)
    })


# --- CONTEST CHALLENGE DETAIL ---
@login_required
def contest_challenge_detail(request, contest_id, challenge_id):
    contest = get_object_or_404(Contest, id=contest_id)
    challenge = get_object_or_404(Challenge, id=challenge_id, contest=contest)

    # user contestga qo'shilgan bo'lishi shart
    if not ContestParticipant.objects.filter(user=request.user, contest=contest).exists():
        messages.error(request, "Avval musobaqaga qo'shiling!")
        return redirect('contest_detail', contest_id=contest.id)

    urinishlar_soni = Urinish.objects.filter(user=request.user, challenge=challenge).count()
    bloklangan = BloklanganChallenge.objects.filter(user=request.user, challenge=challenge).exists()

    first_solvers = Yechim.objects.filter(
        challenge=challenge
    ).select_related('user', 'user__profil').order_by('yechilgan_vaqt')[:5]

    first_solvers_data = [yechim.user for yechim in first_solvers]

    return render(request, 'contests/contest_challenge_detail.html', {
        'contest': contest,
        'challenge': challenge,
        'urinishlar_soni': urinishlar_soni,
        'max_urinish': MAX_URINISH,
        'bloklangan': bloklangan,
        'first_solvers_data': first_solvers_data,
    })


# --- CONTEST PARTICIPANTS ---
@login_required
def contest_participants(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    participants = ContestParticipant.objects.filter(contest=contest).select_related('user__profil')
    return render(request, 'contests/contest_participants.html', {
        'contest': contest,
        'participants': participants
    })


# --- CONTEST SCOREBOARD ---
@login_required
def contest_scoreboard(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    participants = ContestParticipant.objects.filter(contest=contest)
    scoreboard_data = []

    for part in participants:
        user = part.user

        yechimlar = Yechim.objects.filter(user=user, challenge__contest=contest)
        total_points = sum([y.challenge.ochko for y in yechimlar])

        solved_flags = yechimlar.values_list('challenge__flag', flat=True)

        penalties = Urinish.objects.filter(
            user=user,
            challenge__contest=contest
        ).exclude(javob__in=solved_flags).count()

        scoreboard_data.append({
            'user': user,
            'total_score': total_points - penalties,
            'solved_count': yechimlar.count(),
            'penalty': penalties
        })

    scoreboard_data = sorted(scoreboard_data, key=lambda x: x['total_score'], reverse=True)

    return render(request, 'contests/contest_scoreboard.html', {
        'contest': contest,
        'scoreboard_data': scoreboard_data
    })


# --- PRACTICE CHALLENGE LIST ---
@login_required
def challenge_list(request):
    challenges = Challenge.objects.filter(contest__isnull=True)
    solved_challenges_ids = Yechim.objects.filter(
        user=request.user,
        challenge__contest__isnull=True
    ).values_list('challenge_id', flat=True)

    qiyinlik = request.GET.get('qiyinlik')
    if qiyinlik:
        challenges = challenges.filter(qiyinlik=qiyinlik)

    return render(request, 'asosiy/challenge_list.html', {
        'challenges': challenges,
        'solved_challenges': list(solved_challenges_ids),
        'qiyinlik_tanlovlari': Challenge.qiyinlik_choices,
    })


# --- PRACTICE CHALLENGE DETAIL ---
@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if challenge.contest:
        if not ContestParticipant.objects.filter(user=request.user, contest=challenge.contest).exists():
            messages.error(request, "Avval musobaqaga qo'shiling!")
            return redirect('contest_detail', contest_id=challenge.contest.id)

    urinishlar_soni = Urinish.objects.filter(user=request.user, challenge=challenge).count()
    bloklangan = BloklanganChallenge.objects.filter(user=request.user, challenge=challenge).exists()
    first_solvers = Yechim.objects.filter(challenge=challenge).order_by('yechilgan_vaqt')[:5]

    return render(request, 'asosiy/challenge_detail.html', {
        'challenge': challenge,
        'urinishlar_soni': urinishlar_soni,
        'max_urinish': MAX_URINISH,
        'bloklangan': bloklangan,
        'first_solvers': first_solvers,
    })


# --- SOLVE LOGIC ---
@login_required
def yechish(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # qayerdan kelganini bilish uchun
    contest_id = request.POST.get('contest_id')

    if BloklanganChallenge.objects.filter(user=request.user, challenge=challenge).exists():
        messages.warning(request, "Siz bloklangansiz.")
        if challenge.contest:
            return redirect('contest_challenge_detail', contest_id=challenge.contest.id, challenge_id=challenge.id)
        return redirect('challenge_detail', challenge_id=challenge_id)

    if Yechim.objects.filter(user=request.user, challenge=challenge).exists():
        if challenge.contest:
            return redirect('contest_challenge_detail', contest_id=challenge.contest.id, challenge_id=challenge.id)
        return redirect('challenge_list')

    if request.method == 'POST':
        flag = request.POST.get('flag')
        Urinish.objects.create(user=request.user, challenge=challenge, javob=flag)

        if flag == challenge.flag:
            Yechim.objects.create(user=request.user, challenge=challenge, contest=challenge.contest)
            challenge.solved_count += 1
            challenge.save()

            messages.success(request, "Correct Flag!")

            if challenge.contest:
                return redirect('contest_challenge_detail', contest_id=challenge.contest.id, challenge_id=challenge.id)
            return redirect('challenge_list')

        else:
            urinish_count = Urinish.objects.filter(user=request.user, challenge=challenge).count()
            if urinish_count >= MAX_URINISH:
                BloklanganChallenge.objects.get_or_create(user=request.user, challenge=challenge)

            messages.error(request, "Wrong Flag!")

            if challenge.contest:
                return redirect('contest_challenge_detail', contest_id=challenge.contest.id, challenge_id=challenge.id)

    return redirect('challenge_detail', challenge_id=challenge_id)


# --- QOLGAN FUNKSIYALAR (PROFIL, AUTH) ---
def asosiy_sahifa(request):
    return render(request, 'asosiy/asosiy_sahifa.html')


def users_list(request):
    users = User.objects.all().select_related('profil')
    return render(request, 'asosiy/user_list.html', {'users': users})


@login_required
def profil(request):
    profil = get_object_or_404(Profil, user=request.user)
    return render(request, 'asosiy/profil.html', {'profil': profil})


@login_required
def profil_ozgartirish(request):
    profil = request.user.profil
    if request.method == 'POST':
        form = ProfilOzgertirishForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profil')
    else:
        form = ProfilOzgertirishForm(instance=profil)
    return render(request, 'asosiy/profil_ozgartirish.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = FoydalanuvchiRoYXatgaOlishForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = FoydalanuvchiRoYXatgaOlishForm()
    return render(request, 'registration/register.html', {'form': form})


# --- UMUMIY SCOREBOARD (PRACTICE) ---
def scoreboard(request):
    users = User.objects.all()
    sb = []

    for user in users:
        pts = Yechim.objects.filter(
            user=user,
            contest__isnull=True
        ).aggregate(s=Sum('challenge__ochko'))['s'] or 0

        sb.append({
            'user': user,
            'total_score': pts
        })

    return render(request, 'asosiy/scoreboard.html', {
        'scoreboard_data': sorted(sb, key=lambda x: x['total_score'], reverse=True)
    })