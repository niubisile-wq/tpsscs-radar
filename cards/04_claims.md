# Claims Card

## 论文主张

1. 公开雷达数据上，复值自监督与物理约束结合的杂波抑制方法可以在保留弱目标的同时压低杂波，但必须显式控制目标损失。
2. 论文主问题不是纯粹的杂波消除，而是低虚警操作点下的目标保持与检测稳定性。
3. 在公开 AISTAP sample 上，`k=20` 虽然把 clutter attenuation 提高到 `11.268 dB`，但 target loss 也升到 `13.906 dB`，说明单纯增大低秩压制会过抑制弱目标。
4. 在低 `Pfa` 约束下，方法需要优于 raw RD 和低秩残差 baseline，且不能以过度抑制弱目标为代价。
5. 该方法应在跨数据集条件下保持可迁移性，而不是只记住单一场景。
6. 公开基准 OpenClutter-Bench 可以让结果可复现、可扩展、可审计。

## 不允许写成的主张

- first ever
- universal
- comprehensive
- solves all radar clutter problems
- one model fits every radar scene
