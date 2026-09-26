---
name: "BioNeMo Structure Prediction Pipeline (bsppctl)"
category: ["结构生物学", "蛋白质 3D 结构预测", "AI4Science 基础设施", "GPU 加速推理"]
target_problems:
  - "蛋白序列 → 3D 结构预测（单链与多链复合物）"
  - "大规模 MSA 构建与结构预测的流水线编排（千级靶点到百万级）"
  - "复合物界面打分与置信度质控（pLDDT / PAE / ipSAE / pDockQ2）"
data_modalities: ["protein-sequence", "protein-structure"]
inputs:
  format: "FASTA（氨基酸序列；多链复合物按链组成写入同一条目标记录，解析器要求 .fa 后缀）"
  expression_scale: "不适用——输入是序列，不是定量表达矩阵"
  feature_identifier: "序列本身 / UniProt accession；postprocessing 还需要 UniProt 映射参考数据"
  required_metadata: "Cluster Profile（Slurm + Pyxis + Enroot 连接、路径、镜像、挂载、账号与资源默认值）、Phase Plan、MSA 搜索数据库、模型权重、持久化 authority 目录"
outputs:
  primary: "预测 3D 结构文件（ModelCIF / BinaryCIF）+ Parquet 清单，覆盖单链与多链复合物"
  confidence_metrics: "逐残基 pLDDT、PAE（predicted aligned error）矩阵、复合物界面分 ipSAE 与 pDockQ2、steric clash 检查"
dependencies: ["Python 3.12", "uv", "Docker（构建镜像）", "PyArrow（benchmark 重建）", "Slurm + Pyxis + Enroot", "S3 兼容对象存储"]
hardware_requirements: "Slurm 集群 + x86-64 CPU + NVIDIA GPU 显存 ≥80GB（A100 80GB / H100 80GB）；仅 UniRef30 搜索索引约 240GB，强烈建议 NVMe；控制端（bsppctl）本身只需普通 Linux + Python 3.12"
paper:
  title: "无独立方法学论文；对应 AlphaFold DB 复合物数据集的发布（NVIDIA / EMBL-EBI / Google DeepMind 联合）"
  journal: "NVIDIA 开源软件（仓库创建 2026-09-16）"
  doi: "N/A"
repo_url: "https://github.com/NVIDIA-BioNeMo/BioNeMo-Structure-Prediction-Pipeline"
added_date: "2026-09-26"
---

# BioNeMo Structure Prediction Pipeline (bsppctl)

## 1. 核心定位与解决痛点

- **背景痛点**：AlphaFold2 / OpenFold2 能预测结构，但"把一个序列预测成结构"和"把上百万条序列预测成结构"是两件完全不同的事。单机 notebook 方案（典型如 ColabFold 交互式）在靶点数量上千后，MSA 构建、任务分发、失败重试、结果交接和置信度质控全部变成手工劳动；而实验结构解析（晶体学 / 冷冻电镜）单条结构成本以年计、以千美元计。
- **核心机制**：这不是一个新模型，而是一套**把已有模型工程化成可规模化流水线的编排系统**。用 `bsppctl` 一个 CLI，把流程切成三个互相解耦的阶段，每阶段作为容器化 Slurm 作业运行：
  1. **Preprocessing**：用 ColabFold 的 `colabfold_search` + MMseqs2 GPU 搜索，在 GPU 上为每个靶点构建 MSA。
  2. **Folding**：用 OpenFold2 加载 **AlphaFold2-Multimer 权重** 预测结构（单链靶点可选 OpenFold2 pTM 权重），由 **NVIDIA BioNeMo Inference Runtime** 加速；也可切换成标准 OpenFold2 或 ColabFold 后端。
  3. **Postprocessing**：用 PDBe 的 AFDB Integration Kit 计算复合物界面打分（ipSAE、pDockQ2）、做 steric clash 检查，导出 ModelCIF / BinaryCIF 与 Parquet 清单。
- **工程学关键点**：每个阶段被"钉死"到校验过校验和的输入上，作业记录验证通过后签发 **receipt**；阶段之间通过本地存储或 S3 兼容对象存储交接，因此三个阶段可以跑在同一个集群，也可以跑在不同集群。folding 阶段还能按序列长度做负载均衡，把靶点摊到多张 GPU 上。
- **公开成果**：NVIDIA 与 EMBL-EBI、Google DeepMind 用这条流水线产出了两批已进入 AlphaFold DB 的公开数据——2,800 多种病毒的蛋白复合物（大流行备战），以及约 3,100 万条预测里筛出的约 180 万条高置信度复合物（覆盖 4,777 个 proteome）。

