---
title: "哈希表笔记：从数组计数到 HashMap——Java 选型决策树"
date: 2026-01-24T10:00:00+08:00
draft: false
tags:
  - "Algorithm"
  - "Data Structure"
  - "Hash Table"
  - "Array"
  - "String"
  - "Java"
categories:
  - "LeetCode"
description: "哈希题的关键不是背 API，而是选对容器：数组计数、HashSet 去重/判存在、HashMap 存下标/计数。本文用 Java 视角给出选型表、典型题模板与易错点，并解释何时必须转向排序+双指针。"
---

> 题目链接（本文示例）：
>
> - [242. 有效的字母异位词](https://leetcode.cn/problems/valid-anagram/)
> - [383. 赎金信](https://leetcode.cn/problems/ransom-note/)
> - [349. 两个数组的交集](https://leetcode.cn/problems/intersection-of-two-arrays/)
> - [202. 快乐数](https://leetcode.cn/problems/happy-number/)
> - [1. 两数之和](https://leetcode.cn/problems/two-sum/)
> - [454. 四数相加 II](https://leetcode.cn/problems/4sum-ii/)
>
> 难度：简单为主 ｜ 标签：哈希表、数组、字符串

## 核心心智：哈希表不是一个结构，而是一类“用 Key 快速定位”的思维

刷哈希题最容易犯的错是：

- 看到“哈希”两个字就无脑上 `HashMap`。
- 忽略了更轻、更快、更简单的“数组计数”。

**正确打开方式**：先问自己三件事——

1. **Key 的范围小不小？**（例如 `a-z`、ASCII、题目给了上界）
2. **我要的是“存在性/去重”，还是“下标/次数/映射”？**
3. **题目是否要求“组合去重”？**（如果是，同一个数组里找三元组/四元组，常常要转向“排序 + 双指针”，而不是哈希）

---

## 一、Java 里常用的“哈希类工具箱”

### 选型速查表

| 需求 | 首选结构 | 为什么 |
|---|---|---|
| Key 范围小，统计频次 | `int[]` / `boolean[]` | 常数小、无装箱、速度快 |
| 判存在 / 去重（无序） | `HashSet` | $O(1)$ 平均复杂度，API 简洁 |
| 需要 Key → Value（下标/次数） | `HashMap` | 一步到位表达“映射” |
| 需要有序 | `TreeSet` / `TreeMap` | $O(\log n)$，可做范围查询 |
| 需要保留插入顺序 | `LinkedHashSet` / `LinkedHashMap` | 迭代顺序可控 |

### HashMap 背后你应该知道的两个点（够用版）

- **碰撞（Collision）**：不同 Key 算到同一个桶。
- **JDK 8+ 优化**：链表过长会树化（红黑树），避免极端退化。

对刷题来说，你只需要把 HashMap 当作“平均 $O(1)$ 的 Key 定位器”，然后把注意力放在：

- Key 设计是否正确
- 什么时候该存“下标”、什么时候该存“次数”
- 是否需要处理重复/边界

---

## 二、场景 1：数组当哈希表（最快，也最常被忽略）

### 适用条件

- Key 的取值范围**已知且不大**（如 `a-z`、`0-1000`、ASCII 128/256）

### 示例：242 有效的字母异位词

核心：`a-z` → `0-25` 映射到数组下标。

```java
class Solution {
    public boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) return false;

        int[] cnt = new int[26];

        for (int i = 0; i < s.length(); i++) {
            cnt[s.charAt(i) - 'a']++;
        }
        for (int i = 0; i < t.length(); i++) {
            cnt[t.charAt(i) - 'a']--;
        }

        for (int x : cnt) {
            if (x != 0) return false;
        }
        return true;
    }
}
```

### 示例：383 赎金信

核心：不是“相等”，而是“t 是否覆盖 s”。所以只要计数不为负即可。

```java
class Solution {
    public boolean canConstruct(String ransomNote, String magazine) {
        int[] cnt = new int[26];
        for (int i = 0; i < magazine.length(); i++) {
            cnt[magazine.charAt(i) - 'a']++;
        }
        for (int i = 0; i < ransomNote.length(); i++) {
            int idx = ransomNote.charAt(i) - 'a';
            cnt[idx]--;
            if (cnt[idx] < 0) return false; // 提前失败
        }
        return true;
    }
}
```

---

## 三、场景 2：HashSet（去重与存在性）

### 适用条件

- Key 范围很大、稀疏，数组会浪费空间
- 只关心“出现没出现过”

### 示例：349 两个数组的交集

```java
import java.util.*;

class Solution {
    public int[] intersection(int[] nums1, int[] nums2) {
        Set<Integer> set = new HashSet<>();
        for (int x : nums1) set.add(x);

        Set<Integer> ans = new HashSet<>();
        for (int x : nums2) {
            if (set.contains(x)) ans.add(x);
        }

        int[] res = new int[ans.size()];
        int idx = 0;
        for (int x : ans) res[idx++] = x;
        return res;
    }
}
```

### 示例：202 快乐数（用 Set 判“是否进入循环”）

```java
import java.util.*;

class Solution {
    public boolean isHappy(int n) {
        Set<Integer> seen = new HashSet<>();

        while (n != 1 && !seen.contains(n)) {
            seen.add(n);
            n = next(n);
        }
        return n == 1;
    }

    private int next(int x) {
        int sum = 0;
        while (x > 0) {
            int d = x % 10;
            sum += d * d;
            x /= 10;
        }
        return sum;
    }
}
```

---

## 四、场景 3：HashMap（下标/次数/映射）

### 适用条件

- 你需要的不只是“出现过没”，还需要“出现在哪里/出现几次/对应什么值”

### 示例：1 两数之和（返回下标）

```java
import java.util.*;

class Solution {
    public int[] twoSum(int[] nums, int target) {
        // key: 数值, value: 下标
        Map<Integer, Integer> map = new HashMap<>();

        for (int i = 0; i < nums.length; i++) {
            int need = target - nums[i];
            if (map.containsKey(need)) {
                return new int[] { map.get(need), i };
            }
            map.put(nums[i], i);
        }
        return new int[0];
    }
}
```

### 示例：454 四数相加 II（“分治 + 计数”）

这题的关键认知：

- 不是在同一个数组里选 4 个数，不需要考虑“组内去重”。
- 问的是“有多少个元组”，本质是**计数**。

```java
import java.util.*;

class Solution {
    public int fourSumCount(int[] nums1, int[] nums2, int[] nums3, int[] nums4) {
        Map<Integer, Integer> count = new HashMap<>();

        // 统计 A+B 的所有和出现次数
        for (int a : nums1) {
            for (int b : nums2) {
                int s = a + b;
                count.put(s, count.getOrDefault(s, 0) + 1);
            }
        }

        // 用 C+D 去匹配 -(A+B)
        int ans = 0;
        for (int c : nums3) {
            for (int d : nums4) {
                int need = -(c + d);
                ans += count.getOrDefault(need, 0);
            }
        }
        return ans;
    }
}
```

---

## 五、易混淆辨析：哈希法 vs 排序+双指针

最常见的“错题本”：为什么 2Sum 可以哈希，3Sum/4Sum（同数组、要求去重）却更适合排序+双指针？

### 一张表说清楚

| 题型特征 | 典型题 | 推荐解法 | 关键原因 |
|---|---|---|---|
| 返回下标（数组无序） | 1 两数之和 | `HashMap` | 排序会打乱下标；map 一次扫描搞定 |
| 四个独立数组，只问“次数” | 454 四数相加 II | `HashMap` 计数 | 无需组内去重，可分治到 $O(n^2)$ |
| 同一个数组选组合，且必须去重 | 15 三数之和 / 18 四数之和 | 排序 + 双指针 | 哈希去重复杂；排序让重复值连续可跳过 |

---

## 六、复杂度分析（典型）

- 数组计数：时间 $O(n)$，空间 $O(1)$（常数 26/128/256）
- HashSet/HashMap：平均时间 $O(n)$，空间 $O(n)$
- 454 四数相加 II：时间 $O(n^2)$，空间 $O(n^2)$（存 A+B 的计数）

---

## 七、易错点清单（Bug-Free Guide）

### 1）能用数组就别用 HashMap

```text
❌ 误区：字符统计题一律 HashMap<Character, Integer>
✅ 正解：如果是 a-z / ASCII，优先 int[] 计数（更快、更少 bug）
```

### 2）HashSet 只适合“存在性/去重”，不适合“下标/次数”

```text
❌ 用 Set 写 Two Sum：你拿不到下标
✅ 用 Map：value 存下标 / 次数 / 你真正关心的东西
```

### 3）循环检测要先判 seen，再推进状态

```text
快乐数/链表环：
先判断“是否见过”，再推进到 next 状态，避免漏掉首次重复。
```

---

## 八、口诀式总结：哈希题选型决策树

```text
【先问三句话】

1) Key 范围小吗？
   - 是：数组计数（int[] / boolean[]）
   - 否：继续问

2) 只要“存在/去重”吗？
   - 是：HashSet
   - 否：继续问

3) 需要“下标/次数/映射”吗？
   - 是：HashMap（key->value）

【额外警报】
- 同数组选组合且要去重（3Sum/4Sum）：优先排序 + 双指针，不要硬上哈希去重。
```

---

## 总结

哈希题写得快、写得稳，靠的不是“会不会 HashMap”，而是**选型**：

- 范围小就数组
- 去重/判存在用 Set
- 下标/次数/映射用 Map

当题目升级到“组合 + 去重”（例如 3Sum/4Sum），要果断切到“排序 + 双指针”的体系。

### 扩展应用

- [15. 三数之和](https://leetcode.cn/problems/3sum/)：同数组组合去重 → 排序+双指针
- [18. 四数之和](https://leetcode.cn/problems/4sum/)：同上，多一层枚举
- [49. 字母异位词分组](https://leetcode.cn/problems/group-anagrams/)：Key 设计（排序字符串 / 计数签名）
