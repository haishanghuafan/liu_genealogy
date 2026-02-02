"""
刘氏乾正公族谱 - 后台管理配置
"""
from django.contrib import admin
from .models import Generation, Branch, Person, SpouseRelation, GenealogyRecord, UserProfile, PersonImage, PersonVideo


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ['number', 'is_spouse', 'name', 'description']
    list_filter = ['is_spouse']
    ordering = ['number', 'is_spouse']
    search_fields = ['name', 'description']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'founder', 'location']
    search_fields = ['name', 'description', 'location']
    filter_horizontal = []


class HusbandSpouseRelationInline(admin.TabularInline):
    model = SpouseRelation
    fk_name = 'husband'
    extra = 1

class WifeSpouseRelationInline(admin.TabularInline):
    model = SpouseRelation
    fk_name = 'wife'
    extra = 1


class PersonImageInline(admin.TabularInline):
    model = PersonImage
    extra = 1


class PersonVideoInline(admin.TabularInline):
    model = PersonVideo
    extra = 1


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'courtesy_name',
        'art_name',
        'generation',
        'gender',
        'is_outsider',
        'father',
        'birth_year',
        'death_year',
        'branch',
        'has_avatar',
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
    
    def get_inlines(self, request, obj=None):
        # 根据当前人物的性别动态选择inline
        inlines = []
        if obj:
            if obj.gender == 'F':
                inlines.append(WifeSpouseRelationInline)
            else:
                inlines.append(HusbandSpouseRelationInline)
        else:
            # 新建时默认使用丈夫关系
            inlines.append(HusbandSpouseRelationInline)
        inlines.extend([PersonImageInline, PersonVideoInline])
        return inlines
    fieldsets = (
        ('基本信息', {
            'fields': (
                'name',
                'courtesy_name',
                'art_name',
                'alias',
                'gender',
                'is_outsider',
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
        ('多媒体信息', {
            'fields': (
                'avatar',
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
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'generation':
            # 获取当前表单的is_outsider值
            # 从request.POST中获取，或者从instance中获取
            is_outsider = False
            
            # 尝试从POST数据中获取
            if 'is_outsider' in request.POST:
                is_outsider = request.POST.get('is_outsider') == 'on'
            # 尝试从instance中获取（编辑模式）
            elif hasattr(self, 'obj') and self.obj:
                is_outsider = self.obj.is_outsider
            
            # 根据is_outsider过滤世代
            kwargs['queryset'] = Generation.objects.filter(is_spouse=is_outsider)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        # 保存当前实例，供formfield_for_foreignkey使用
        self.obj = obj
        return super().get_form(request, obj, **kwargs)
    
    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'genealogy/js/dynamic_generation.js',
        )


@admin.register(SpouseRelation)
class SpouseRelationAdmin(admin.ModelAdmin):
    list_display = ['husband', 'wife', 'relation_type', 'source_info', 'order']
    list_filter = ['relation_type', 'order']
    search_fields = ['husband__name', 'wife__name', 'source_info']


@admin.register(GenealogyRecord)
class GenealogyRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'page_number', 'has_source_image']
    search_fields = ['title', 'content', 'source']
    filter_horizontal = ['related_persons']


@admin.register(PersonImage)
class PersonImageAdmin(admin.ModelAdmin):
    list_display = ['person', 'title', 'upload_date']
    search_fields = ['person__name', 'title', 'description']
    list_filter = ['person__generation', 'upload_date']


@admin.register(PersonVideo)
class PersonVideoAdmin(admin.ModelAdmin):
    list_display = ['person', 'title', 'upload_date']
    search_fields = ['person__name', 'title', 'description']
    list_filter = ['person__generation', 'upload_date']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'related_person']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['related_person']
