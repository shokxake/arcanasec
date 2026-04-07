from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# 1. Profil Modeli
class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, null=True)
    img = models.ImageField(default='arcana.jpg', upload_to='profil_rasmlari')

    def __str__(self):
        return self.user.username


# 2. Contest (Musobaqa) Modeli
class Contest(models.Model):
    FORMAT_CHOICES = [
        ('jeopardy', 'Jeopardy'),
        ('attack-defense', 'Attack-Defense'),
    ]

    TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    PARTICIPATION_CHOICES = [
        ('single', 'Single Player'),
        ('team', 'Team'),
    ]

    nomi = models.CharField(max_length=200)
    tavsif = models.TextField(blank=True, null=True)
    formati = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='jeopardy')
    tipi = models.CharField(max_length=20, choices=TYPE_CHOICES, default='public')
    qatnashish = models.CharField(max_length=50, choices=PARTICIPATION_CHOICES, default='single')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.nomi

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def has_started(self):
        return timezone.now() >= self.start_date

    @property
    def has_ended(self):
        return timezone.now() > self.end_date

    class Meta:
        verbose_name = "Contest"
        verbose_name_plural = "Contests"


# 3. Challenge (Masala) Modeli
class Challenge(models.Model):
    qiyinlik_choices = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    nomi = models.CharField(max_length=255)
    tavsif = models.TextField()
    fayl = models.FileField(upload_to='challenge_fayllari/', blank=True, null=True)
    flag = models.CharField(max_length=255)
    kategoriya = models.CharField(max_length=100, blank=True, null=True)
    qiyinlik = models.CharField(max_length=10, choices=qiyinlik_choices, default='easy')

    # contest bo'sh bo'lsa practice challenge
    contest = models.ForeignKey(
        Contest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='challenges'
    )

    ochko = models.IntegerField(default=10)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_count = models.IntegerField(default=0)
    urinishlar_soni = models.IntegerField(default=0)

    def __str__(self):
        return self.nomi


# 4. Contest qatnashchilari
class ContestParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'contest')
        verbose_name = "Contest Participant"
        verbose_name_plural = "Contest Participants"

    def __str__(self):
        return f"{self.user.username} -> {self.contest.nomi}"


# 5. Yechim Modeli
class Yechim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True, blank=True)
    yechilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} - {self.challenge.nomi}"


# 6. Urinish Modeli
class Urinish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    urinish_vaqti = models.DateTimeField(auto_now_add=True)
    javob = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Urinishlar"

    def is_correct(self):
        return self.javob == self.challenge.flag


# 7. Bloklangan Challenge Modeli
class BloklanganChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    bloklangan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} - {self.challenge.nomi}"