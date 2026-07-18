# Scope Card

问题定义：

- 输入：公开雷达复值回波或其 range-Doppler / space-Doppler 表示。
- 输出：杂波抑制后的表示、检测统计量、低虚警阈值下的目标判定。
- 目标：在强杂波、弱目标、有限标签和跨场景条件下，尽量保持目标同时压低 false alarm。

主线数据范围：

- AISTAP-SIM
- RASPNet public CVNN / EXAMPLES subset
- IPIX sea clutter
- NetRAD monostatic / bistatic sea clutter

排除项：

- 不把需要申请授权、邮件审批或不可重复获取的数据作为主实验依赖。
- 不把 NEXRAD 或 RadarScenes 纳入当前主线，除非后续明确拆成独立论文。

顶刊约束：

- 不能只在一个数据集上证明有效。
- 不能只给可视化，不给低虚警量化。
- 不能只给方法结构，不给消融和泛化。

