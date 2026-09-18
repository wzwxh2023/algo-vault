---
name: "RADAR"
category: ["基础大模型", "医疗多模态AI", "3D医学影像", "全腹部CT诊断"]
target_problems:
  - "全腹部 CT 18 个解剖器官、146 种病征的通用全景初筛与专家级辅助诊断 (Generalist Abdominal CT Diagnosis)"
  - "无需手工像素级病灶勾画的大规模弱监督图文对比学习 (Label-free 3D Image-Text Alignment)"
  - "急诊急腹症 (肠梗阻、气腹穿孔、腹主动脉瘤、结石积水) 零样本快速预警与防漏诊 (Emergency Zero-Shot Triage)"
data_modalities: ["Abdominal CT (3D Volume)", "Contrast-enhanced CT", "Non-contrast CT", "Radiology Reports"]
inputs:
  format: "3D NIfTI (.nii.gz / .nii) 或通过 dcm2niix 转换自 PACS 的 DICOM 序列"
  expression_scale: "CT 软组织窗截断 [-300, 400] HU，归一化至 [0, 1]，体素重采样至 (1.0, 1.0, 5.0) mm"
  feature_identifier: "3D CT Volume 空间张量 [C, D, H, W]"
  required_metadata: "无硬性要求 (可选配临床放射学报告用于微调或外部验证评估)"
outputs:
  primary: "RADAR_infer_results_{tag}.csv (包含 146 种腹部病征的阳性概率置信度预测打分)"
  confidence_metrics: "146 维病变阳性预测得分 [0, 1]、多中心独立验证受试者操作特征曲线下面积 (AUC)"
dependencies: ["torch>=2.0", "monai>=1.3", "simpleitk", "transformers>=4.25", "dynamic-network-architectures"]
hardware_requirements: "推理仅需单张 24GB 显存 GPU (如 NVIDIA RTX 3090 / 4090 / A10 / A100)；训练需多卡分布式集群"
paper:
  title: "An expert-level generalist AI for abdominal CT diagnosis"
  journal: "Science, 2026"
  volume: "393"
  issue: "6817"
  pages: "eaec6129"
  doi: "10.1126/science.aec6129"
repo_url: "https://github.com/alibaba-damo-academy/damo-radar"
weights_url: "https://huggingface.co/radar-generalist"
added_date: "2026-09-19"
---

# RADAR: 面向全腹部 CT 诊断的专家级通用多模态人工智能

## 1. 核心定位与解决痛点
- **背景痛点**：
  1. **“专病专模”无法应对临床全景**：传统医疗影像 AI 多为单一病种模型（如只看肝癌或只看胰腺炎）。全腹部包含 18 个复杂重叠器官，单一模型面对多病共存时极易造成灾难性漏诊。
  2. **像素级手工勾画（Mask）成本高昂**：以往分割或检测网络要求放射科医生逐层手动标注数万例病灶边缘，数据扩展瓶颈极其严峻。
  3. **急诊急腹症时间窗口极度紧迫**：夜间急诊年轻值班医生经验有限，微量游离气体（穿孔）、不全性肠梗阻或腹主动脉瘤破裂前兆误诊率高。
- **核心机制**：
  - 由浙江大学医学院附属第一医院（梁廷波团队）与阿里巴巴达摩院（张灵团队）联合研发，发表于 ***Science* 2026**。
  - **42.5 万例大规模预训练**：利用 150 万个 3D CT 影像-报告图文对及 1500 万个解剖特异性对进行端到端对比学习。
  - **免人工勾画的解剖空间对齐**：引入 TotalSegmentator 自动化提取 36 个器官 3D 解剖边界，通过 NLP 解析报告段落，建立器官级细粒度图文对比学习（ITC）与动量蒸馏机制。
  - **单卡轻量化推理**：核心推理参数仅 **2~3.5 亿（约 1.5GB 权重）**，单张 24G 显卡（RTX 3090/4090）滑动窗口秒级完成 146 种病征筛查。

---

## 2. 选型对比（何时选 RADAR vs 竞品？）

| 对比维度 | RADAR (*Science 2026*) | Stanford Merlin (*2024*) | 传统 3D UNet / nnU-Net | 2D 医疗 VLM (如 BiomedCLIP) |
| :--- | :--- | :--- | :--- | :--- |
| **影像输入维度** | **3D 连续容积 CT** | 3D 容积 CT | 3D 局部 Patch | 仅支持 2D 单切片（丢弃层间信息） |
| **病征覆盖广度** | 🏆 **18 个器官 / 146 种病征** | 约 20 种急诊常见病征 | 仅 1 种特定疾病 (专病专模) | 局限于胸片或浅表 2D 影像 |
| **标注数据依赖** | 🏆 **完全免人工病灶勾画** | 免标注 (急诊图文报告) | ❌ 强依赖医生逐层像素级标注 | 免标注 (仅限 2D 图文) |
| **内部测试集 AUC** | 🏆 **0.913** (146 种平均) | 约 0.88 | 局限于单一任务 Dice 值 | N/A |
| **外部多中心泛化** | 🏆 **0.895** (8 家异源三甲医院) | 0.883 (单中心急诊测试) | 跨院跨机型易性能崩塌 | 跨模态泛化中等 |
| **急诊急腹症适用** | 🏆 **Zero-shot AUC 0.904** | 针对急诊设计 | 无法应对全腹未知并发症 | 不适用 |
| **显存与硬件门槛** | **单卡 24GB (3090/4090 即可)** | 需高显存服务器 | 较低 | 极低 |
| **最佳适用场景** | **全腹 CT 全景筛查、急腹症防漏诊、大样本免标验证** | 斯坦福急诊基准评测 | 确诊患者的精确手术规划分割 | 2D 胸部 X 光片快速分类 |

