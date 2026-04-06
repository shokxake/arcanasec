from django.contrib import admin
from .models import Profil, Challenge, Yechim, Urinish, BloklanganChallenge, Contest
from django.db.models import Count

# 1. Profil Admin
admin.site.register(Profil)

# 2. Challenge Admin
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'kategoriya', 'qiyinlik', 'ochko', 'author', 'solved_count', 'fayl')
    list_filter = ('kategoriya', 'qiyinlik', 'author')
    search_fields = ('nomi', 'tavsif', 'flag')
    prepopulated_fields = {'nomi': ('nomi',)}
    ordering = ('nomi',)
    readonly_fields = ('solved_count',) # urinishlar_soni o'rniga solved_count ishlatdik
    actions = ['nolga_tushirish_solved_count']

    def nolga_tushirish_solved_count(self, request, queryset):
        queryset.update(solved_count=0)
        self.message_user(request, f"{queryset.count()} ta challenge'ning yechganlar soni 0 ga tushirildi.")
    
    nolga_tushirish_solved_count.short_description = "Tanlangan challengelarning yechganlar sonini 0 ga tushirish"

admin.site.register(Challenge, ChallengeAdmin)

# 3. Yechim Admin
class YechimAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'yechilgan_vaqt')
    list_filter = ('user', 'challenge', 'yechilgan_vaqt')
    search_fields = ('user__username', 'challenge__nomi')
    ordering = ('-yechilgan_vaqt',) 

admin.site.register(Yechim, YechimAdmin)

# 4. Bloklangan Challenge Admin
class BloklanganChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'bloklangan_vaqt')
    list_filter = ('user', 'challenge')
    search_fields = ('user__username', 'challenge__nomi')
    ordering = ('bloklangan_vaqt',)
    actions = ['ochish_bloklangan_va_urinishlarni_tiklash']

    def ochish_bloklangan_va_urinishlarni_tiklash(self, request, queryset):
        for blocked_challenge in queryset:
            Urinish.objects.filter(user=blocked_challenge.user, challenge=blocked_challenge.challenge).delete()
            blocked_challenge.delete()
        self.message_user(request, f"{queryset.count()} ta bloklangan challenge ochildi va urinishlar tiklandi.")
    
    ochish_bloklangan_va_urinishlarni_tiklash.short_description = "Tanlangan bloklarni ochish va urinishlarni tiklash"

admin.site.register(BloklanganChallenge, BloklanganChallengeAdmin)

# 5. Urinish Admin
class UrinishAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'javob', 'urinish_vaqti', 'is_correct_display')
    list_filter = ('user', 'challenge', 'urinish_vaqti')
    search_fields = ('user__username', 'challenge__nomi', 'javob')

    def is_correct_display(self, obj):
        return obj.is_correct()

    is_correct_display.short_description = "To'g'ri javob"
    is_correct_display.boolean = True

admin.site.register(Urinish, UrinishAdmin)

# 6. Contest Admin (Yangi qo'shilgan)
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    # Ro'yxatda ko'rinadigan ustunlar
    list_display = ('nomi', 'formati', 'tipi', 'qatnashish', 'start_date', 'end_date')
    
    # Filtrlash paneli (o'ng tomonda)
    list_filter = ('tipi', 'formati', 'qatnashish', 'start_date')
    
    # Qidiruv maydoni
    search_fields = ('nomi',)
    
    # Sanalar bo'yicha iyerarxiya (tepada kalendar filtri chiqadi)
    date_hierarchy = 'start_date'
    
    # Ma'lumotlarni tartiblash (eng yangi contest tepada)
    ordering = ('-start_date',)