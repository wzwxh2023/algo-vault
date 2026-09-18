---
name: "scTFA-Benchmark"
category: ["单细胞转录组", "基因调控网络", "算法基准评测", "转录因子活性"]
target_problems:
  - "单细胞转录因子活性 (TFA) 推断算法权威选型与决策 (Algorithm Selection & Benchmarking)"
  - "基于大规模 Perturb-seq 扰动金标准的调控网络客观评价 (Perturbation Ground Truth Evaluation)"
  - "先验驱动 (Prior) vs 从头构建 (De novo) vs 整合式 (Integrated) 网络范式对比"
data_modalities: ["scRNA-seq", "Perturb-seq"]
inputs:
  format: "Scanpy AnnData / Seurat RDS / 基因表达矩阵"
  expression_scale: "Log-normalized counts (decoupleR/metaTF) 或 Raw counts (pySCENIC/GENIE3)"
  feature_identifier: "Official Gene Symbol (如 TP53, MYC, SOX2)"
  required_metadata: "无强制要求 (可提供 celltype, treatment 用于分组统计)"
outputs:
  primary: "细胞/亚群 × 转录因子活性得分矩阵 (TFA Score Matrix)"
  confidence_metrics: "Regulon 在真实 DEG 中的富集度统计量, 扰动预测召回率 (Perturbation Recovery Rate)"
dependencies: ["decoupler", "scanpy", "pyscenic", "metaTF", "r-viper"]
hardware_requirements: "Prior 驱动类 (如 decoupleR) 仅需单机 CPU (秒级)；De novo 驱动类 (如 pySCENIC) 推荐多核 CPU / GPU 加速"
paper:
  title: "Benchmarking methods for inferring single-cell transcription factor activity using large-scale perturbation sequencing data"
  journal: "Briefings in Bioinformatics, 2026"
  doi: "10.1093/bib/bbag513"
  pmid: "42752548"
repo_url: "https://doi.org/10.1093/bib/bbag513"
added_date: "2026-09-18"
---

# scTFA-Benchmark：基于大规模扰动测序的单细胞转录因子活性推断基准与选型指南

## 1. 核心定位与解决痛点

- **背景痛点**：
  1. **mRNA 丰度 ≠ 调控活性**：转录因子（TF）受翻译后修饰（磷酸化、泛素化）、核转位阻滞及辅因子依赖影响，其自身 mRNA 表达水平与实际转录活性常发生脱节（低表达 TF 可能极具功能活性，高表达 TF 可能处于无活性状态）。
  2. **传统评测缺乏“真实金标准”**：过去十余种 TFA 算法多在自建数据集或少量 ChIP-seq 上自证，缺乏独立、统一且基于大规模细胞实验级基因扰动（Perturb-seq）的横向客观评价。
- **评测设计与机制**：
  - 由国科大杭高院团队（Briefings in Bioinformatics, 2026）完成，利用高通量 CRISPRi/Perturb-seq 敲除转录组作为绝对 Ground Truth。
  - 系统对比了 8 种主流 TFA 推断算法，涵盖**先验驱动（Prior GRN）**、**从头构建（De novo GRN）**与**整合式（Integrated GRN）**三大技术路线。

---

## 2. 核心算法横向评测与选型矩阵（何时选谁？）

| 评估维度 | 整合式冠军：`metaTF` | 从头构建代表：`pySCENIC` | 先验驱动标杆：`decoupleR` | 扰动预测新秀：`TFActProfiler` |
| :--- | :--- | :--- | :--- | :--- |
| **算法范式** | **Integrated GRN**（先验骨架 + 数据自适应剪枝） | **De novo GRN**（共表达模块 + Motif 富集剪枝） | **Prior GRN**（纯已知先验数据库 + 统计打分） | **Signed Prior GRN**（260万带符号连续权重先验） |
| **综合精度排行** | 🥇 **第一名**（扰动细胞与 TF 预测最准） | 🥈 **第二名**（预测精度仅次于 metaTF） | 🥉 **第三名**（均衡可靠的工业级基准） | 🌟 专注免训练表达漂移模拟 |
| **TF 覆盖度** | **高**（兼具先验广度与特异性） | ⚠️ **较低**（严格过滤导致大量 TF 无法成网） | 🏆 **极高**（依赖 CollecTRI/DoRothEA） | 🏆 **极高**（全库覆盖绝大多数人类 TF） |
| **算力与运行耗时** | 中等（需网络微调，数分钟） | 较慢（多核 CPU / GPU 耗时较长） | ⚡ **极快**（秒级完成，内存占用小） | ⚡ **极快**（标准线性回归，秒级完成） |
| **对先验知识依赖** | 中度依赖（需初始 Scaffold） | 零依赖（仅需基因组 Motif 库） | 强依赖（先验质量决定上限） | 强依赖（内置训练好的先验权重） |
| **最佳适用场景** | **重点疾病亚群的高精度调控机制深入验证** | **非经典模型物种、探究未知全新 Regulon** | **全景快速探索、大规模单细胞图谱常规分析** | **模拟敲除某个 TF 后的全基因组转录漂移** |

