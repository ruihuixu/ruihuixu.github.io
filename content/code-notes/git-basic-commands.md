---
title: "常用 Git 命令备忘"
date: 2025-12-14T10:00:00+08:00
draft: false
tags: ["Git", "DevOps"]
---

记录一些容易忘记的 Git 命令，防止下次再查文档。

### 撤销修改

* `git checkout -- <file>`: 丢弃工作区的修改
* `git reset HEAD <file>`: 暂存区的修改撤销回工作区

### 常用流程

> 永远记得在 Push 之前先 Pull！

```bash
git add .
git commit -m "update notes"
git push

