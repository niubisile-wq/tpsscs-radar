# AISTAP 第三批3 vs 配电网 / 锂电池论文全面对比审计

Date: 2026-07-15

## 0. 结论先行

按“中科院一区 Top / 高影响力工程论文”的实验标准看，`第三批3 / AISTAP` 现在已经达到**可冲一区 Top 的实验证据门槛**，并且在三者中是目前**实验强度、外部验证质量、低误警任务契合度和方法闭环最强**的一篇。

但需要区分两个层级：

- **实验是否完成**：完成。第三批3已经通过自动 top-readiness 自检，硬失败为 0，并完成 AISTAP-SIM、IPIX、SSDD 三类任务证据。
- **是否等于可以直接投稿**：还不等于。第三批3的实验已经够强，但稿件还需要把 SSDD/IPIX 的方法、图表、限制性声明和主文叙事整合进去。
- **是否已经超过配电网和锂电池两篇**：按实验论证强度和顶刊冲击力，第三批3现在排第一；按稿件交付成熟度，锂电池仍排第一；按可复现基线干净程度，配电网论文较稳但顶刊冲击力最低。

综合排序：

| 维度 | 第三批3 / AISTAP | 锂电池故障检测 | 配电网 / power_se |
|---|---:|---:|---:|
| 一区 Top 实验证据强度 | 1 | 2 | 3 |
| 方法新颖性与任务锋利度 | 1 | 2 | 3 |
| 外部验证对主张的支撑 | 1 | 2 | 3 |
| 稿件/投稿包成熟度 | 3 | 1 | 2 |
| 边界声明与风险控制 | 2 | 1 | 2 |
| 当前优先投稿价值 | 1 | 2 | 3 |

最终判断：**第三批3现在已经达到一区 Top 的实验标准，但还需要一次稿件级整合才能达到“可直接投”的标准。**

## 1. 对比对象与边界

主对比对象：

| 论文 | 本地证据位置 | 本次评估边界 |
|---|---|---|
| 第三批3 / AISTAP | `C:\Users\刘子轩\Desktop\第三批3` | 以 2026-07-15 top-readiness 自检、外部验证日志和完成审计为准 |
| 配电网 / power_se | `C:\Users\刘子轩\Desktop\power_se` | 以 IEEE feeder state-estimation 基线、缩放审计和投稿包为准 |
| 锂电池故障检测 | `C:\Users\刘子轩\Desktop\已完成项目\锂电池故障检测论文` | 以电池外部验证 one-pager、cross-source matrix、submission package validation 为准 |

补充边界：锂电池项目文件夹中还包含 `DISTRIBUTION_NETWORK_*` 配电网稿件。若“配电网”指这份稿件而不是 `power_se`，它的结论是：投稿包更干净、边界审计更完整，但顶刊冲击力仍弱于第三批3，外部验证强度也弱于锂电池主稿。

## 2. 核心证据对比

### 2.1 第三批3 / AISTAP

当前状态：

- `aistap_top_readiness_self_check_20260715.md` 判定：`top_ready`。
- 硬失败：0。
- 外部方法验证：通过。
- 本地参考论文优势门：通过。
- 完成审计判定：实验目标已完成，剩余主要是稿件整合，不是硬实验阻塞。

主要实验链：

- AISTAP-SIM 官方 full assets：`simMed_test.mat`、`simWind_test.mat`，共 210 个含目标 full-asset items。
- AISTAP-SIM detector protocol：在 `simMed_test` 上 105 个含目标样本，7/7 个 Pfa 点胜过 raw 和 low-rank。
- IPIX 外部验证：14 个 Dartmouth weak-target CDF，1 个开发集、1 个验证集、12 个 held-out test；residual-aware fusion 在 12 个 held-out recordings 上 7/7 Pfa 点胜 raw 和 low-rank。
- IPIX 关键数值：Pfa=1e-2 时 fusion Pd 0.1374，raw 0.0972，low-rank 0.0096。
- SSDD 外部验证：官方 SSDD SAR ship 数据集，test 231 images / 545 ship annotations；trainable gate 在官方测试集上对 raw 为 4/7 胜 + 3/7 平 + 0 负，对 low-rank 为 7/7 胜。
- SSDD 关键数值：Pfa=1e-2 时 gate Pd 0.7469，raw 0.5284。

