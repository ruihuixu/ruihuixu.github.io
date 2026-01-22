---
title: "LeetCode 26 / 27 / 283：数组双指针的原地修改——快慢指针的统一模板"
date: 2026-01-24T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Array"
  - "Two Pointers"
  - "Fast-Slow Pointers"
  - "In-Place"
  - "Java"
categories:
  - "LeetCode"
description: "数组原地修改的本质是快慢指针维护有效边界。本文建立统一模板：27 移除元素是基础，26 去重是有序优化，283 移动零是稳定交换，三题一个模式通吃。"
---

> 题目链接：
>
> - [27. 移除元素](https://leetcode.cn/problems/remove-element/)
> - [26. 删除有序数组中的重复项](https://leetcode.cn/problems/remove-duplicates-from-sorted-array/)
> - [283. 移动零](https://leetcode.cn/problems/move-zeroes/)
>
> 难度：简单 / 简单 / 简单 ｜ 标签：数组、双指针、原地修改

## 核心心智：快慢指针 = 维护有效边界的"压缩机"

数组的原地修改问题有一个共同特征：**不能使用额外数组，必须在 O(1) 空间内完成**。

如果允许额外空间，我们可以创建新数组，遍历一遍筛选元素。但原地修改要求我们"边扫描边压缩"，这就是**快慢指针**的用武之地。

这三道题构成完整的抽象升级路径：

- **27（基础模板）**：移除指定值，建立"快扫描、慢写入"的基础模式
- **26（有序优化）**：利用有序性去重，相邻比较即可判断
- **283（稳定交换）**：移动零到末尾，需要保持非零元素相对顺序

掌握这套统一模板后，你会发现所有数组原地修改题都是同一个"快慢指针"的不同应用。

---

## 一、基础模板：移除指定元素（LeetCode 27）

### 题目描述

给你一个数组 `nums` 和一个值 `val`，你需要**原地**移除所有数值等于 `val` 的元素，并返回移除后数组的新长度。

要求：
- 不要使用额外的数组空间
- 必须仅使用 O(1) 额外空间并**原地**修改输入数组
- 元素的顺序可以改变
- 不需要考虑数组中超出新长度后面的元素

### 核心思路：快慢指针的基础模式

这是快慢指针最纯粹的形态：

- `slow`：指向"下一个应该写入有效元素的位置"（也可理解为"有效数组的尾指针"）
- `fast`：扫描整个数组，寻找有效元素

**核心不变量**：`[0, slow)` 区间内的元素都是有效的（不等于 `val`）

**物理类比**：想象一个压缩机，`fast` 是输送带扫描器，`slow` 是压缩后的输出口。只有合格的元素才能通过 `slow` 写入。

### 代码实现

```java
public int removeElement(int[] nums, int val) {
    int slow = 0;
    
    for (int fast = 0; fast < nums.length; fast++) {
        // 只有不等于 val 的元素才写入
        if (nums[fast] != val) {
            nums[slow] = nums[fast];
            slow++;
        }
    }
    
    return slow; // slow 即为新数组长度
}
```

### 图解（以 nums = [3,2,2,3], val = 3 为例）

```text
初始：[3, 2, 2, 3]
      slow
      fast

fast=0, nums[0]=3 (等于val，跳过)：
      [3, 2, 2, 3]
      slow
          fast

fast=1, nums[1]=2 (不等于val，写入)：
      [2, 2, 2, 3]
          slow
             fast

fast=2, nums[2]=2 (不等于val，写入)：
      [2, 2, 2, 3]
             slow
                fast

fast=3, nums[3]=3 (等于val，跳过)：
      [2, 2, 2, 3]
             slow
                   fast (结束)

最终：[2, 2, ?, ?]  返回 slow = 2
      ↑______↑
      有效区间
```

### 关键点

- **为什么 slow 不需要判断？** 因为只有 `nums[fast] != val` 时才写入，保证了 `[0, slow)` 的有效性
- **为什么可以直接覆盖？** 因为 `slow <= fast` 始终成立，不会丢失未扫描的元素
- **返回值是什么？** `slow` 就是新数组的长度，也是下一个待写入位置的索引

---

## 二、有序优化：删除有序数组中的重复项（LeetCode 26）

### 题目描述

给你一个**非严格递增**排列的数组 `nums`，请你**原地**删除重复出现的元素，使每个元素只出现一次，并返回删除后数组的新长度 `k`。

要求：
- `nums` 的前 `k` 个元素应包含去重后的唯一元素（相对顺序保持一致）
- `k` 之后的元素可以忽略

### 核心思路：利用有序性的相邻比较

这题是 27 题的变种，但有一个关键优化：**数组有序，重复元素一定相邻**。

因此我们不需要判断 `nums[fast]` 是否等于某个固定值，而是判断它是否等于 `nums[slow]`（已写入的最后一个元素）。

**核心不变量**：`[0, slow]` 区间内的元素都是唯一的（去重后的结果）

### 代码实现

```java
public int removeDuplicates(int[] nums) {
    if (nums.length == 0) return 0;
    
    int slow = 0; // slow 指向"已放好唯一元素"的最后一个位置
    
    for (int fast = 1; fast < nums.length; fast++) {
        // 只有遇到新值时才写入
        if (nums[fast] != nums[slow]) {
            slow++;
            nums[slow] = nums[fast];
        }
    }
    
    return slow + 1; // 长度 = 索引 + 1
}
```

### 图解（以 nums = [1,1,2,2,3] 为例）

```text
初始：[1, 1, 2, 2, 3]
      slow
         fast

fast=1, nums[1]=1 (等于nums[slow]=1，跳过)：
      [1, 1, 2, 2, 3]
      slow
            fast

fast=2, nums[2]=2 (不等于nums[slow]=1，写入)：
      [1, 2, 2, 2, 3]
         slow
               fast

fast=3, nums[3]=2 (等于nums[slow]=2，跳过)：
      [1, 2, 2, 2, 3]
         slow
                  fast

fast=4, nums[4]=3 (不等于nums[slow]=2，写入)：
      [1, 2, 3, 2, 3]
            slow
                     fast (结束)

最终：[1, 2, 3, ?, ?]  返回 slow + 1 = 3
      ↑________↑
      有效区间
```

### 关键点

- **为什么 slow 从 0 开始？** 第一个元素一定保留，`slow` 指向它
- **为什么 fast 从 1 开始？** 第一个元素已经在 `slow` 位置，从第二个开始比较
- **为什么返回 slow + 1？** `slow` 是索引，长度需要 +1
- **与 27 题的区别？** 27 题判断 `nums[fast] != val`，26 题判断 `nums[fast] != nums[slow]`

---

## 三、稳定交换：移动零（LeetCode 283）

### 题目描述

给定一个数组 `nums`，请你编写一个函数，将所有 `0` 移动到数组末尾，同时保持非零元素的相对顺序。

要求：
- 必须**原地**操作，不能拷贝数组
- 尽量减少操作次数

### 核心思路：快慢指针 + 稳定交换

这题是 27 题的变种，但有一个额外要求：**保持非零元素的相对顺序**。

如果直接用 27 题的覆盖写法，会破坏原有顺序。因此我们需要用**交换**代替覆盖。

**核心不变量**：`[0, slow)` 区间内的元素都是非零的，且保持原有顺序

**物理类比**：想象一个队列，非零元素依次排队到前面，零元素自然被挤到后面。

### 代码实现（方法一：交换法）

```java
public void moveZeroes(int[] nums) {
    int slow = 0; // slow 指向"下一个非零元素应该放的位置"

    for (int fast = 0; fast < nums.length; fast++) {
        if (nums[fast] != 0) {
            // 只有当 slow != fast 时才需要交换
            if (slow != fast) {
                int temp = nums[slow];
                nums[slow] = nums[fast];
                nums[fast] = temp;
            }
            slow++;
        }
    }
}
```

### 代码实现（方法二：覆盖 + 填零）

```java
public void moveZeroes(int[] nums) {
    int slow = 0;

    // 第一步：把所有非零元素前移
    for (int fast = 0; fast < nums.length; fast++) {
        if (nums[fast] != 0) {
            nums[slow] = nums[fast];
            slow++;
        }
    }

    // 第二步：把 slow 后面的位置全部填 0
    for (int i = slow; i < nums.length; i++) {
        nums[i] = 0;
    }
}
```

### 图解（以 nums = [0,1,0,3,12] 为例）

**方法一（交换法）**：

```text
初始：[0, 1, 0, 3, 12]
      slow
      fast

fast=0, nums[0]=0 (跳过)：
      [0, 1, 0, 3, 12]
      slow
         fast

fast=1, nums[1]=1 (交换)：
      [1, 0, 0, 3, 12]
         slow
            fast

fast=2, nums[2]=0 (跳过)：
      [1, 0, 0, 3, 12]
         slow
               fast

fast=3, nums[3]=3 (交换)：
      [1, 3, 0, 0, 12]
            slow
                  fast

fast=4, nums[4]=12 (交换)：
      [1, 3, 12, 0, 0]
               slow
                     fast (结束)

最终：[1, 3, 12, 0, 0]
```

**方法二（覆盖 + 填零）**：

```text
第一步：前移非零元素
      [1, 3, 12, 3, 12]  slow = 3

第二步：填零
      [1, 3, 12, 0, 0]
```

### 关键点

- **为什么需要 `if (slow != fast)`？** 避免自己和自己交换，减少无效操作
- **两种方法的区别？**
  - 方法一：一次遍历，原地交换，更优雅
  - 方法二：两次遍历，先覆盖再填零，更直观
- **与 27 题的区别？** 27 题可以直接覆盖，283 题需要交换保持顺序

---

## 四、统一对比与抽象升级

这三道题虽然场景不同，但本质都是**快慢指针维护有效边界**。

| 特性 | 27. 移除元素 | 26. 删除重复项 | 283. 移动零 |
|------|-------------|---------------|------------|
| **核心操作** | 过滤指定值 | 去重（有序） | 移动零到末尾 |
| **判断条件** | `nums[fast] != val` | `nums[fast] != nums[slow]` | `nums[fast] != 0` |
| **写入方式** | 覆盖 | 覆盖 | 交换（保持顺序） |
| **slow 初始值** | 0 | 0 | 0 |
| **fast 初始值** | 0 | 1（第一个元素已在 slow） | 0 |
| **返回值** | slow（新长度） | slow + 1（新长度） | 无（void） |
| **核心不变量** | `[0, slow)` 不含 val | `[0, slow]` 无重复 | `[0, slow)` 无零 |
| **时间复杂度** | $O(n)$ | $O(n)$ | $O(n)$ |
| **空间复杂度** | $O(1)$ | $O(1)$ | $O(1)$ |

### 统一模板的本质

无论是移除元素、去重还是移动零，核心都是：

1. **定义不变量**：`slow` 维护的区间内元素满足什么条件
2. **快指针扫描**：`fast` 遍历整个数组，寻找符合条件的元素
3. **慢指针写入**：只有符合条件的元素才通过 `slow` 写入有效区间
4. **保持不变量**：每次写入后 `slow++`，确保不变量始终成立

---

## 五、易错点清单（Bug-Free Guide）

### 1. slow 和 fast 的初始值混淆（26 题）

```java
// ❌ 错误：26 题 slow 和 fast 都从 0 开始
int slow = 0;
for (int fast = 0; fast < nums.length; fast++) {
    if (nums[fast] != nums[slow]) {
        slow++;
        nums[slow] = nums[fast];
    }
}
// 问题：第一个元素会和自己比较，导致逻辑错误

// ✅ 正确：slow 从 0 开始，fast 从 1 开始
int slow = 0;
for (int fast = 1; fast < nums.length; fast++) {
    if (nums[fast] != nums[slow]) {
        slow++;
        nums[slow] = nums[fast];
    }
}
```

### 2. 返回值错误（26 题）

```java
// ❌ 错误：返回 slow
return slow;

// ✅ 正确：返回 slow + 1（长度 = 索引 + 1）
return slow + 1;
```

### 3. 忘记判断 slow != fast（283 题）

```java
// ❌ 错误：无条件交换，导致自己和自己交换
if (nums[fast] != 0) {
    swap(nums, slow, fast);
    slow++;
}

// ✅ 正确：只有 slow != fast 时才交换
if (nums[fast] != 0) {
    if (slow != fast) {
        swap(nums, slow, fast);
    }
    slow++;
}
```

### 4. 边界条件未处理（26 题）

```java
// ❌ 错误：空数组会导致数组越界
int slow = 0;
for (int fast = 1; fast < nums.length; fast++) {
    // ...
}

// ✅ 正确：提前判空
if (nums.length == 0) return 0;
int slow = 0;
for (int fast = 1; fast < nums.length; fast++) {
    // ...
}
```

### 5. 不变量理解错误

```java
// ❌ 错误理解：认为 [0, slow] 是有效区间（27 题）
// 导致 slow 初始化为 -1 或其他错误值

// ✅ 正确理解：
// - 27/283 题：[0, slow) 是有效区间（左闭右开）
// - 26 题：[0, slow] 是有效区间（左闭右闭）
```

---

## 六、口诀式总结：快慢指针的万能模板

```text
【数组原地修改万能模板】

1. 定义不变量
   - slow：有效区间的边界（写入位置）
   - fast：扫描指针（寻找有效元素）
   - 不变量：[0, slow) 或 [0, slow] 满足题目要求

2. 初始化
   - 27/283 题：slow = 0, fast = 0
   - 26 题：slow = 0, fast = 1（第一个元素已确定）

3. 扫描写入
   for (int fast = ...; fast < nums.length; fast++) {
       if (符合条件) {
           写入操作（覆盖或交换）
           slow++
       }
   }

4. 返回结果
   - 27 题：return slow（新长度）
   - 26 题：return slow + 1（新长度）
   - 283 题：void（原地修改）

【三题决策树】
- 移除指定值 → 判断 nums[fast] != val
- 去重（有序）→ 判断 nums[fast] != nums[slow]
- 移动零 → 判断 nums[fast] != 0，用交换保持顺序

【核心不变量】
- 27 题：[0, slow) 不含 val
- 26 题：[0, slow] 无重复
- 283 题：[0, slow) 无零，且保持原顺序
```

---

## 总结

数组原地修改的本质是**快慢指针维护有效边界**，掌握这套统一模板后：

- **27** 是基础模板，过滤指定值
- **26** 是有序优化，利用相邻比较去重
- **283** 是稳定交换，保持非零元素顺序

记住：**定义不变量，快指针扫描，慢指针写入，保持不变量**。画图推演一遍，代码自然长出来。

### 扩展应用

这个模板还可以解决：

- **80. 删除有序数组中的重复项 II**：允许重复两次，调整判断条件为 `nums[fast] != nums[slow - 1]`
- **88. 合并两个有序数组**：双指针从后往前合并
- **75. 颜色分类**：三指针（荷兰国旗问题）

掌握快慢指针思维，数组原地修改问题迎刃而解！

