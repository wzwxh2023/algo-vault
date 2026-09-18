---
name: "MAPA"
category: ["多模态整合", "多组学通路分析", "功能模块发现", "大模型生信智能体"]
target_problems:
  - "多组学 (转录+蛋白+代谢) 通路富集结果严重冗余与去重难题 (Functional Redundancy Reduction)"
  - "无重叠基因但功能相关通路的语义关联发现 (Zero-overlap Semantic Pathway Linkage)"
  - "基于 PubMed RAG 的自动化生物学机制解读与综述生成 (Automated Literature-Grounded Interpretation)"
data_modalities: ["Transcriptomics", "Proteomics", "Untargeted Metabolomics"]
inputs:
  format: "R data.frame (包含分子 ID 与差异检验结果, 或已富集的 pathway 对象)"
  expression_scale: "Log2 Fold Change, P-value / FDR, 或预排序分子列表"
  feature_identifier: "Ensembl ID / Gene Symbol (基因/蛋白), HMDB ID / KEGG ID (代谢物)"
  required_metadata: "物种注释数据库 (如 org.Hs.eg.db, org.Mm.eg.db)"
outputs:
  primary: "functional_module_result 数据框 (模块 ID、归属通路集、关键分子、LLM 命名与综述文本)"
  confidence_metrics: "聚类质量指标 (Silhouette 轮廓系数, Davies-Bouldin), RAG 文献契合度置信度得分 (0-1)"
dependencies: ["mapa", "simona", "clusterProfiler", "igraph", "Cairo"]
hardware_requirements: "单机 CPU (常规笔记本或服务器均可, 无需 GPU；需网络访问以支持 PubMed 与 LLM API)"
paper:
  title: "MAPA: A Semantic Network Framework for Functional Module Discovery and Interpretation in Multi-Omics Data"
  journal: "Advanced Science, 2026"
  doi: "10.1002/advs.77774"
  pmid: "42750316"
repo_url: "https://github.com/jaspershen-lab/mapa"
web_tool: "https://mapashiny.jaspershenlab.com/"
tutorial_url: "https://www.shen-lab.org/mapa-tutorial/"
added_date: "2026-09-18"
---

# MAPA (Modular Analysis and Phenotype-informed Annotation)

## 1. 核心定位与解决痛点
- **背景痛点**：
  1. **海量冗余刷屏**：传统 ORA (Over-Representation Analysis) 或 GSEA 经常富集出数百条高度同义但分属不同数据库的通路（如 Cell Cycle 相关的数十个条目），研究者常被迫随意截取前 5~10 条，导致关键中低位通路丢失。
  2. **传统重叠算法失效（Zero-overlap 盲区）**：传统 Jaccard 相似度依赖共有基因数。若两条通路属于同一下游生理事件但没有共享基因（如细胞膜受体激活 vs 细胞核转录），传统方法判定相似度为 0 并强行割裂。
  3. **代谢组与转录组脱节**：代谢物富集（HMDB/SMPDB）与基因富集（GO/KEGG）使用不同字典体系，极难构建端到端因果故事。
  4. **人工机制综述撰写成本极高**：研究者需要耗费数天逐个阅读文献归纳通路背后的机制。
- **核心机制**：
  - **Biotext Embedding 语义嵌入**：将通路层级描述映射为文本向量，基于余弦相似度计算生物学语义关联，打破共有分子限制。
  - **语义-生物学融合网络**：结合分子网络与通路语义，引入重启随机游走（RWR）与 Louvain 社区聚类，自动基于轮廓系数寻优聚类超参数。
  - **四阶 PubMed RAG 智能体**：动态检索 PubMed 文献 ➔ 向量初筛 ➔ LLM 相关性重排（0-1）➔ 生成带引文支撑的结构化机制综述。

---

## 2. 选型对比（何时选 MAPA vs 竞品？）

