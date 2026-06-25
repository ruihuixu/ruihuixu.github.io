# 前置知识与环境搭建

## 数学基础

阅读本教程需要：

1. **概率论**：期望 $\mathbb{E}[X]$、条件概率 $P(A|B)$、KL 散度 $D_{KL}(P\|Q)$、重要性采样 $\mathbb{E}_{x\sim p}[f(x)] = \mathbb{E}_{x\sim q}[\frac{p(x)}{q(x)}f(x)]$
2. **优化**：梯度下降、Adam 优化器、学习率调度的基本概念
3. **深度学习**：PyTorch 基本操作（`nn.Module`, `forward`, `backward`, `optimizer.step`）、Transformer 架构的基本理解

## 软件环境

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/Scripts/activate   # Windows
# 或: source .venv/bin/activate  # Linux/Mac

# 升级 pip
pip install --upgrade pip

# 核心依赖
pip install torch --index-url https://download.pytorch.org/whl/cu128
pip install numpy matplotlib jupyter notebook ipywidgets
pip install gymnasium   # CartPole 环境
pip install transformers datasets accelerate   # LLM 实验
pip install trl   # DPO/GRPO 训练器

# 验证安装
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'"
python -c "import trl; print(f'TRL {trl.__version__}')"
```

## 硬件要求

本教程在此设备上开发，硬件约束如下。所有实验在此配置下可运行：

| 组件 | 配置 |
|------|------|
| GPU | Quadro P620 4GB VRAM, CUDA 12.8 |
| RAM | 16GB |
| CPU | 12 cores |

- **ch01-ch03（CartPole）**: CPU 可运行
- **ch03-ch06（DistilGPT-2 / 推荐模拟器）**: 需要 GPU
- 所有 LLM 实验使用 **DistilGPT-2（82M 参数）**，batch_size=1，gradient_accumulation_steps=4，适配 4GB VRAM

## 模型选择说明

| 模型 | 参数量 | fp32 显存 | 本教程使用 |
|------|--------|-----------|-----------|
| DistilGPT-2 | 82M | ~330MB | ch03-ch06 默认 |
| GPT-2 small | 124M | ~500MB | 可选替换 |
| GPT-2 medium | 355M | ~1.4GB | 不可用（OOM） |

训练时实际显存占用 ≈ 模型 × 2（forward+gradient）+ 优化器状态 × 2 ≈ 模型 × 4。
DistilGPT-2: 330MB × 4 ≈ 1.3GB，在 4GB 内安全。