最强点：

- 任务高度聚焦：低误警、弱目标保持、强杂波背景下检测。
- 外部验证不是泛泛换数据，而是同一雷达/SAR任务族内的外源任务压力测试。
- 有明确负结果边界：IPIX zero-shot 仍为负，SSDD 是监督 trainable-gate adaptation，不把它夸大成 zero-shot。

主要风险：

- SSDD 结果强，但属于监督外部适配，不是保存态 zero-shot 迁移。
- IPIX 的 zero-shot 原始分支仍不能作为正面主张，只能主张验证选择后的 residual-aware fusion。
- 稿件层面仍需把新实验写入主文、图表、方法和限制性声明。

### 2.2 锂电池故障检测

当前状态：

- `BATTERY_SUBMISSION_PACKAGE_VALIDATION_20260713.json`：`missing_count: 0`。
- `DUAL_MANUSCRIPT_DELIVERY_VALIDATION_20260713.json`：`overall_passed: true`。
- 本地材料显示：锂电池稿件是该完成项目中更强的 Nature-subjournal / 高影响力候选。

主要实验链：

- Mendeley EV fault dataset fallback：能跑通 smoke / pipeline / distribution-shift probe；pilot AUROC 约 0.8583 到 0.9349，但该源偏 synthetic/MATLAB generated，主要作为次级验证。
- Beihang real-fleet archive：已完成 workbook-level 结构、来源、标签语义索引；Fig.3e source-data benchmark macro F1 0.9029。
- 2026 millions-scale open archive：恢复 94,551 个有效 top-level prefix；一维 conservative prefix baseline AUROC 0.9820、AUPRC 0.6234、balanced accuracy 0.9584；七特征 summary AUROC 0.9866、AUPRC 0.6885、balanced accuracy 0.9544。
- 处理集关键数值：271 samples、28 features；multiclass accuracy 0.9446、balanced accuracy 0.8754、macro F1 0.8643；binary AUROC 0.9985、AUPRC 0.9972、TPR@FPR<=0.05 为 0.9880。
- CH-BatteryGen：20,489 files、500 VINs、LFP/NCM、故障类型/严重度/故障单体标注；fault-type macro F1 约 0.768，severity 约 0.395。
- Cross-source transfer 显示真实分布偏移：Mendeley -> 2026 archive AUROC 0.4291，TPR@FPR<=0.05 为 0；2026 archive -> Mendeley AUROC 0.8339，TPR@FPR<=0.05 为 0.4414。

最强点：

- 投稿包和验证包最成熟，机器检查缺失为 0。
- 外源数据层级多，尤其真实车队/大规模开放归档对审稿人更有说服力。
- 对数据源局限、恢复状态、跨源不可替代性有较强边界纪律。

主要风险：

- Beihang `GIS/<folder> -> ID` 精确绑定仍缺失。
- 2026 archive 是恢复/过滤后的可用版本，不是完整 pristine turnkey 数据。
- CH-BatteryGen 是 AI-generated benchmark derived from real-world NEV data，更适合做注释审计或辅助验证，不宜作为最强主证据。

### 2.3 配电网 / power_se

当前状态：

- 可复现 IEEE feeder state-estimation 对比包已经成型。
- manuscript-facing comparison stack、submission package、figure/table final pack 均存在。
- `m0_feasibility_gate.py` 可运行。

主要实验链：

- Feeder WLS-SE finite errors：
  - `case33bw-dist33`：RMSE_vm 0.688 mpu，RMSE_va 0.0063 deg。
  - `IEEE30`：RMSE_vm 58.300 mpu，RMSE_va 1.9015 deg，是明确异常点。
  - `IEEE118`：RMSE_vm 4.898 mpu，RMSE_va 0.1039 deg。
- GN reference baseline on `case33bw`：RMSE_vm 1.613 mpu，RMSE_va 0.0783 deg。
- DNN-SE baselines：
  - `case33bw`：0.759 / 0.0175。
  - `case118`：0.325 / 0.2703。
  - `case57`：0.735 / 0.1805。
  - `cigre_mv`：0.633 / 0.0475。
  - `mv_oberrhein`：0.431 / 0.0319。
