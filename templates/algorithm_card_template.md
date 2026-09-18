---
name: "算法名称 (如 TFActProfiler)"
category: ["分类标签, 如 单细胞转录组, 基因调控网络"]
target_problems:
  - "解决的具体生物学/计算问题 1 (如 转录因子活性推断)"
  - "解决的具体生物学/计算问题 2 (如 基因敲除扰动预测)"
data_modalities: ["scRNA-seq", "bulk-RNA-seq", "scATAC-seq"]
inputs:
  format: "数据结构 (如 Scanpy AnnData, Seurat RDS, CSV 矩阵)"
  expression_scale: "表达量标度 (如 Raw counts, Log-normalized counts, TPM)"
  feature_identifier: "基因标识符类型 (如 Official Gene Symbol, Ensembl ID)"
  required_metadata: "必需的样本/细胞元数据 (如 celltype, batch, treatment)"
outputs:
  primary: "核心产出数据 (如 细胞 × TF 活性得分矩阵)"
  confidence_metrics: "置信度/质控指标 (如 均方误差 MSE, P-value, 残差)"
dependencies: ["包名 1", "包名 2", "Python >= 3.9"]
hardware_requirements: "GPU / CPU 内存推荐 (如 16GB RAM, 无需 GPU)"
paper:
  title: "论文标题"
  journal: "期刊名称与年份"
  doi: "10.xxxx/xxxx"
repo_url: "https://github.com/org/repo"
added_date: "YYYY-MM-DD"
---

# {算法名称}

## 1. 核心定位与解决痛点
- **背景痛点**：传统方法存在什么局限（如假阳性高、无符号、运算慢等）。
- **核心机制**：该算法的核心数理/统计学创新（如带符号网络预训练、图神经网络、扩散模型等）。

## 2. 选型对比（何时选它 vs 选竞品？）
| 对比维度 | 当前算法 ({name}) | 常见竞品 1 ({baseline1}) | 常见竞品 2 ({baseline2}) |
| :--- | :--- | :--- | :--- |
| **核心优势** | ... | ... | ... |
| **主要劣势** | ... | ... | ... |
| **最佳适用场景** | ... | ... | ... |

## 3. 5 分钟极简可运行代码（Minimal Working Example）
```python
# 最小可运行 Python 脚本
import scanpy as sc

# 1. 准备标准输入
# ...

# 2. 运行核心分析
# ...

# 3. 获取输出与质控
# ...
```

## 4. 常见陷阱与注意事项（Gotchas）
- 踩坑点 1（如大小写、必须过滤核糖体基因、网络文件路径等）
- 踩坑点 2
