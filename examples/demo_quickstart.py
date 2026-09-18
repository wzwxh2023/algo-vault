#!/usr/bin/env python3
"""
demo_quickstart.py - TFActProfiler 最小端到端可运行示例脚本
展示如何准备输入数据、推断转录因子活性并评估可靠性置信度。
"""

import sys

def main():
    print("=== TFActProfiler Quickstart Recipe ===")
    print("Dependencies: pip install scanpy decoupler tfactprofiler pandas\n")
    
    recipe = '''
import scanpy as sc
import decoupler as dc
import tfactprofiler as tfp
import pandas as pd

# 1. 准备单细胞表达矩阵 (必须 log1p 标准化)
adata = dc.ds.pbmc3k()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=3000)

# 2. 读取官方带符号调控先验权重表 (三列: source, target, weight)
# 下载源: https://raw.githubusercontent.com/HikaruSugimoto/tfactprofiler/main/example/TFactprofiler_all.csv
prior_net = pd.read_csv("TFactprofiler_all.csv")

# 3. 运行 ULM 模型推断单细胞 TF 活性
dc.mt.ulm(data=adata, net=prior_net)
tf_scores = dc.pp.get_obsm(adata, key="score_ulm")
print("TF Activity matrix shape:", tf_scores.shape)

# 4. 计算推断可靠性 MSE (写入 adata.obs['mse'])
adata = tfp.estimate_reliability(adata, prior_net, cluster_key="celltype")
print("Top 5 cells reliability (MSE):", adata.obs["mse"].head())
'''
    print(recipe)

if __name__ == "__main__":
    main()
