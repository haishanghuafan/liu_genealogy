---
name: genealogy-testing-skill
version: 1.0.0
license: MIT
author: Genealogy Team
description: 族谱管理系统测试技能，涵盖Django后端测试和家族关系验证的最佳实践
---

# 族谱管理系统测试技能

## 概述

本技能提供族谱管理系统（Django 5.2）的完整测试指南，包括单元测试、集成测试的最佳实践，重点关注家族关系管理、世代计算和权限控制。

## 使用场景

- 编写后端API测试
- 编写家族关系测试
- 编写数据导入导出测试
- 设置测试基础设施
- 调试测试失败
- 验证家族树结构

---

## 一、测试工具选择

### 1.1 工具对比

| 场景 | 推荐工具 | 说明 |
|------|----------|------|
| API功能测试 | agent-browser / curl | 快速验证接口 |
| 页面元素检查 | agent-browser | 轻量级页面验证 |
| 家族关系测试 | pytest | 家族关系验证 |
| 数据导入测试 | pytest | Excel导入测试 |
| 家族树测试 | pytest | 家族树结构测试 |

### 1.2 agent-browser 使用示例

```python
# 快速验证页面元素
navigate("http://localhost:8000/genealogy/")
assert_element("[data-testid='family-tree']")
assert_element("[data-testid='person-list']")

# 添加家族成员测试
click("[data-testid='add-person-btn']")
fill("[data-testid='person-name']", "测试人员")
select("[data-testid='gender-select']", "male")
select("[data-testid='generation-select']", "第10代")
click("[data-testid='save-btn']")
assert_text(".success-message", "保存成功")

# API测试
curl -X POST "http://localhost:8000/api/genealogy/persons/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "测试人员",
    "gender": "male",
    "generation_id": "gen-001",
    "father_id": "person-001"
  }'
```

---

## 二、后端测试 (Django 5.2)

### 2.1 测试文件结构

```
genealogy/tests/
├── __init__.py
├── test_models.py              # 模型测试
├── test_services.py            # 服务层测试
├── test_views.py               # 视图测试
├── test_integration.py         # 集成测试
├── test_family_relations.py    # 家族关系测试
├── test_import_export.py       # 导入导出测试
└── test_permissions.py         # 权限测试
```

### 2.2 家族关系测试

```python
# genealogy/tests/test_family_relations.py
from django.test import TestCase
from genealogy.models import Person, Generation, SpouseRelation


class FamilyRelationTest(TestCase):
    """家族关系测试"""

    def setUp(self):
        self.generation_10 = Generation.objects.create(
            name='第10代',
            level=10
        )
        self.generation_11 = Generation.objects.create(
            name='第11代',
            level=11
        )

    def test_father_son_relation(self):
        """测试父子关系"""
        father = Person.objects.create(
            name='父亲',
            gender='male',
            generation=self.generation_10
        )

        son = Person.objects.create(
            name='儿子',
            gender='male',
            generation=self.generation_11,
            father=father
        )

        # 验证父子关系
        self.assertEqual(son.father, father)
        self.assertIn(son, father.children.all())
        self.assertEqual(son.generation.level, father.generation.level + 1)

    def test_spouse_relation(self):
        """测试配偶关系"""
        husband = Person.objects.create(
            name='丈夫',
            gender='male',
            generation=self.generation_10
        )

        wife = Person.objects.create(
            name='妻子',
            gender='female',
            generation=self.generation_10
        )

        # 创建配偶关系
        SpouseRelation.objects.create(
            husband=husband,
            wife=wife,
            relation_type='married'
        )

        # 验证配偶关系
        self.assertEqual(husband.wives.first(), wife)
        self.assertEqual(wife.husband, husband)

    def test_siblings_relation(self):
        """测试兄弟姐妹关系"""
        father = Person.objects.create(
            name='父亲',
            gender='male',
            generation=self.generation_10
        )

        son1 = Person.objects.create(
            name='大儿子',
            gender='male',
            generation=self.generation_11,
            father=father
        )

        son2 = Person.objects.create(
            name='小儿子',
            gender='male',
            generation=self.generation_11,
            father=father
        )

        # 验证兄弟关系
        self.assertIn(son2, son1.get_siblings())
        self.assertIn(son1, son2.get_siblings())
        self.assertEqual(son1.father, son2.father)

    def test_circular_relation_prevented(self):
        """测试防止循环关系"""
        person1 = Person.objects.create(
            name='人员1',
            gender='male',
            generation=self.generation_10
        )

        person2 = Person.objects.create(
            name='人员2',
            gender='male',
            generation=self.generation_11,
            father=person1
        )

        # 尝试将自己设为祖先（应该失败）
        with self.assertRaises(ValueError):
            person1.father = person2
            person1.save()
```

