from django.contrib import admin
from .models import Profil, Challenge, Yechim, Urinish, BloklanganChallenge, Contest, ContestParticipant
from django.db.models import Count

# 1. Profil Admin
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'country')
    search_fields = ('user__username', 'country')

# 2. Contest Admin
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'formati', 'tipi', 'qatnashish', 'start_date', 'end_date')
    list_filter = ('tipi', 'formati', 'qatnashish')
    search_fields = ('nomi', 'tavsif')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

# 3. Contest Participant Admin (Yangi qo'shildi)
@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'joined_at')
    list_filter = ('contest', 'joined_at')
    search_fields = ('user__username', 'contest__nomi')

# 4. Challenge Admin (Contest maydoni bilan yangilandi)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'contest', 'kategoriya', 'qiyinlik', 'ochko', 'solved_count')
    # Endi contest bo'yicha ham filtrlasa bo'ladi
    list_filter = ('contest', 'kategoriya', 'qiyinlik', 'author')
    search_fields = ('nomi', 'tavsif', 'flag')
    prepopulated_fields = {'nomi': ('nomi',)}
    ordering = ('nomi',)
    readonly_fields = ('solved_count',)
    actions = ['nolga_tushirish_solved_count']

    def nolga_tushirish_solved_count(self, request, queryset):
        queryset.update(solved_count=0)
        self.message_user(request, f"{queryset.count()} ta masalaning yechganlar soni 0 ga tushirildi.")
    
    nolga_tushirish_solved_count.short_description = "Tanlangan masalalarning yechimlar sonini 0 ga tushirish"

admin.site.register(Challenge, ChallengeAdmin)

# 5. Yechim Admin
@admin.register(Yechim)
class YechimAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'contest', 'yechilgan_vaqt')
    list_filter = ('contest', 'challenge', 'user', 'yechilgan_vaqt')
    search_fields = ('user__username', 'challenge__nomi', 'contest__nomi')
    ordering = ('-yechilgan_vaqt',)

# 6. Urinish Admin
@admin.register(Urinish)
class UrinishAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'javob', 'urinish_vaqti', 'is_correct_display')
    list_filter = ('user', 'challenge', 'urinish_vaqti')
    search_fields = ('user__username', 'challenge__nomi', 'javob')

    def is_correct_display(self, obj):
        return obj.is_correct()

    is_correct_display.short_description = "To'g'ri javob"
    is_correct_display.boolean = True

# 7. Bloklangan Challenge Admin
@admin.register(BloklanganChallenge)
class BloklanganChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'bloklangan_vaqt')
    list_filter = ('user', 'challenge')
    search_fields = ('user__username', 'challenge__nomi')
    actions = ['ochish_bloklangan_va_urinishlarni_tiklash']

    def ochish_bloklangan_va_urinishlarni_tiklash(self, request, queryset):
        for blocked_challenge in queryset:
            Urinish.objects.filter(user=blocked_challenge.user, challenge=blocked_challenge.challenge).delete()
            blocked_challenge.delete()
        self.message_user(request, f"{queryset.count()} ta blok ochildi.")