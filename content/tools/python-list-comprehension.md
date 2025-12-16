---
title: "Python 列表推导式技巧"
date: 2025-12-15T20:00:00+08:00
draft: false
tags: ["Python", "Efficiency"]
---

这是我的第一篇代码笔记。列表推导式（List Comprehension）是 Python 中非常优雅的语法。

### 示例代码

```python
# 传统写法
squares = []
for x in range(10):
    squares.append(x**2)

# 列表推导式写法
squares = [x**2 for x in range(10)]