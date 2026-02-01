"""
刘氏乾正公族谱 - 数据模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import FileExtensionValidator


class Generation(models.Model):
    """世代"""
    number = models.IntegerField(verbose_name='世代数')
    is_spouse = models.BooleanField(default=False, verbose_name='是否为配偶世代')
    name = models.CharField(max_length=50, blank=True, verbose_name='世代名称')
    generation_char = models.CharField(max_length=10, blank=True, verbose_name='辈份字')
    description = models.TextField(blank=True, verbose_name='描述')
    
    class Meta:
        verbose_name = '世代'
        verbose_name_plural = '世代'
        ordering = ['number', 'is_spouse']
        unique_together = ['number', 'is_spouse']
    
    def __str__(self):
        base_str = f"第{self.number}世"
        if self.is_spouse:
            base_str += "（配）"
        if self.generation_char:
            base_str += f"({self.generation_char}字辈)"
        return base_str
    
    def get_generation_title(self):
        """获取世代称谓"""
        if self.number == 1:
            title = "始祖"
        elif self.number == 2:
            title = "二世祖"
        elif self.number == 3:
            title = "三世祖"
        elif self.number <= 9:
            title = f"{self.number}世祖"
        else:
            title = f"第{self.number}世"
        
        if self.is_spouse:
            title += "（配）"
        
        return title
    
    def get_person_count(self):
        """获取该世代的人数"""
        return self.persons.count()


class Branch(models.Model):
    """支系"""
    name = models.CharField(max_length=100, verbose_name='支系名称')
    founder = models.ForeignKey(
        'Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='founded_branch',
        verbose_name='开基祖'
    )
    description = models.TextField(blank=True, verbose_name='描述')
    location = models.CharField(max_length=200, blank=True, verbose_name='分布地区')
    
    class Meta:
        verbose_name = '支系'
        verbose_name_plural = '支系'
    
    def __str__(self):
        return self.name


class Person(models.Model):
    """人物"""
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name='姓名')
    courtesy_name = models.CharField(max_length=100, blank=True, verbose_name='字')
    art_name = models.CharField(max_length=100, blank=True, verbose_name='号')
    alias = models.CharField(max_length=100, blank=True, verbose_name='别名')
    
    # 性别
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name='性别')
    
    # 是否为外族配偶
    is_outsider = models.BooleanField(default=False, verbose_name='是否为外族配偶')
    
    # 世代
    generation = models.ForeignKey(
        Generation,
        on_delete=models.CASCADE,
        related_name='persons',
        verbose_name='世代',
        null=True,
        blank=True
    )
    
    # 父母关系
    father = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children_as_father',
        verbose_name='父亲',
        limit_choices_to={'gender': 'M'}
    )
    mother = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children_as_mother',
        verbose_name='母亲',
        limit_choices_to={'gender': 'F'}
    )
    
    # 配偶（多对多关系通过SpouseRelation模型）
    spouses = models.ManyToManyField(
        'self',
        through='SpouseRelation',
        through_fields=('husband', 'wife'),
        symmetrical=False,
        related_name='partners',
        blank=True,
        verbose_name='配偶'
    )
    
    # 支系
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='所属支系'
    )
    
    # 生卒信息
    birth_year = models.IntegerField(null=True, blank=True, verbose_name='出生年份')
    death_year = models.IntegerField(null=True, blank=True, verbose_name='逝世年份')
    birth_place = models.CharField(max_length=200, blank=True, verbose_name='出生地')
    
    # 墓葬信息
    burial_place = models.CharField(max_length=300, blank=True, verbose_name='葬地')
    burial_fengshui = models.CharField(max_length=200, blank=True, verbose_name='墓形/风水')
    burial_direction = models.CharField(max_length=100, blank=True, verbose_name='坐向')
    
    # 生平简介
    biography = models.TextField(blank=True, verbose_name='生平简介')
    achievements = models.TextField(blank=True, verbose_name='主要事迹')
    
    # 后裔分布
    descendants_location = models.TextField(blank=True, verbose_name='后裔分布')
    
    # 备注
    notes = models.TextField(blank=True, verbose_name='备注')
    
    # 排序
    order = models.IntegerField(default=0, verbose_name='排序')
    
    # 多媒体信息
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='头像'
    )
    
    # 用户账号关联
    related_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_person',
        verbose_name='关联用户'
    )
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', '激活'),
            ('inactive', '未激活'),
            ('disabled', '禁用'),
        ],
        default='inactive',
        verbose_name='账号状态'
    )
    
    # 元信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_persons',
        verbose_name='创建者'
    )
    
    class Meta:
        verbose_name = '人物'
        verbose_name_plural = '人物'
        ordering = ['generation__number', 'order', 'id']
    
    def __str__(self):
        if self.courtesy_name:
            return f"{self.name}（字{self.courtesy_name}）"
        return self.name
    
    def get_absolute_url(self):
        return reverse('genealogy:person_detail', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        """获取完整姓名"""
        parts = [self.name]
        if self.courtesy_name:
            parts.append(f"字{self.courtesy_name}")
        if self.art_name:
            parts.append(f"号{self.art_name}")
        return ' '.join(parts)
    
    def get_spouses_list(self):
        """获取配偶列表"""
        return self.spouses.all()
    
    def get_children(self):
        """获取子女列表"""
        if self.gender == 'M':
            return self.children_as_father.all()
        else:
            return self.children_as_mother.all()
    
    def get_siblings(self):
        """获取兄弟姐妹"""
        if self.father:
            siblings = self.father.children_as_father.exclude(pk=self.pk)
            return siblings
        return Person.objects.none()
    
    def get_all_children(self):
        """获取所有子女（包括作为父亲和母亲的子女）"""
        children = set()
        if self.gender == 'M':
            children.update(self.children_as_father.all())
        else:
            children.update(self.children_as_mother.all())
        # 合并并排序
        return sorted(children, key=lambda x: (x.order, x.id))
    
    def get_family_members(self):
        """获取所有家庭成员"""
        family = {
            'parents': [],
            'spouses': [],
            'children': [],
            'siblings': []
        }
        
        # 父母
        if self.father:
            family['parents'].append(self.father)
        if self.mother:
            family['parents'].append(self.mother)
        
        # 配偶
        family['spouses'] = list(self.spouses.all())
        
        # 子女
        family['children'] = self.get_all_children()
        
        # 兄弟姐妹
        family['siblings'] = list(self.get_siblings())
        
        return family
    
    def get_generation_depth(self):
        """获取辈份深度"""
        if hasattr(self, 'generation'):
            return self.generation.number
        return 0
    
    def get_ancestors_chain(self):
        """获取祖先链"""
        ancestors = []
        current = self
        while current.father:
            ancestors.append(current.father)
            current = current.father
        return reversed(ancestors)
    
    def has_avatar(self):
        """是否有头像"""
        return bool(self.avatar)
    has_avatar.short_description = '有头像'
    has_avatar.boolean = True


class SpouseRelation(models.Model):
    """配偶关系"""
    # 关系类型
    RELATION_TYPE_CHOICES = [
        ('marriage', '婚姻'),
        ('concubine', '妾室'),
        ('adopted', '继配'),
    ]
    
    husband = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='husband_relations',
        verbose_name='丈夫',
        limit_choices_to={'gender': 'M'}
    )
    wife = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='wife_relations',
        verbose_name='妻子',
        limit_choices_to={'gender': 'F'}
    )
    
    # 关系信息
    relation_type = models.CharField(
        max_length=20,
        choices=RELATION_TYPE_CHOICES,
        default='marriage',
        verbose_name='关系类型'
    )
    
    # 配偶来源信息（用于外族配偶）
    source_info = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='配偶来源信息（如：某村某氏）'
    )
    
    # 排序
    order = models.IntegerField(default=1, verbose_name='排序（第几任）')
    
    class Meta:
        verbose_name = '配偶关系'
        verbose_name_plural = '配偶关系'
        unique_together = ['husband', 'wife']
        ordering = ['husband', 'order']
    
    def __str__(self):
        return f"{self.husband.name} - {self.wife.name}"


class GenealogyRecord(models.Model):
    """族谱记录（原始资料）"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    source = models.CharField(max_length=300, blank=True, verbose_name='来源')
    page_number = models.CharField(max_length=50, blank=True, verbose_name='页码')
    related_persons = models.ManyToManyField(
        Person,
        blank=True,
        related_name='records',
        verbose_name='相关人物'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '族谱记录'
        verbose_name_plural = '族谱记录'
    
    def __str__(self):
        return self.title


class PersonImage(models.Model):
    """人物图片/照片"""
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='人物'
    )
    image = models.ImageField(
        upload_to='person_images/',
        verbose_name='图片'
    )
    title = models.CharField(max_length=100, blank=True, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        verbose_name = '人物图片'
        verbose_name_plural = '人物图片'
    
    def __str__(self):
        return f"{self.person.name}的图片: {self.title or '未命名'}"


class PersonVideo(models.Model):
    """人物视频"""
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name='人物'
    )
    video = models.FileField(
        upload_to='person_videos/',
        validators=[FileExtensionValidator(['mp4', 'avi', 'mov', 'wmv', 'flv'])],
        verbose_name='视频'
    )
    title = models.CharField(max_length=100, blank=True, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        verbose_name = '人物视频'
        verbose_name_plural = '人物视频'
    
    def __str__(self):
        return f"{self.person.name}的视频: {self.title or '未命名'}"


from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    address = models.CharField(max_length=300, blank=True, verbose_name='地址')
    related_person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_users',
        verbose_name='关联族谱人物'
    )
    bio = models.TextField(blank=True, verbose_name='个人简介')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """当创建用户时自动创建UserProfile"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Person)
def update_user_profile_relation(sender, instance, **kwargs):
    """当更新人物时同步更新UserProfile的关联"""
    if instance.related_user:
        # 更新UserProfile的related_person
        try:
            profile = instance.related_user.profile
            if profile.related_person != instance:
                profile.related_person = instance
                profile.save()
        except UserProfile.DoesNotExist:
            # 如果UserProfile不存在，创建它
            UserProfile.objects.create(
                user=instance.related_user,
                related_person=instance
            )
