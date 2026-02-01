"""
刘氏乾正公族谱 - 后台管理配置
"""
from django.contrib import admin
from .models import Generation, Branch, Person, SpouseRelation, GenealogyRecord, UserProfile


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'description']
    ordering = ['number']
    search_fields = ['name', 'description']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'founder', 'location']
    search_fields = ['name', 'description', 'location']
    filter_horizontal = []


class SpouseRelationInline(admin.TabularInline):
    model = SpouseRelation
    fk_name = 'husband'
    extra = 1


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'courtesy_name',
        'art_name',
        'generation',
        'gender',
        'father',
        'birth_year',
        'death_year',
        'branch',
    ]
    list_filter = [
        'generation__number',
        'gender',
        'branch',
        'birth_year',
    ]
    search_fields = [
        'name',
        'courtesy_name',
        'art_name',
        'alias',
        'biography',
        'notes',
    ]
    raw_id_fields = ['father', 'mother']
    inlines = [SpouseRelationInline]
    fieldsets = (
        ('基本信息', {
            'fields': (
                'name',
                'courtesy_name',
                'art_name',
                'alias',
                'gender',
                'generation',
            )
        }),
        ('家族关系', {
            'fields': (
                'father',
                'mother',
                'branch',
            )
        }),
        ('生卒信息', {
            'fields': (
                'birth_year',
                'death_year',
                'birth_place',
            )
        }),
        ('墓葬信息', {
            'fields': (
                'burial_place',
                'burial_fengshui',
                'burial_direction',
            ),
            'classes': ('collapse',)
        }),
        ('生平事迹', {
            'fields': (
                'biography',
                'achievements',
                'descendants_location',
            ),
            'classes': ('collapse',)
        }),
        ('其他', {
            'fields': (
                'notes',
                'order',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(SpouseRelation)
class SpouseRelationAdmin(admin.ModelAdmin):
    list_display = ['husband', 'wife', 'order']
    list_filter = ['order']
    search_fields = ['husband__name', 'wife__name']


@admin.register(GenealogyRecord)
class GenealogyRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'page_number']
    search_fields = ['title', 'content', 'source']
    filter_horizontal = ['related_persons']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'related_person']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['related_person']
