from django.contrib import admin
from django.utils import timezone
from .models import (
    Profil,
    Challenge,
    Yechim,
    Urinish,
    BloklanganChallenge,
    Contest,
    ContestParticipant
)


# 1. Profil Admin
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'country')
    search_fields = ('user__username', 'country')
    ordering = ('user__username',)


# 2. Contest Admin
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = (
        'nomi',
        'formati',
        'tipi',
        'qatnashish',
        'start_date',
        'end_date',
        'contest_status',
    )
    list_filter = ('tipi', 'formati', 'qatnashish', 'start_date', 'end_date')
    search_fields = ('nomi', 'tavsif')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

    fieldsets = (
        ('Asosiy maʼlumotlar', {
            'fields': ('nomi', 'tavsif')
        }),
        ('Contest sozlamalari', {
            'fields': ('formati', 'tipi', 'qatnashish')
        }),
        ('Vaqt', {
            'fields': ('start_date', 'end_date')
        }),
    )

    def contest_status(self, obj):
        now = timezone.now()
        if now < obj.start_date:
            return "Upcoming"
        elif obj.start_date <= now <= obj.end_date:
            return "Active"
        return "Ended"

    contest_status.short_description = "Holati"


# 3. Contest Participant Admin
@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'joined_at')
    list_filter = ('contest', 'joined_at')
    search_fields = ('user__username', 'contest__nomi')
    ordering = ('-joined_at',)


# 4. Challenge Admin
@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'nomi',
        'contest',
        'challenge_mode',
        'kategoriya',
        'qiyinlik',
        'ochko',
        'author',
        'solved_count',
        'yaratilgan_vaqt',
    )
    list_filter = ('contest', 'kategoriya', 'qiyinlik', 'author', 'yaratilgan_vaqt')
    search_fields = ('nomi', 'tavsif', 'flag', 'kategoriya', 'author__username')
    ordering = ('nomi',)
    readonly_fields = ('solved_count', 'yaratilgan_vaqt')

    fieldsets = (
        ('Asosiy maʼlumotlar', {
            'fields': ('nomi', 'tavsif', 'fayl', 'flag')
        }),
        ('Tasnif', {
            'fields': ('kategoriya', 'qiyinlik', 'ochko')
        }),
        ('Bogʻlanishlar', {
            'fields': ('contest', 'author')
        }),
        ('Statistika', {
            'fields': ('solved_count', 'yaratilgan_vaqt')
        }),
    )

    actions = ['nolga_tushirish_solved_count']

    def challenge_mode(self, obj):
        return "Contest" if obj.contest else "Practice"

    challenge_mode.short_description = "Mode"

    def nolga_tushirish_solved_count(self, request, queryset):
        updated = queryset.update(solved_count=0)
        self.message_user(
            request,
            f"{updated} ta masalaning solved_count qiymati 0 ga tushirildi."
        )

    nolga_tushirish_solved_count.short_description = (
        "Tanlangan masalalarning solved_count qiymatini 0 ga tushirish"
    )


# 5. Yechim Admin
@admin.register(Yechim)
class YechimAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'contest', 'challenge_mode', 'yechilgan_vaqt')
    list_filter = ('contest', 'challenge', 'user', 'yechilgan_vaqt')
    search_fields = ('user__username', 'challenge__nomi', 'contest__nomi')
    ordering = ('-yechilgan_vaqt',)

    def challenge_mode(self, obj):
        return "Contest" if obj.contest else "Practice"

    challenge_mode.short_description = "Mode"


# 6. Urinish Admin
@admin.register(Urinish)
class UrinishAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'challenge_contest', 'javob', 'urinish_vaqti', 'is_correct_display')
    list_filter = ('challenge__contest', 'user', 'challenge', 'urinish_vaqti')
    search_fields = ('user__username', 'challenge__nomi', 'javob')
    ordering = ('-urinish_vaqti',)

    def challenge_contest(self, obj):
        return obj.challenge.contest.nomi if obj.challenge.contest else "Practice"

    challenge_contest.short_description = "Contest"

    def is_correct_display(self, obj):
        return obj.is_correct()

    is_correct_display.short_description = "To'g'ri javob"
    is_correct_display.boolean = True


# 7. Bloklangan Challenge Admin
@admin.register(BloklanganChallenge)
class BloklanganChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'challenge_contest', 'bloklangan_vaqt')
    list_filter = ('challenge__contest', 'user', 'challenge', 'bloklangan_vaqt')
    search_fields = ('user__username', 'challenge__nomi')
    ordering = ('-bloklangan_vaqt',)
    actions = ['ochish_bloklangan_va_urinishlarni_tiklash']

    def challenge_contest(self, obj):
        return obj.challenge.contest.nomi if obj.challenge.contest else "Practice"

    challenge_contest.short_description = "Contest"

    def ochish_bloklangan_va_urinishlarni_tiklash(self, request, queryset):
        count = queryset.count()
        for blocked_challenge in queryset:
            Urinish.objects.filter(
                user=blocked_challenge.user,
                challenge=blocked_challenge.challenge
            ).delete()
            blocked_challenge.delete()

        self.message_user(request, f"{count} ta blok ochildi va urinishlar tozalandi.")

    ochish_bloklangan_va_urinishlarni_tiklash.short_description = (
        "Tanlangan bloklarni ochish va urinishlarni tozalash"
    )