# 🧬 Algo-Vault — 面向计算生物学与多组学分析的“可执行算法储备库”

> **定位**：拒绝只存标题和摘要的“文献黄页”。Algo-Vault 是一个专为**人类研究者**与 **AI Agent 智能体**设计的**可执行、可检索算法知识库**。
> 每一个收录的算法均包含机器可读契约（YAML）、数据输入/输出规范、竞品选型横评与 5 分钟极简可运行代码。

---

## 📑 已收录算法索引 (Curated Algorithms Index)

| 编号 | 算法名称 | 核心分类 | 关键解决问题 | 论文出处 | 卡片直达 |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **001** | **[TFActProfiler](transcriptomics/TFActProfiler.md)** | 单细胞转录组 / 基因调控网络 / 扰动生物学 | 260万带符号先验的 TF 活性推断、免训练扰动响应预测、单细胞残差置信度质控 | *NAR 2026* | [👉 点击阅读卡片](transcriptomics/TFActProfiler.md) |
| **002** | **[scTFA-Benchmark](transcriptomics/scTFA_Benchmark.md)** | 单细胞转录组 / 调控网络 / 基准评测 | 基于大规模 Perturb-seq 扰动金标准的 8 种 TFA 算法权威横评与选型指南 (含 metaTF / decoupleR / pySCENIC) | *Brief Bioinform 2026* | [👉 点击阅读卡片](transcriptomics/scTFA_Benchmark.md) |
| **003** | **[MAPA](multi_omics/MAPA.md)** | 多模态整合 / 多组学通路分析 / LLM智能体 | 基于生物文本嵌入与 PubMed RAG 的多组学功能模块发现与无幻觉自动化机制解读 | *Advanced Science 2026* | [👉 点击阅读卡片](multi_omics/MAPA.md) |

---

## 📂 仓库分类体系

```text
algo-vault/
├── README.md                      # 仓库主索引与 AI 交互指南
├── templates/
│   └── algorithm_card_template.md # 算法知识卡片标准化模板
├── tools/
│   └── search_vault.py            # 本地极简语义检索工具（支持 Agent 调用）
├── examples/
│   └── demo_quickstart.py         # 端到端快速上手脚本
│
├── transcriptomics/               # 单细胞 / Bulk 转录组算法 (已收录: TFActProfiler, scTFA-Benchmark)
├── spatial_omics/                 # 空间转录组 / 空间多组学 (Visium, MERFISH, Xenium)
├── multi_omics/                   # 多模态整合 (scRNA + scATAC, CITE-seq, 已收录: MAPA)
├── epigenomics/                   # 表观遗传与染色质 (scATAC, Hi-C, 甲基化)
├── proteomics_metabolomics/       # 单细胞质谱、蛋白质组与代谢组
└── foundation_models/             # 生物学基础大模型与 AI4Science Agent
```

---

## 🔍 如何使用与检索算法？

### 方式 1：让 AI Agent 帮你自动检索（推荐）
在与 Antigravity / Claude 等 AI 助手对话时，直接发送以下指令：
> *“请检索我本地的 `algo-vault`，我目前有一批 `scRNA-seq` 数据，想研究细胞受药物刺激后的转录因子网络重编程，请推荐最合适的算法并说明数据输入要求。”*

AI 将自动调用 `tools/search_vault.py` 或扫描卡片 YAML 标签，为您输出结构化建议与即开即用的 Python 代码。

### 方式 2：命令行快速搜索
```bash
# 查看库内所有收录的算法
python3 tools/search_vault.py

# 按生物学任务/关键词检索
python3 tools/search_vault.py "转录因子"
python3 tools/search_vault.py "扰动预测"

# 输出 JSON 格式（供脚本流水线或自动化 Agent 消费）
python3 tools/search_vault.py --json
```

---

## 📝 如何新增算法入库？

1. **AI 自动化提取（极简）**：
   将您刚看过的文献或 GitHub 链接发送给 AI：
   > *“帮我解读这篇论文，并按照 `templates/algorithm_card_template.md` 规范提取出一张算法卡片，存入 `algo-vault/` 对应的子目录下。”*
2. **人工手动模板套用**：
   复制 `templates/algorithm_card_template.md`，填写 YAML 头部与核心章节即可。

---

## 🔗 与其他项目的协同闭环

* **数据源头**：上游配合 [`../algorithm-hot`](../algorithm-hot)（每日六轨自动追踪生物信息与多组学方法学顶刊论文）；
* **沉淀过滤**：从每日动态追踪的论文中，筛选出具有重大实用价值的新方法；
* **归档落地**：在本项目（`algo-vault`）中落地为“标准化执行资产”，并同步至 GitHub 永久保存。