- complex-vs-real shift check：complex 2178 params vs real 4356；shifted RMSE_vm 3.355 vs 3.334，real 略好。
- DNN scale check：bus count 与 RMSE_vm Pearson -0.773，与 RMSE_va 0.172；说明 feeder-dependent，不支持 size-monotone 强结论。

最强点：

- 可复现性和基线审计扎实。
- 主张边界相对清楚，不强行宣称 universal winner。
- 图表包、投稿说明、claim matrix 较完整。

主要风险：

- 顶刊冲击力偏弱，更像“可靠基线 + 缩放审计 + 工程比较”，不是强科学发现。
- IEEE30 异常点会被审稿人追问。
- 外部验证深度不足，主要仍在 feeder/cached benchmark 内部闭环。

## 3. 逐维度排名

| 维度 | 第一 | 第二 | 第三 | 判断理由 |
|---|---|---|---|---|
| 方法新颖性 | AISTAP | 锂电池 | 配电网 | AISTAP 的低误警目标保持 + residual/gate 分支最贴近明确科学问题；锂电池有跨源车队验证但方法冲击略弱；配电网偏基线审计 |
| 主张锋利度 | AISTAP | 锂电池 | 配电网 | AISTAP 主张可以收束为“强杂波低误警目标保持”；锂电池主张可收束为“跨源电池故障检测”；配电网主张更偏工程比较 |
| 外部验证质量 | AISTAP | 锂电池 | 配电网 | AISTAP 的 IPIX + SSDD 对雷达/SAR任务非常贴题；锂电池外源数量和规模强，但部分源存在恢复/绑定限制；配电网外部性较弱 |
| 原始数据规模 | 锂电池 | AISTAP | 配电网 | 锂电池有 94,551 prefix、20,489 files、500 VINs 等规模优势；AISTAP 的规模较小但任务针对性更强 |
| 低误警/风险敏感指标 | AISTAP | 锂电池 | 配电网 | AISTAP 直接围绕 Pfa/Pd；锂电池有 TPR@FPR<=0.05；配电网风险指标不是主线 |
| 可复现性 | 锂电池 | 配电网 | AISTAP | 锂电池和配电网投稿包更成熟；AISTAP 新增 SSDD/IPIX 后实验完成，但稿件包还需整合 |
| 稿件成熟度 | 锂电池 | 配电网 | AISTAP | 锂电池 validation missing_count 0；配电网已有 final draft/figure pack；AISTAP 当前强在实验完成，不是最终稿完成 |
| 边界声明 | 锂电池 | AISTAP | 配电网 | 锂电池对数据绑定、恢复归档、跨源失败写得最完整；AISTAP 已明确 IPIX zero-shot 和 SSDD supervised adaptation；配电网边界清楚但问题规模较低 |
| 审稿风险 | AISTAP/锂电池接近 | AISTAP/锂电池接近 | 配电网 | AISTAP 风险是稿件整合和外部适配表述；锂电池风险是源数据绑定/恢复状态；配电网风险是顶刊重要性不足 |

## 4. 按 Nature-style / 一区 Top 评估轴对比

### 4.1 Originality

- AISTAP：强。主张集中在弱目标、强杂波、低误警条件下的目标保持与检测增强，且有多外源任务支撑。
- 锂电池：中强。跨源电池故障检测和真实车队归档支撑较好，但需要更明确地区分“模型新颖性”与“验证体系新颖性”。
- 配电网：中。更像严谨工程比较和状态估计基线审计，原创科学问题不够锋利。

排序：AISTAP > 锂电池 > 配电网。

### 4.2 Scientific importance / significance

- AISTAP：强。低误警雷达检测直接关联实际感知可靠性，SSDD/IPIX 增强后能支撑更广泛雷达/SAR读者兴趣。
- 锂电池：强。新能源车电池安全和故障检测具有明确工程与社会价值，真实车队数据提高重要性。
- 配电网：中。电力系统状态估计重要，但当前结果更像方法/基线稳定性分析，缺少足够强的跨场景突破。