## 2. 选型对比（何时选它 vs 选竞品？）

| 对比维度 | **BioNeMo BSPP (bsppctl)** | ColabFold（单机版） | ESMFold |
| :--- | :--- | :--- | :--- |
| **模型/方法类型** | 编排系统，底层 OpenFold2 + AlphaFold2-Multimer 权重（可选 ColabFold / 标准 OpenFold2 后端） | AlphaFold2 的易用封装，含 `colabfold_search` MSA 服务器与本地搜索 | 蛋白语言模型，单序列直接预测 |
| **是否需 MSA** | 需要，且是流水线第一等公民（GPU MMseqs2 搜索） | 需要 | **不需要**，靠语言模型隐式学到的共进化 |
| **算力与部署** | 硬门槛最高：Slurm + Pyxis + Enroot + ≥80GB 显存 GPU + Docker 构建镜像 + ~240GB 搜索索引 + 对象存储 | 一台带 GPU 的机器即可，笔记本也能跑（慢），或直接用官方 notebook | 一台 GPU 即可，吞吐极高 |
| **可扩展规模** | **千级至百万级靶点**，多 GPU 分摊、失败重试、阶段跨集群交接 | 十到百级靶点，再往上需要自己写批处理脚本 | 千级容易，但精度在难靶点上明显落后 |
| **主要劣势** | 极重的运维负担；**没有单条端到端命令**；仓库很新（2026-09 创建）、仍在快速变动；`openfold-trt` 后端只是占位、会 fail closed | 大批量缺任务编排、断点续跑和质控汇总 | 多链复合物与界面精度明显不如 AF2-Multimer 系 |
| **最佳适用场景** | **结构性目标**：要在自有集群上批量产出复合物结构（自建 AFDB 式资源、病原体结构库、大规模突变体筛选） | 少量靶点的即时验证与探索 | 极大批量初筛、对精度要求不高的快速轮廓 |

**一句话选型**：靶点少于几十条 → 用 ColabFold；只想看某个已知蛋白的结构 → 先查 AlphaFold DB 有没有现成预测；**只有在"批量 + 复合物 + 自有集群"三个条件同时成立时，这条流水线才划算**。

## 3. 5 分钟极简可运行代码（Minimal Working Example）

**必须先说清楚**：真正出结构需要 Slurm 集群 + 80GB 显存 GPU，**5 分钟内在普通机器上跑不完**。因此下面分两段——A 段是**无需 GPU、真能 5 分钟跑通**的控制端与基准重建；B 段是出结构所需的阶段提交（模板，需集群资产，标注为不可直接运行）。

### A. 控制端 + 公开基准重建（无需 GPU，可真跑）

```bash
git clone https://github.com/NVIDIA-BioNeMo/BioNeMo-Structure-Prediction-Pipeline.git
cd BioNeMo-Structure-Prediction-Pipeline

# 1) 安装控制端 CLI（只装轻量编排工具，科学计算都在容器里）
uv sync --frozen --package bspp-orchestration-control --no-dev
uv run --frozen --package bspp-orchestration-control --no-dev bsppctl --help

# 2) 校验随仓库附带的 1000 靶点基准输入包（750 单体 / 150 二聚体 / 50 三聚体 / 50 四聚体）
(cd docs/benchmarks/pdb-temporal-2022-2025-v1 && sha256sum -c SHA256SUMS)

# 3) 从公开 RCSB 下载重建基准语料（不需要任何凭证），并用指纹确认身份
export BSPP_BENCHMARK_ROOT=/path/to/new-benchmark-workspace
mkdir -p "$BSPP_BENCHMARK_ROOT"
uv run --frozen --package bspp-orchestration-control --no-dev --with pyarrow \
  bsppctl prepare-benchmark \
  --spec docs/benchmarks/pdb-temporal-2022-2025-v1/benchmark-spec.json \
  --reconstruct docs/benchmarks/pdb-temporal-2022-2025-v1/reconstruction-targets.jsonl \
  --output "$BSPP_BENCHMARK_ROOT/corpus" --workers 4

python3 - "$BSPP_BENCHMARK_ROOT/corpus/dataset.json" <<'PY'
import json, sys
expected = "c04ec62e6eecf165eea010f82f7aa1ad72ddfd99ce462a9c4afeac286049a217"
actual = json.load(open(sys.argv[1]))["dataset_fingerprint"]
if actual != expected:
    raise SystemExit(f"Corpus identity changed: expected {expected}, got {actual}")
print("Published benchmark fingerprint matches.")
PY

# 4) 预处理解析器要求 .fa 后缀：做一份字节相同的副本
cp "$BSPP_BENCHMARK_ROOT/corpus/targets.fasta" "$BSPP_BENCHMARK_ROOT/benchmark-input.fa"
```

