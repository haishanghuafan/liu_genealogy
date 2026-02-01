"""
刘氏乾正公族谱 - 数据模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Generation(models.Model):
    """世代"""
    number = models.IntegerField(unique=True, verbose_name='世代数')
    name = models.CharField(max_length=50, blank=True, verbose_name='世代名称')
    description = models.TextField(blank=True, verbose_name='描述')
    
    class Meta:
        verbose_name = '世代'
        verbose_name_plural = '世代'
        ordering = ['number']
    
    def __str__(self):
        return f"第{self.number}世"


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
    
    # 世代
    generation = models.ForeignKey(
        Generation,
        on_delete=models.CASCADE,
        related_name='persons',
        verbose_name='世代'
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
    
    # 配偶（多对多关系通过Spouse模型）
    spouses = models.ManyToManyField(
        'self',
        through='SpouseRelation',
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
        return self.spouses.filter(gender='F')
    
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


class SpouseRelation(models.Model):
    """配偶关系"""
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
