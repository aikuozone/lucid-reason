# Concepts: mechanism, examples, boundaries

Scenario: `core-01`. [Run record](../evals/results/release-v1.1.4/core-01-lr-r1.json) · [Evaluation method](../docs/evaluation.md)

The following responses are copied verbatim from the actual recorded run. Scenario questions are shown below; the JSON also preserves the full neutral wrapper and explicit skill selector.

## Turn 1: user

解释 Pydantic v2 的 BaseModel：字段声明怎样变成运行时数据模型？给一个正常输入和一个非法输入的最小例子，说明类型转换、校验错误和序列化，以及它不能保证什么。

## Turn 1: actual response

**Pydantic v2 的 `BaseModel` 把字段声明变成一套运行时规则：接收数据，按规则转换和校验，成功后生成模型实例，再按需序列化。** 普通 Python 类型注解本身不会自动完成这些检查。

字段声明到实例，大致经过三个步骤：

1. **定义类时收集规则**：`BaseModel` 的类创建机制读取类型注解、默认值和 `Field(...)` 约束，形成字段信息，可通过 `model_fields` 查看。
2. **生成运行时处理逻辑**：Pydantic 将这些信息组织成内部核心模式（core schema），交给主要用 Rust 实现的 `pydantic-core`，构建校验器和序列化器。它与用于对外描述结构的 JSON Schema 有区别。
3. **输入数据时执行规则**：调用 `Model(...)` 或 `Model.model_validate(...)`，校验器处理输入；可接受的数据转换成字段值，不满足规则则抛出 `ValidationError`。

下面假设使用 **Pydantic v2 默认的非严格模式**。本地 Python 未安装 Pydantic，以下是预期行为，未在当前环境实测。

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    name: str
    age: int = Field(ge=0)  # 必填，且必须大于等于 0


# 正常输入：字符串 "18" 可以转换为整数
user = User.model_validate({"name": "小明", "age": "18"})

print(user.age, type(user.age).__name__)
# 18 int

print(user.model_dump())
# {'name': '小明', 'age': 18}

print(user.model_dump_json())
# {"name":"小明","age":18}


# 非法输入：可以转换为整数，但转换后违反 ge=0
try:
    User.model_validate({"name": "小明", "age": "-1"})
except ValidationError as exc:
    for error in exc.errors():
        print(error["loc"], error["type"], error["msg"])
# ('age',) greater_than_equal Input should be greater than or equal to 0
```

这个例子体现了几个区别：

- **类型转换**：默认模式允许部分转换，如 `"18"` → `18`；并非任意输入都能转换。若传入 `"abc"`，会产生整数解析错误。需要拒绝字符串形式的年龄时，可使用严格模式，例如 `Field(ge=0, strict=True)`。
- **校验错误**：`ValidationError` 提供结构化错误，其中 `loc` 指出字段位置，`type` 表示错误类别，`msg` 解释原因；失败时不会返回成功构造的模型。
- **序列化**：`model_dump()` 返回 Python 字典，其中某些字段仍可能是 Python 对象；`model_dump_json()` 返回 JSON 字符串。序列化负责输出表示，不会自动增加业务校验。

**它能保证的范围取决于声明了什么，以及是否经过校验入口。**

- `age >= 0` 不能证明年龄真实，也不能证明用户身份、权限或数据库记录存在；这些需要额外业务规则和外部检查。
- 默认会忽略额外输入字段；需要拒绝时，应配置 `extra="forbid"`。
- 模型默认可修改，赋值默认不重新校验，例如 `user.age = -1`；需要时配置 `validate_assignment=True`，但这也不等于所有内部可变对象的修改都会被检查。
- `model_construct()` 可以跳过校验，默认值默认也不校验；因此“拿到了一个模型实例”不能无条件等同于“其中所有数据始终有效”。
