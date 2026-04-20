---
alwaysApply: false
description: 运行各种测试时生效
---
# 族谱管理系统测试规则

## 一、测试工具选择
**原则**: 优先使用agent-browser，如果没有agent-browser，再使用Playwright默认无头模式。

| 场景 | 推荐工具 | 说明 |
|------|----------|------|
| API功能测试 | agent-browser / curl | 快速验证接口 |
| 页面元素检查 | agent-browser | 轻量级页面验证 |
| 表单提交测试 | agent-browser | 快速表单验证 |
| 复杂业务流程 | Playwright (headless) | 完整E2E测试 |
| 族谱关系测试 | pytest | 家族关系验证 |


## 二、测试文件管理

1. **禁止多文件测试同一流程** - 一个业务流程一个测试文件
2. **命名规范**:
   - 单元测试: `test_{module}.py`
   - 集成测试: `test_{flow}_integration.py`
   - E2E测试: `{flow}.spec.ts`
3. **位置**: `tests/` 或模块内 `__tests__/` 目录

## 三、测试执行原则

1. **先解决问题，再写报告** - 禁止问题未修复就生成总结文档
2. **失败优先修复** - 禁止用新测试文件绕过失败
3. **必须有断言** - 禁止无断言的"通过"测试
4. **数据独立** - 每个测试用例数据独立，禁止测试间依赖

## 四、测试断言规范

```python
# ❌ 禁止 - 只验证状态码
def test_create_person(self):
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, 201)

# ✅ 正确 - 验证数据内容
def test_create_person(self):
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, 201)
    result = response.json()
    self.assertIn('id', result['data'])
    self.assertEqual(result['data']['name'], '测试人员')
    self.assertEqual(result['data']['gender'], 'male')
```

## 五、数据验证要求

- **前置验证**: 测试前验证基础数据存在（家族分支、世代）
- **字段级断言**: 每个响应字段必须验证，不仅是状态码
- **端到端一致性**: 创建→查询→详情，数据必须一致
- **关系完整性**: 父子关系、配偶关系必须正确

## 六、族谱系统特殊测试要求

1. **家族关系** - 父子关系、配偶关系、兄弟姐妹关系
2. **世代管理** - 世代计算、字辈管理
3. **权限控制** - 普通成员vs管理员权限
4. **数据导入导出** - Excel导入导出功能
5. **家族树展示** - 家族树数据结构正确性

## 七、E2E测试规范

1. **选择器精确** - 用 `locator('button:has-text("添加成员")')` 而非 `locator('button')`
2. **智能等待** - 用 `waitForResponse` 而非固定 `sleep`
3. **数据预置** - 测试前确保基础数据已存在
4. **Playwright默认无头** - `headless: true`

## 八、禁止事项

- ❌ 禁止创建多个测试文件测试同一业务流程
- ❌ 禁止问题未解决就创建总结文档
- ❌ 禁止测试中出现未验证的假设
- ❌ 禁止测试间共享状态
- ❌ 禁止非必要使用Playwright（优先agent-browser）
- ❌ 禁止Playwright非无头模式运行（除非调试）
- ❌ 禁止只验证状态码不验证数据内容
- ❌ 禁止跳过失败的测试
- ❌ 禁止循环家族关系（自己成为自己的祖先）

## 九、核心原则

- **先解决问题，再写报告**
- **一个流程一个测试文件**
- **测试必须有断言**
- **优先agent-browser**
- **Playwright无头模式**
- **数据验证完整**
- **端到端一致性**
- **家族关系正确**
