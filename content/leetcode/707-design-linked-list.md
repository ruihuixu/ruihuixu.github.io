---
title: "LeetCode 707. 设计链表：增删改查的统一模板——Dummy Head + Size 模式"
date: 2026-01-19T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Linked List"
  - "Design"
  - "Dummy Node"
  - "Java"
categories:
  - "LeetCode"
description: "链表设计的本质是用虚拟头节点统一增删逻辑，用 size 管住边界。本文提供两版实现对照，附常见易错点复盘与原子操作模板。"
---

> 题目链接：[707. 设计链表](https://leetcode.cn/problems/design-linked-list/description/)
>
> 难度：中等 ｜ 标签：链表、设计

## 题目描述

设计实现一个链表 `MyLinkedList` 类，支持以下操作：

- `get(index)`：获取链表中第 `index` 个节点的值；若索引无效，返回 `-1`。
- `addAtHead(val)`：在链表头部插入节点。
- `addAtTail(val)`：在链表尾部追加节点。
- `addAtIndex(index, val)`：在第 `index` 个节点之前插入节点。
  - 若 `index == size`：等价于尾插。
  - 若 `index > size`：不插入。
  - 若 `index < 0`：按 `index = 0` 处理（等价于头插）。
- `deleteAtIndex(index)`：删除第 `index` 个节点（仅当索引有效）。

## 核心思路：Dummy Head + size + 找前驱

这题的关键不是“会不会链表”，而是把边界条件变成统一逻辑：

1. **虚拟头节点（Dummy Head）**
   - 让 `dummyHead.next` 指向真实头节点。
   - 好处：无论头插、删头还是中间插入/删除，都能统一为“先找到前驱节点 `pred`，再改 `pred.next`”。
2. **维护 `size`**
   - 把“长度”变成 $O(1)$ 可用信息。
   - 所有越界判断都依赖 `size`，避免无意义遍历。
3. **只找前驱（predecessor）**
   - 单向链表无法回退，因此增/删都围绕“前驱节点”操作：
     - 插入：`toAdd.next = pred.next; pred.next = toAdd`
     - 删除：`pred.next = pred.next.next`

## 按操作拆解：增删改查的“原子步骤”模板（含反转延展）

很多同学卡在这题，并不是思路不懂，而是对链表操作的“指针改动顺序”不够熟。下面把每个操作拆成可以直接背诵/套用的模板。

> 约定：都有 `dummyHead` 与 `size`，并且所有定位都优先“找前驱 `pred`”。

### 1）查：`get(index)` —— 先判边界，再走固定步数

- **边界**：`index` 必须满足 `0 <= index < size`
- **移动**：从 `dummyHead` 出发走 `index + 1` 步到目标节点

```java
public int get(int index) {
    if (index < 0 || index >= size) return -1;

    ListNode cur = dummyHead;
    for (int i = 0; i <= index; i++) {
        cur = cur.next;
    }
    return cur.val;
}
```

### 2）增：`addAtIndex(index, val)` —— 找前驱，再“两连”

- **边界**：
  - `index > size`：不插入
  - `index < 0`：按 `index = 0`（等价头插）
- **定位前驱**：从 `dummyHead` 走 `index` 步到 `pred`
- **指针原子操作（插入）**：
  1. `toAdd.next = pred.next`
  2. `pred.next = toAdd`
- **维护 size**：插入成功后 `size++`

```java
public void addAtIndex(int index, int val) {
    if (index > size) return;
    if (index < 0) index = 0;

    ListNode pred = dummyHead;
    for (int i = 0; i < index; i++) {
        pred = pred.next;
    }

    ListNode toAdd = new ListNode(val);
    toAdd.next = pred.next;
    pred.next = toAdd;
    size++;
}
```

对应地：

- **头插**：`addAtIndex(0, val)`
- **尾插**：`addAtIndex(size, val)`

### 3）删：`deleteAtIndex(index)` —— 找前驱，再“一跳”

- **边界**：`0 <= index < size`
- **定位前驱**：从 `dummyHead` 走 `index` 步到 `pred`
- **指针原子操作（删除）**：`pred.next = pred.next.next`
- **维护 size**：删除成功后 `size--`

```java
public void deleteAtIndex(int index) {
    if (index < 0 || index >= size) return;

    ListNode pred = dummyHead;
    for (int i = 0; i < index; i++) {
        pred = pred.next;
    }

    pred.next = pred.next.next;
    size--;
}
```

### 4）改：更新第 `index` 个节点值（本题未要求，但属于同一套“查到节点再赋值”）

- **边界**：`0 <= index < size`
- **定位目标**：从 `dummyHead` 走 `index + 1` 步到 `cur`
- **更新**：`cur.val = newVal`

```java
public void set(int index, int newVal) {
    if (index < 0 || index >= size) return;

    ListNode cur = dummyHead;
    for (int i = 0; i <= index; i++) {
        cur = cur.next;
    }
    cur.val = newVal;
}
```

### 5）延展：反转链表（Reverse）也是同一类“指针扭转”的原子操作

反转的本质不是“交换两个元素”，而是反复把一条边 `cur -> next` 扭转成 `cur -> prev`。

- **核心原子操作（每轮 3 行）**：
  1. 先保存：`next = cur.next`（否则链表会断）
  2. 再反转：`cur.next = prev`
  3. 再前进：`prev = cur; cur = next`

```java
public ListNode reverseList(ListNode head) {
    ListNode prev = null;
    ListNode cur = head;

    while (cur != null) {
        ListNode next = cur.next; // 1) 先保留后继
        cur.next = prev;          // 2) 扭转指针
        prev = cur;               // 3) 整体前进
        cur = next;
    }
    return prev;
}
```

你会发现它和“插入/删除”的共通点是：**永远先保住还需要访问的引用，再做指针改动**。

## 易错点与注意事项（Common Pitfalls）

- **索引边界差异**
  - 查/删（`get`/`deleteAtIndex`）：有效范围是 `[0, size - 1]`。
  - 增（`addAtIndex`）：有效范围是 `[0, size]`（允许等于 `size` 追加）。
  - 口诀：“增”可以等于 `size`，“删/查”必须小于 `size`。
- **走几步的问题（从 dummy 出发）**
  - 找第 `index` 个节点：通常走 `index + 1` 步。
  - 找第 `index` 个节点的前驱：通常走 `index` 步。
- **引用 != 删除**
  - `cur = null` 只是断开变量引用，不会改变链表结构。
  - 只有改指针：`pred.next = pred.next.next` 才是“删除”。

## 我的错误复盘（My Bug Report）

### 错误一：逻辑穿透（Missing Return）

场景：`addAtIndex` 里为了处理 `index == size`，调用了 `addAtTail(val)`。

问题：调用完忘记 `return;`，导致尾插完成后又继续走“通用插入逻辑”，同一个值被插入两次。

修正：调用兄弟方法完成任务后，必须立刻 `return`。

### 错误二：size 状态未同步

场景：`deleteAtIndex` 正确改了 `next` 指针删除节点。

问题：忘记 `size--`，导致长度信息落后于真实结构，后续 `get` 可能误判合法并走到空指针。

修正：链表增删必须与 `size` 的增减保持严格一致。

## 参考实现（两种写法）

### 版本一：原始代码修复版（保留 while 风格）

说明：重点体现“特判后必须 return”与“删除后必须 size--”。并补上 `index < 0` 的处理以符合题意。

```java
class MyLinkedList {
    class ListNode {
        int val;
        ListNode next;
        ListNode(int val) { this.val = val; }
    }

    private int size;
    private ListNode dummyhead;

    public MyLinkedList() {
        this.dummyhead = new ListNode(0);
        this.size = 0;
    }

    public int get(int index) {
        if (index < 0 || index > this.size - 1) return -1;

        ListNode cur = dummyhead;
        while (index >= 0) { // 从 dummy 出发走 index+1 步
            cur = cur.next;
            index--;
        }
        return cur.val;
    }

    public void addAtHead(int val) {
        ListNode newHead = new ListNode(val);
        newHead.next = dummyhead.next;
        dummyhead.next = newHead;
        this.size++;
    }

    public void addAtTail(int val) {
        ListNode newNode = new ListNode(val);
        ListNode cur = dummyhead;
        while (cur.next != null) {
            cur = cur.next;
        }
        cur.next = newNode;
        this.size++;
    }

    public void addAtIndex(int index, int val) {
        if (index > this.size) return;
        if (index < 0) index = 0;

        if (index == this.size) {
            addAtTail(val);
            return; // ✅ 必须 return，防止逻辑穿透
        }

        ListNode cur = dummyhead;
        while (index > 0) { // 找前驱：从 dummy 走 index 步
            cur = cur.next;
            index--;
        }

        ListNode newNode = new ListNode(val);
        newNode.next = cur.next;
        cur.next = newNode;
        this.size++;
    }

    public void deleteAtIndex(int index) {
        if (index < 0 || index > this.size - 1) return;

        ListNode cur = dummyhead;
        while (index > 0) { // 找前驱
            cur = cur.next;
            index--;
        }
        cur.next = cur.next.next;
        this.size--; // ✅ 必须维护 size
    }
}
```

### 版本二：简洁优化版（推荐参考）

说明：

- DRY：`addAtHead` / `addAtTail` 直接复用 `addAtIndex`，减少重复代码与分支错误。
- `for` 循环更直观表达“移动 N 步”。

```java
class MyLinkedList {
    class ListNode {
        int val;
        ListNode next;
        ListNode(int val) { this.val = val; }
    }

    int size;
    ListNode dummyHead;

    public MyLinkedList() {
        size = 0;
        dummyHead = new ListNode(0);
    }

    public int get(int index) {
        if (index < 0 || index >= size) return -1;

        ListNode cur = dummyHead;
        for (int i = 0; i <= index; i++) {
            cur = cur.next;
        }
        return cur.val;
    }

    public void addAtHead(int val) {
        addAtIndex(0, val);
    }

    public void addAtTail(int val) {
        addAtIndex(size, val);
    }

    public void addAtIndex(int index, int val) {
        if (index > size) return;
        if (index < 0) index = 0;

        size++;

        ListNode pred = dummyHead;
        for (int i = 0; i < index; i++) {
            pred = pred.next;
        }

        ListNode toAdd = new ListNode(val);
        toAdd.next = pred.next;
        pred.next = toAdd;
    }

    public void deleteAtIndex(int index) {
        if (index < 0 || index >= size) return;

        size--;

        ListNode pred = dummyHead;
        for (int i = 0; i < index; i++) {
            pred = pred.next;
        }
        pred.next = pred.next.next;
    }
}
```

## 复杂度分析

- **时间复杂度**：单次操作最坏为 $O(N)$（需要遍历到指定位置）。
- **空间复杂度**：链表节点占用 $O(N)$；除节点外额外空间为 $O(1)$。

## 总结

- 用 `dummyHead` 统一“头部/中间”的增删逻辑。
- 用 `size` 管住所有边界判断，避免越界与无效遍历。
- 增删只改 `pred.next`，别把精力耗在特殊 case 上。