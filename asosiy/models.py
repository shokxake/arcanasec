from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, null=True)
    img = models.ImageField(default='arcana.jpg', upload_to='profil_rasmlari')

    def __str__(self):
        return f"{self.user.username}"

class Challenge(models.Model):
    nomi = models.CharField(max_length=255)
    tavsif = models.TextField()
    fayl = models.FileField(upload_to='challenge_fayllari/', blank=True, null=True)
    flag = models.CharField(max_length=255)
    kategoriya = models.CharField(max_length=100, blank=True, null=True)
    qiyinlik = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='easy'
    )






    ochko = models.IntegerField(default=10)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_count = models.IntegerField(default=0)
    urinishlar_soni = models.IntegerField(default=0)

    def __str__(self):
        return self.nomi

    def get_difficulty_display(self):
        return dict(self.qiyinlik_choices)[self.qiyinlik]

    qiyinlik_choices = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

class Yechim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    yechilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')

class Urinish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    urinish_vaqti = models.DateTimeField(auto_now_add=True)
    javob = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Urinishlar"

    def is_correct(self):
        return self.javob == self.challenge.flag

class BloklanganChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    bloklangan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge',)

    def __str__(self):
        return f"{self.user.username} - {self.challenge.nomi}"



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
    formati = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='jeopardy')
    tipi = models.CharField(max_length=20, choices=TYPE_CHOICES, default='public')
    qatnashish = models.CharField(max_length=50, choices=PARTICIPATION_CHOICES, default='single')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "Contest"
        verbose_name_plural = "Contests"