### 🧭 推荐决策流：
1. **常规首选 / 快速筛查**：优先使用 `decoupleR`（配合 CollecTRI 数据库与 ULM 统计模型），速度最快、代码维护最好、TF 覆盖面最广。
2. **高精验证 / 关键发现**：当对重点亚群的几类特定 TF 存在疑问时，使用 `metaTF` 验证其整合网络活性。
3. **探索全新生物学机制**：当分析未收录充分先验的生物系统或希望完全由数据说话时，调用 `pySCENIC`。

---

## 3. 5 分钟极简可运行代码（Minimal Working Example）

根据 Benchmark 评测推荐，优先使用工程体验与综合表现最均衡的 `decoupleR` 进行标准化 TFA 推断：

```python
import scanpy as sc
import decoupler as dc
import pandas as pd

# 1. 准备单细胞数据 (以标准 log1p 矩阵为例)
adata = dc.ds.pbmc3k()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# 2. 获取 Benchmark 表现优异的 CollecTRI 高质量先验网络
# CollecTRI 整合了 DoRothEA 等经过人工精编的高置信度 TF-靶基因调控关系
net = dc.op.get_collectri(organism='human', split_complexes=False)

# 3. 运行 TFA 推断 (评测中推荐的一元线性模型 ULM)
# ULM 对每个细胞的每个 TF 拟合基因表达与先验权重的线性关系
dc.mt.ulm(
    data=adata,
    net=net,
    source='source',    # 转录因子名 (TF)
    target='target',    # 靶基因 (Target gene)
    weight='weight',    # 调控极性 (+1 激活 / -1 抑制)
    verbose=True
)

# 4. 提取 TFA 活性矩阵并可视化
tf_act = dc.pp.get_obsm(adata, key='score_ulm')
print("TF 活性得分矩阵 (前5个细胞 × 5个TF):")
print(tf_act.iloc[:5, :5])

# 将关键 TF 活性存入 obs 并投影至 UMAP
adata.obs['PAX5_activity'] = tf_act['PAX5']
# sc.pl.umap(adata, color=['PAX5_activity', 'celltype'])
```

---

## 4. 评测关键发现与避坑指南（Gotchas & Insights）

1. **Regulon 与真实差异表达基因（DEG）的富集度是决定性生命线**：
   - 算法表现好坏，根本上取决于其构建的 Regulon 能否真正代表 TF 敲除后的下游效应基因。千万不要盲目追求靶基因数量庞大的“虚胖网络”，靶基因信噪比越低，TFA 信号被稀释得越严重。
2. **打分算法的选择陷阱**：
   - 评测显示，**线性模型类（如 ULM / Multivariate Linear Models）** 比单纯的富集度打分（如 AUCell、GSEA、wmean）具有更强的抗共表达噪音与多效性干扰能力。在调用 `decoupleR` 时，推荐优先选用 `ulm` 或 `mlm`。
3. **低丰度 TF 的活性断言**：
   - 转录因子本身的 mRNA drop-out 率很高。如果某个 TF 在单细胞中表达量接近 0，**切勿得出“该 TF 没有活性”的结论**。应当通过其下游靶基因的协同激活状态（TFA 分数）来定量其蛋白质层面的功能状态。
4. **扰动实验类型的系统差异**：
   - CRISPRi（转录抑制）导致的下游响应往往较纯粹；而永久敲除（Knockout）可能激活细胞的代偿机制（Genetic Compensation）。在验证 TFA 推断结果时，需结合实验扰动类型客观看待残余活性。