### 2.3 家族树服务测试

```python
# genealogy/tests/test_services.py
from django.test import TestCase
from genealogy.services.tree_service import TreeService
from genealogy.models import Person, Generation


class TreeServiceTest(TestCase):
    """家族树服务测试"""

    def setUp(self):
        self.service = TreeService()
        self._create_family_tree()

    def _create_family_tree(self):
        """创建测试家族树"""
        self.gen_1 = Generation.objects.create(name='第1代', level=1)
        self.gen_2 = Generation.objects.create(name='第2代', level=2)
        self.gen_3 = Generation.objects.create(name='第3代', level=3)

        # 第一代
        self.grandfather = Person.objects.create(
            name='祖父',
            gender='male',
            generation=self.gen_1
        )

        # 第二代
        self.father = Person.objects.create(
            name='父亲',
            gender='male',
            generation=self.gen_2,
            father=self.grandfather
        )
        self.uncle = Person.objects.create(
            name='叔叔',
            gender='male',
            generation=self.gen_2,
            father=self.grandfather
        )

        # 第三代
        self.son = Person.objects.create(
            name='儿子',
            gender='male',
            generation=self.gen_3,
            father=self.father
        )

    def test_get_ancestors(self):
        """测试获取祖先"""
        ancestors = self.service.get_ancestors(self.son)

        self.assertEqual(len(ancestors), 2)
        self.assertEqual(ancestors[0], self.father)
        self.assertEqual(ancestors[1], self.grandfather)

    def test_get_descendants(self):
        """测试获取后代"""
        descendants = self.service.get_descendants(self.grandfather)

        self.assertEqual(len(descendants), 3)
        self.assertIn(self.father, descendants)
        self.assertIn(self.uncle, descendants)
        self.assertIn(self.son, descendants)

    def test_get_family_tree_data(self):
        """测试获取家族树数据"""
        tree_data = self.service.get_family_tree_data(self.grandfather)

        self.assertEqual(tree_data['name'], '祖父')
        self.assertEqual(len(tree_data['children']), 2)

        # 找到父亲节点
        father_node = next(
            (child for child in tree_data['children'] if child['name'] == '父亲'),
            None
        )
        self.assertIsNotNone(father_node)
        self.assertEqual(len(father_node['children']), 1)
        self.assertEqual(father_node['children'][0]['name'], '儿子')

    def test_calculate_generation_level(self):
        """测试计算世代层级"""
        level = self.service.calculate_generation_level(self.son)
        self.assertEqual(level, 3)
```

### 2.4 数据导入导出测试

