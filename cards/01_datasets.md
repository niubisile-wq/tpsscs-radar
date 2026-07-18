# Dataset Card

## 当前候选数据

| Dataset | Role | Access | Status | Notes |
|---|---|---|---|---|
| AISTAP-SIM | 主训练/主验证 | Public GitHub | Confirmed | 公开、可下载、适合作为主定量数据 |
| RASPNet public CVNN/EXAMPLES | 外部泛化 | Public subset | Confirmed | 只使用即时可下载部分，不依赖完整 16TB |
| IPIX sea clutter | 真实海杂波 | Public web page | Needs download check | 作为真实目标/海杂波验证数据 |
| NetRAD sea clutter | 真实海杂波外部验证 | UCL repository | Confirmed | 适合作为双基地/单基地泛化验证 |

## 必做审计字段

每个数据源必须记录：

- 下载 URL
- 访问日期
- 文件名列表
- 总大小
- 校验 hash
- 许可协议
- 标签类型
- 是否存在目标真值
- 是否需要目标注入

## 处理原则

- 统一转成复值张量。
- 所有 split 固定并落盘。
- 所有 target injection 参数固定并保存。
- 不允许训练集和测试集共享同一 recording 或同一目标轨迹。