---

## 3. 5 分钟极简可运行代码（Minimal Working Example）

根据开源仓库提供的推理流程，单机加载预训练模型直接对 3D 腹部 CT 进行 146 种病变评分：

```python
import os
import torch
import numpy as np
import pandas as pd
from monai import transforms
from monai.data.utils import dense_patch_slices
from dynamic_network_architectures.vision_branch import VisionBranch

# 1. 影像预处理：加载 3D NIfTI 并执行标准腹部软组织窗截断与重采样
def preprocess_ct_volume(nii_path):
    data = {"image": nii_path}
    res = transforms.LoadImaged(keys=["image"], image_only=False, ensure_channel_first=True)(data)
    
    affine = res["image_meta_dict"]["affine"]
    spacing = (abs(affine[0, 0].item()), abs(affine[1, 1].item()), abs(affine[2, 2].item()))
    _, h, w, d = res["image"].shape
    
    # 重采样到 RADAR 基准空间分辨率 (1.0, 1.0, 5.0) mm
    ref_spacing = (1.0, 1.0, 5.0)
    scale = [spacing[i] / ref_spacing[i] for i in range(3)]
    target_size = [int(h * scale[1]), int(w * scale[0]), int(d * scale[2])]
    
    trans = transforms.Compose([
        transforms.Resized(spatial_size=target_size, keys=["image"], mode="trilinear"),
        transforms.Transposed(keys=["image"], indices=(0, 3, 2, 1)),
    ])
    resized = trans(res)["image"]
    
    # 标准软组织窗截断 [-300, 400] HU 并归一化到 [0, 1]
    resized[resized > 400] = 400
    resized[resized < -300] = -300
    norm_img = (resized - resized.min()) / (resized.max() - resized.min() + 1e-8)
    return norm_img.unsqueeze(0)  # [1, 1, D, W, H]

# 2. 加载预训练权重与 146 种临床表现的文本特征嵌入
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = VisionBranch(in_channels=1).to(device)
ckpt = torch.load("ckpt/checkpoint_radar_pretrain.pth", map_location=device)
model.load_state_dict(ckpt["model"], strict=False)
model.eval()

# 官方提取好的 146 种病征文本正负提示词嵌入字典
text_feat_dict = torch.load("ckpt/infer_text_embedding_radar.pt", map_location=device)

# 3. 滑动窗口轻量化推理 (Patch: 96x256x384, 彻底避免 24G 显存溢出)
input_tensor = preprocess_ct_volume("data/demo_cases/patient_001.nii.gz").to(device)
roi_size = (96, 256, 384)

with torch.no_grad():
    # 提取多尺度器官级 3D 视觉特征向量
    _, _, feat1, feat2, feat3, _, _, _ = model(input_tensor, None)
    visual_feat = torch.cat([feat1, feat2, feat3], dim=1).mean(dim=1)
    visual_feat = torch.nn.functional.normalize(visual_feat, dim=-1)

# 4. 计算影像与 146 种病变的相似度得分 (以肠梗阻、结石、腹主动脉瘤为例)
results = {}
for finding, text_embed in text_feat_dict.items():
    score = torch.matmul(visual_feat, text_embed.T).max().item()
    results[finding] = score

# 导出预测结果 CSV
df_result = pd.DataFrame([results], index=["patient_001"])
df_result.to_csv("RADAR_predictions.csv")
print("Top 3 预测病变得分:", df_result.iloc[0].nlargest(3))
```

---

## 4. 常见陷阱与注意事项（Gotchas）

1. **DICOM 至 NIfTI 的空间轴翻转问题**：
   - 医院 PACS 导出的 DICOM 序列切片顺序必须使用标准工具（如 `dcm2niix -z y`）转换。切忌手动通过 numpy 堆叠切片，否则容易颠倒 Z 轴正负向导致解剖位置倒置。
2. **增强 CT vs 平扫 CT 的合理预期**：
   - 模型预训练主体为**增强 CT 门脉期**。在急诊**平扫 CT** 下：
     - **极度有效**：肠梗阻（AUC 0.97）、泌尿系结石/肾积水（AUC 0.94）、气腹穿孔、腹主动脉瘤（AUC 0.99）、腹水。
     - **需谨慎对待**：主动脉夹层（平扫仅能抓钙化内移等间接征象，确诊须做增强 CTA）、微小早期胰腺癌（无强化灌注差，平扫易漏）。
3. **输入尺度上限跳过机制**：
   - 官方代码中包含保护逻辑：若重采样后某一空间维度尺寸 `> 1000` 切片，建议先剔除无效的颈部或大腿多余扫描段，防止滑动窗口切分产生数千个 Patch 耗尽内存。