```python
# genealogy/tests/test_import_export.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import io

from genealogy.services.import_service import ImportService
from genealogy.services.export_service import ExportService
from genealogy.models import Person, Generation


class ImportExportTest(TestCase):
    """导入导出测试"""

    def setUp(self):
        self.import_service = ImportService()
        self.export_service = ExportService()

    def test_import_from_excel(self):
        """测试从Excel导入"""
        # 创建测试Excel文件
        import pandas as pd

        df = pd.DataFrame({
            '姓名': ['测试人员1', '测试人员2'],
            '性别': ['男', '女'],
            '世代': ['第10代', '第10代'],
            '父亲姓名': ['', ''],
            '出生日期': ['1990-01-01', '1992-02-02']
        })

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # 导入数据
        result = self.import_service.import_from_excel(excel_buffer)

        self.assertEqual(result['imported_count'], 2)
        self.assertEqual(Person.objects.count(), 2)

        person1 = Person.objects.get(name='测试人员1')
        self.assertEqual(person1.gender, 'male')

    def test_export_to_excel(self):
        """测试导出到Excel"""
        # 创建测试数据
        gen = Generation.objects.create(name='第10代', level=10)
        Person.objects.create(name='人员1', gender='male', generation=gen)
        Person.objects.create(name='人员2', gender='female', generation=gen)

        # 导出数据
        excel_file = self.export_service.export_to_excel()

        # 验证导出文件
        import pandas as pd
        df = pd.read_excel(excel_file)

        self.assertEqual(len(df), 2)
        self.assertIn('姓名', df.columns)
        self.assertIn('性别', df.columns)
```

### 2.5 权限测试

```python
# genealogy/tests/test_permissions.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from genealogy.models import Person, Generation

User = get_user_model()


class PermissionTest(TestCase):
    """权限测试"""

    def setUp(self):
        self.client = Client()
        self.gen = Generation.objects.create(name='第10代', level=10)
        self.person = Person.objects.create(name='测试人员', gender='male', generation=self.gen)

        # 创建普通用户
        self.user = User.objects.create_user(
            username='normal_user',
            password='testpass123'
        )

        # 创建管理员
        self.admin = User.objects.create_user(
            username='admin_user',
            password='testpass123',
            is_staff=True
        )

    def test_normal_user_can_view_person(self):
        """测试普通用户可以查看人员"""
        self.client.force_login(self.user)
        response = self.client.get(f'/api/genealogy/persons/{self.person.id}/')
        self.assertEqual(response.status_code, 200)

    def test_normal_user_cannot_delete_person(self):
        """测试普通用户不能删除人员"""
        self.client.force_login(self.user)
        response = self.client.delete(f'/api/genealogy/persons/{self.person.id}/')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_person(self):
        """测试管理员可以删除人员"""
        self.client.force_login(self.admin)
        response = self.client.delete(f'/api/genealogy/persons/{self.person.id}/')
        self.assertEqual(response.status_code, 204)
```

### 2.6 数据工厂

```python
# genealogy/tests/factories.py
import uuid
from faker import Faker

fake = Faker('zh_CN')


class TestDataFactory:
    """测试数据工厂"""

    @staticmethod
    def create_generation(level=None, **kwargs):
        """创建世代"""
        from genealogy.models import Generation

        if level is None:
            level = fake.random_int(1, 20)

        defaults = {
            'name': f'第{level}代',
            'level': level
        }
        defaults.update(kwargs)
        return Generation.objects.create(**defaults)

    @staticmethod
    def create_person(generation=None, father=None, **kwargs):
        """创建人员"""
        from genealogy.models import Person

        if generation is None:
            generation = TestDataFactory.create_generation()

        defaults = {
            'name': fake.name(),
            'gender': fake.random_element(['male', 'female']),
            'generation': generation,
            'father': father
        }
        defaults.update(kwargs)
        return Person.objects.create(**defaults)

    @staticmethod
    def create_user(**kwargs):
        """创建用户"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        defaults = {
            'username': f'user_{uuid.uuid4().hex[:8]}',
            'email': fake.email(),
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
```

---

## 三、调试技巧

### 3.1 后端调试

```python
import logging

logger = logging.getLogger(__name__)

def test_with_debug(self):
    logger.debug(f"测试数据: {self.data}")

    try:
        result = self.service.process(self.data)
        logger.debug(f"处理结果: {result}")
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise
```

---

## 四、测试运行命令

```bash
# Django测试
python manage.py test                    # 运行所有测试
python manage.py test genealogy.tests    # 运行族谱模块测试
python manage.py test --verbosity=2      # 详细输出

# pytest
pytest                                   # 运行所有测试
pytest genealogy/tests/                  # 运行族谱模块测试
pytest -xvs                              # 详细输出，失败即停
pytest --cov=genealogy                   # 生成覆盖率报告
```