排序：AISTAP ≈ 锂电池 > 配电网。

### 4.3 Interdisciplinary readership

- AISTAP：中强。雷达、SAR、遥感、鲁棒检测、低误警感知系统读者会关心；需要在稿件中把“为什么不是只对雷达小圈子有用”写清楚。
- 锂电池：强。电池安全、车队运维、机器学习可靠性、能源系统读者都容易理解价值。
- 配电网：中。主要吸引电力系统和状态估计读者，跨学科外溢较弱。

排序：锂电池 > AISTAP > 配电网。

### 4.4 Technical soundness

- AISTAP：目前最强。AISTAP-SIM full assets、IPIX held-out、SSDD official test 形成了主张闭环；硬失败为 0。
- 锂电池：强。多源验证成熟，但 Beihang 精确绑定和 2026 archive 完整性是技术审稿风险。
- 配电网：中强。可复现性好，但 IEEE30 outlier 和外部验证不足限制了强结论。

排序：AISTAP > 锂电池 > 配电网。

### 4.5 Readability / manuscript readiness

- AISTAP：实验材料强，但需要重写结果主线、外部验证段落和限制性声明。
- 锂电池：最成熟，投稿包和验证包已经最接近可交付状态。
- 配电网：较成熟，已有 final draft、submission note、figure/table pack。

排序：锂电池 > 配电网 > AISTAP。

## 5. 是否达到中科院一区 Top 标准

### 第三批3 / AISTAP

判断：**达到实验标准，尚需稿件整合。**

理由：

- 已经不是“只有内部数据”的状态。
- IPIX 和 SSDD 提供了外部雷达/SAR任务族证据。
- 低 Pfa/Pd 指标贴合真实雷达检测的高风险操作点。
- 自检通过且硬失败为 0。
- 与本地配电网、锂电池参考包相比，实验主张更锋利，外部验证对核心 claim 的支撑更直接。

不宜写成：

- “所有外源 zero-shot 均成功”。
- “SSDD 证明保存态模型可无监督迁移”。
- “IPIX 原始 zero-shot 分支成功”。

应写成：

- “AISTAP-SIM saved-state / protocol establishes in-domain target-preserving low-Pfa gains.”
- “IPIX held-out validation supports residual-aware fusion after validation selection.”
- “SSDD official test supports supervised trainable-gate adaptation on an external SAR ship benchmark.”

### 锂电池故障检测

判断：**达到高水平投稿包标准，一区 Top 竞争力强，但实验风险主要在数据源可追溯性。**

理由：

- 稿件包成熟度最高。
- 多外源验证和真实车队归档支撑强。
- Cross-source transfer 负结果反而增强了真实分布偏移的可信度。

限制：

- Beihang 精确绑定缺失会影响可审计性。
- 2026 archive 不是 pristine 全量数据，会被严格审稿人追问。

### 配电网 / power_se

判断：**达到稳健工程论文/基线审计标准，但单独冲一区 Top 的科学突破性不足。**

理由：

- 可复现、边界清楚、图表和包成熟。
- 但没有足够强的外部验证或跨场景突破。
- IEEE30 outlier 会削弱“广泛有效”叙事。

## 6. 最终建议

优先级建议：

| 优先级 | 论文 | 建议 |
|---:|---|---|
| 1 | 第三批3 / AISTAP | 作为当前最值得冲一区 Top 的主稿推进；下一步应集中做稿件整合、图表重排、claim matrix 同步和 limitations 写法 |
| 2 | 锂电池故障检测 | 作为成熟度最高的备份/并行高水平稿件；重点处理数据源可追溯性和 archive 恢复边界 |
| 3 | 配电网 / power_se | 适合稳妥投稿或作为方法/基线审计稿；若要冲 Top，需要新增更强外部场景或更明确原创机制 |

一句话结论：

**第三批3现在已经超过配电网和锂电池两篇的“实验冲击力”，达到中科院一区 Top 的实验门槛；但锂电池仍是投稿包成熟度最高的一篇。第三批3下一步不是继续补实验，而是把新增 IPIX/SSDD 证据写进主文并做成可投版本。**