### B. 提交预处理 / 折叠 / 后处理（需集群资产，模板不可直接运行）

```bash
# 三个阶段的 Plan 模板就在仓库里，路径与镜像名都是占位符，必须先换成真实值
ls skills/examples/run-plans/            # cluster-profile / preprocessing / folding / postprocessing

# 阶段生命周期（materialize → submit → status → resume → cancel → retry → finalize）
bsppctl phase materialize --profile <cluster-profile.yaml> --plan <preprocessing-phase-plan.yaml>
bsppctl phase submit      --run <runspec-id>
bsppctl phase status      --run <runspec-id>
bsppctl phase finalize    --run <runspec-id>     # 校验作业记录后签发 receipt

# 注意：folding 阶段要先显式设置 folding_release_preset: public，
# 否则默认走 internal 预设。
```

### C. 如果你只是"想拿到一个结构"（绕过集群的现实路径）

```bash
# 单机替代方案：不涉及本流水线，仅作对照
pip install "colabfold[alphafold]"
colabfold_batch input.fa out_dir/          # 输入同一个 FASTA，输出含 pLDDT 与 PAE 的结果目录
# 或者先查 AlphaFold DB 是否已有该 UniProt 的现成预测：https://alphafold.ebi.ac.uk/
```

## 4. 常见陷阱与注意事项（Gotchas）

1. **没有端到端单条命令**。`preprocessing → folding → postprocessing` 之间必须人工阶段交接，没有任何公开协调器一次跑完。别指望 `bsppctl run-all`。
2. **Plan 模板里的路径和镜像名是假值**。schema 校验通过 **不等于** 镜像、输入文件、checkpoint 或远端对象真的存在。必须逐项替换为已核实的资产。
3. **`openfold-trt` 是空壳**。文档明确写着它"contract value only; execution fails closed"——选了它会直接失败，不是性能问题。
4. **`folding_release_preset` 默认是 `internal`**。跑公开基准必须显式设为 `public`，漏设会走到非预期配置。
5. **`validate-run` 必须要 S3 语料位置**，不接受本地目录参数。所以"我把公开参考数据下载到本地"并不能满足它的传输要求。
6. **"完成"有三层不同含义**：scheduler 退出成功 = 作业完成；phase finalize = 证据封存并签发 receipt；benchmark validation = 预测结果与配置的套件比对。**三者都不能单独证明实验精度**。
7. **输入 FASTA 必须是 `.fa` 后缀**。预处理解析器对后缀敏感，用 `.fasta` 会出问题——所以官方 quickstart 里要显式做一份 `.fa` 副本。
8. **硬件不要低估**：显存 ≥80GB 只是入场券，UniRef30 索引本身约 240GB，SSD 吞吐直接决定 preprocessing 是否成为瓶颈。
9. **仓库很新且不接受贡献**（创建 2026-09-16，README 明确 "not accepting contributions"）。API 与文档可能随时变，锁到具体 commit（文档给出的快照是 `9af63428fb0b721d9c81f98c3e41d045d87184d9`）再引用。
10. **许可分层**：代码 Apache-2.0；随仓库的 PDB 基准数据集是 CC0-1.0；第三方组件见 `THIRD_PARTY_NOTICES.md`（500KB，引用前值得一读）。

## 5. 对本课题组的相关性（sepsis / 多组学）

- **直接可用性低**：本流程产出的是"结构"，不是"表达量"。sepsis 方向的常规分析（Olink 血浆蛋白组、bulk/scRNA 表达矩阵、临床队列建模）与它不在同一数据模态上，无法直接接入。
- **唯一真实的接入口**：当研究需要对某个具体蛋白靶点做结构层面推论时——例如孟德尔随机化找到的 sepsis 候选靶点（如 DUSP13、INHBC、TLR1）要做口袋分析或虚拟筛选，或要做宿主–病原体复合物建模。此时**增量点在于复合物结构**，因为 AlphaFold DB 里人类单体结构早已存在，重复预测单体没有意义。
- **不建议**为了用这套流水线而去找一个 sepsis 问题；应反过来，先有结构层面的科学问题，再评估是否值得承担这套集群运维成本。