| 对比维度 | MAPA (*Adv Sci 2026*) | aPEAR (*Bioinformatics 2023*) | PAVER (*2024*) | 经典 enrichplot / clusterProfiler |
| :--- | :--- | :--- | :--- | :--- |
| **相似度度量原理** | **LLM 生物文本嵌入 + 经典语义双轨** | 仅分子 Jaccard / Cosine / 相关性 | 文本嵌入 + 余弦距离 | 仅分子 Jaccard 重叠 |
| **真实聚类一致性 (ARI)** | 🏆 **0.95** | 0.23 – 0.33 | 0.31 – 0.45 | 0.28 – 0.40 |
| **无重叠基因通路关联** | ✅ **优秀（基于语义表征）** | ❌ 无法关联 (相似度=0) | ⚠️ 局部支持 | ❌ 无法关联 |
| **跨组学整合能力** | ✅ **转录组 + 蛋白质组 + 非靶向代谢组** | ❌ 仅支持单一基因列表 | ❌ 仅支持基因 | ⚠️ 仅支持基本基因列表 |
| **自动化文献落地解读** | ✅ **内置 PubMed 动态 RAG 综述生成** | ❌ 无，仅网络绘图 | ⚠️ 仅生成关键词标签 | ❌ 无，仅基础图表 |
| **交互式 Web 支持** | ✅ **MAPAShiny 在线平台** | ❌ 仅 R 代码包 | ❌ 仅 Python 包 | ❌ 需自写代码 |
| **最佳适用场景** | **复杂多组学整合、需发表高水平机制文章** | 单一转录组简单聚类出图 | 快速文本聚类 | 基础探索性单基因集快速检验 |

---

## 3. 5 分钟极简可运行代码（Minimal Working Example）

```r
library(mapa)

# 1. 准备差异基因输入并做 ID 转换 (支持 ensembl, symbol, entrezid)
example_dt <- read.csv("differential_expression_genes.csv")
variable_info <- convert_id(
  data = example_dt,
  query_type = "gene",
  from_id_type = "ensembl",
  organism = "org.Hs.eg.db"
)

# 2. 多数据库联合富集分析 (内置 ORA 引擎)
enriched_res <- enrich_pathway(
  variable_info = variable_info,
  query_type = "gene",
  database = c("go", "kegg", "reactome")
)

# 3. 计算 Biotext Embedding 语义相似度 (推荐 OpenAI text-embedding-3-small)
sim_matrix <- get_bioembedsim(
  object = enriched_res,
  api_provider = "openai",
  text_embedding_model = "text-embedding-3-small",
  api_key = Sys.getenv("OPENAI_API_KEY"),
  database = c("go", "kegg", "reactome"),
  save_to_local = FALSE
)

# 4. 自适应社区发现：合并为功能模块 (Functional Modules)
modules_res <- get_functional_modules(
  object = sim_matrix,
  sim.cutoff = 0.7,
  cluster_method = "louvain"
)

# 5. 调用 PubMed RAG 智能体自动撰写模块机理报告
annotated_res <- llm_interpret_module(
  object = modules_res,
  module_content_number_cutoff = 2,
  api_key = Sys.getenv("OPENAI_API_KEY")
)

# 6. 一键导出发表级网络图与完整 Markdown 报告
report_functional_module(
  object = annotated_res,
  path = "./mapa_output_report",
  type = "md"
)
```

---

## 4. 常见陷阱与注意事项（Gotchas）

1. **API Key 与网络连通性**：
   `get_bioembedsim()` 和 `llm_interpret_module()` 依赖大语言模型与 PubMed 实时检索。若在无网络连接的离线超算上运行，请改用传统相似度模式 `merge_pathways(measure.method.kegg = "jaccard")`。
2. **代谢物 ID 匹配规范**：
   代谢组分析时强烈建议提供标准 **HMDB ID** 或 **KEGG Compound ID**，纯化合物俗名（Common Name）易因异构体命名分歧造成富集失真。
3. **聚类阈值（sim.cutoff）微调**：
   默认 `sim.cutoff = 0.7` 是经过超参数扫网验证的稳健默认值。若产生过多单通路碎模块（Singletons），可使用 `determine_optimal_clusters()` 自动评估 Silhouette 峰值对应的最优参数。
