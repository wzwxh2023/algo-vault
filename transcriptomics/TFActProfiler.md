---
name: "TFActProfiler"
category: ["单细胞转录组", "基因调控网络", "扰动生物学"]
target_problems:
  - "单细胞/Bulk 转录因子活性定量推断 (TF Activity Inference)"
  - "免训练转录组级基因敲除响应预测 (Training-free Perturbation Prediction)"
  - "推断结果不确定性与可靠性评估 (Uncertainty & Reliability Estimation)"
data_modalities: ["scRNA-seq", "bulk-RNA-seq"]
inputs:
  format: "Scanpy AnnData"
  expression_scale: "Log-normalized counts (normalize_total 1e4 + log1p)"
  feature_identifier: "Official Gene Symbol (人类大写, 如 TP53, PAX5)"
  required_metadata: "adata.obs['celltype'] 或聚类列 (用于 cluster-wise 残差评估)"
outputs:
  primary: "adata.obsm['score_ulm']: [细胞数 × 转录因子数] 活性 Z-score 矩阵"
  confidence_metrics: "adata.obs['mse']: 每个细胞的均方误差残差 (数值越小越可靠)"
dependencies: ["scanpy", "decoupler", "tfactprofiler", "pandas"]
hardware_requirements: "单机 CPU (常规笔记本或服务器均可, 无需 GPU)"
paper:
  title: "A transcription factor regulatory atlas for activity inference and perturbation prediction"
  journal: "Nucleic Acids Research, 2026"
  doi: "10.1093/nar/gkag897"
repo_url: "https://github.com/HikaruSugimoto/tfactprofiler"
web_tool: "https://tfact.wpgsa.org/"
added_date: "2026-09-18"
---

# TFActProfiler

## 1. 核心定位与解决痛点
- **背景痛点**：
  1. 传统基于 ChIP-seq / Motif 扫描的网络（如 ChIP-Atlas）覆盖广但假阳性极高；精编集合（如 DoRothEA）假阳性低但覆盖的 TF 极度匮乏。
  2. 几乎所有传统 Regulon 都缺乏“带正负符号（+激活 / -抑制）”与“连续调控权重”，导致其只能用于打富集分，无法预测敲除某个 TF 之后全基因组的表达漂移。
- **核心机制**：
  - 融合 ChIP-Atlas、Motif、CollecTRI、CellOracle 先验，在海量人体组织单细胞图谱（*Tabula Sapiens*）与 Bulk 图谱（*ARCHS4*）上训练拟合，生成了包含 **2,606,176 条带正负极性与定量连续权重的 TF–mRNA 调控网络**。
  - 具备原生“自调控屏蔽”策略防偏差，并利用残差均方误差（MSE）提供每个细胞的可信度质控。

## 2. 选型对比（何时选它 vs 选竞品？）
| 对比维度 | TFActProfiler | DoRothEA (decoupleR) | SCENIC / SCENIC+ | GEARS / scGPT |
| :--- | :--- | :--- | :--- | :--- |
| **网络极性** | ✅ 带符号 (+/-) 与连续权重 | ⚠️ 仅分级置信度 (A-E) | ⚠️ 仅二值/简单共表达 | 依赖深度网络黑盒 |
| **扰动响应预测** | ✅ **零额外训练直接预测** | ❌ 无法预测扰动 | ❌ 需配合动力学模拟 | ⚠️ 需大量 Perturb-seq 训练 |
| **算力与运行时间** | 秒级（标准线性回归/ULM） | 秒级 | 分钟至小时级（较慢） | 极重（需多卡 GPU 训练） |
| **可靠素质控** | ✅ 细胞级 MSE 残差 | ❌ 无 | ❌ 无 | ⚠️ 仅测试集 Loss |
| **最佳适用场景** | 快速评估单细胞 TF 活性 + 探索性模拟敲除 TF | 经典基准 TF 活性打分 | 结合 scATAC 探索顺式调控 | 拥有大规模真实微扰筛选数据 |

## 3. 5 分钟极简可运行代码（Minimal Working Example）

```python
import scanpy as sc
import decoupler as dc
import tfactprofiler as tfp
import pandas as pd

# 1. 加载对数化单细胞数据 (以 PBMC 为例)
adata = dc.ds.pbmc3k()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=3000)

# 2. 载入官方 260 万条带符号先验网络 (从 GitHub / Zenodo 下载)
# https://raw.githubusercontent.com/HikaruSugimoto/tfactprofiler/main/example/TFactprofiler_all.csv
prior_net = pd.read_csv("TFactprofiler_all.csv")

# 3. 任务 A: 推断单细胞转录因子活性得分 (基于 ULM 模型)
dc.mt.ulm(data=adata, net=prior_net)
tf_scores = dc.pp.get_obsm(adata, key="score_ulm")

# 4. 任务 B: 计算单细胞推断置信度指标 (MSE 越小越可信)
adata = tfp.estimate_reliability(adata, prior_net, cluster_key="celltype")
print("Top 5 cells MSE:", adata.obs["mse"].head())

# 5. 任务 C: 免训练模拟敲除某个转录因子 (如 TP53 敲低)
# res_df = tfp.perturbation_predict(
#     RNA_data=adata.to_df().T,
#     prior_knowledge=prior_net,
#     perturb_tf="TP53",
#     perturb_value=0.0
# )
```

## 4. 常见陷阱与注意事项（Gotchas）
1. **基因名必须为大写 Symbol**：输入矩阵必须是人类标准 Gene Symbol（全大写），如果是小鼠数据，需通过 Ensembl 同源基因字典（Biomart）先转换为大写 Human Orthologs。
2. **切忌使用原始非对数化 Reads**：`adata.X` 必须是 `log1p` 标准化后的数值，否则 Ridge 回归权重会发生严重尺度偏移。
3. **器官特异性需求**：全库 `TFactprofiler_all.csv` 适于全血或泛组织分析；若分析肝、脑、胰腺等专用组织，建议从官方仓库 `TFactprofiler_organ/` 目录选用对应器官的 CSV，以剔除非特异性相互作用。
