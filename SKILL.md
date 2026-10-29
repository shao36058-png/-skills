---
name: hfss-et-divider
description: "面向射频与微波工程的 HFSS 矩形波导 E/H 面功分器、功率合成器、魔T与电阻隔离优化。 Inspect and tune HFSS rectangular-waveguide E/H-plane dividers and combiners, magic tees, matching irises/posts, resistive cards, coherent efficiency, input isolation, modal phase and matched-load sensitivity. Use for existing AEDT projects and offline complex-S result audits."
license: MIT
metadata:
  author: shao36058-png
  version: "0.3.0"
  domain: "Electronics Engineering / 电子工程"
  specialty: "RF and Microwave Engineering / 射频与微波工程"
  component: "Waveguide Power Dividers and Combiners / 波导功分器与合成器"
  author-suggested-soc: "17-2072"
---

# HFSS 波导功分与合成

检查并优化现有矩形波导功分器、合成器及其隔离通道。名称保留 `hfss-et-divider` 以兼容已有安装。案例的频段、端口编号、材料、路径补偿和尺寸均不是新任务的默认要求。结果解释或技能整理优先读取已有数据，无需启动 HFSS。

## 按任务读取

- E-T 对称膜片、开口/深入/厚度/位置、横臂 60 mm 与支路 30 mm：[几何与电磁约定](references/et-design.md)。
- 换 BJ140 或调谐至 13.75–14.5 GHz：[BJ140 功分案例](references/bj140-14ghz.md)。
- 效率与输入隔离、同相合成、E/H 面与补偿、端口 0 W、过模及输出渐变：[合成与隔离判断](references/combining-and-isolation.md)。
- 中央电阻膜、实体隔片、镍铬厚度、氧化铝电阻卡：[电阻隔离与加工约束](references/resistive-isolation.md)。
- 四端口魔 T、3 号沿 Z 输出、4 号沿 Y 接负载、取消输入补偿：[无补偿魔 T 完整案例](references/magic-t-14ghz.md)。
- 比较前面各轮方案或查找成功/未达标试验：[21 项案例目录](references/case-library.md)，19 个合成网络另有 [机器索引](assets/case-index.json)。
- 连接已打开 AEDT、求解、提取、保存、迁移和内存控制：[AEDT 操作与结果完整性](references/aedt-workflow.md)。

## 先核对，再调参

1. 核实会话、绝对工程路径、设计和物理接口；读取已有几何、材料、边界、端口模式、积分线、扫频及当前名义结果。相同文件名不代表同一历史结构。
2. 确定工作带宽、两路功率与相位、有效输出模式、隔离端口的实物终端、接口尺寸和加工约束。用户已明确的内容不重复询问。遵从原位修改或新建工程的选择；不强制建立副本。
3. 分开评估独立输入隔离、每端口自反射和双源相干效率。使用完整传播模矩阵计算 `b = S a`；不能把单条约 −3 dB 的 S 曲线当作总合成损耗，也不能用高效率代替高隔离。
4. 初次调参保留现有求解精度，用有限候选或有界优化覆盖全带最差指标。膜片位置、开口、厚度、柱径/位置和渐变各自有物理含义；均匀支路变长不要求全部匹配尺寸同比放大。
5. 保留已验证最好结果。仅在有具体精度疑点或用户要求时加强网格/频点验证；内存不足时先减并发并监测，不能为继续搜索反复耗尽内存。
6. 交付当前名义参数、端口/相位约定、收敛和真实扫频类型、功率去向及适用条件。按任务需要验证保存重开。清理仅限已授权候选，保留其他工程。

## 每次合成评估必须包括

- 其他端口匹配时的独立输入耦合 `Sji`、各端口 `Sii`；写清隔离正值 `−20log10|Sji|` 与负值 S 曲线的区别。
- 两路指定功率/相位下，有效输出 `|b_out|² / Σ|a_in|²`、输入返回、负载吸收、全部传播模式的输出与损耗/数值残余。
- 单路工作、相位偏差、幅度失衡、反相输入；单路关闭按匹配终端计算时须说明，实际故障功放可能失配。
- 有隔离口时检查实际负载失配的影响。0 W 波端口仍可接收功率；金属封死不是匹配负载。多模输出必须说明未利用模式的终端。
- 检查端口模式极性和参考面后解释相位。E/H 面判据来自结区电场与分支方向，馈电弯头也可改变外部同相对应的和/差通道。翻转积分线不构成物理相位补偿。

三端口、单模、无耗、互易网络无法同时实现全端口匹配和输入隔离；对称等分且公共口匹配时常见输入耦合约 −6 dB，不是所有三端口的统一极限。增设匹配差模出口或引入选择性耗散后可改善隔离。矩形金属波导开槽、加柱或加宽本身不提供差模吸收。

## 离线复核

在技能根目录执行。Python 3.10+；功分工具仅需标准库，合成工具还需 NumPy。

```bash
python scripts/divider_metrics.py --input assets/reference-case.json --max-reflection-db -25 --min-frequency-ghz 23 --max-frequency-ghz 25
python scripts/divider_metrics.py --input assets/bj140-14ghz-case.json --max-reflection-db -25 --min-frequency-ghz 13.75 --max-frequency-ghz 14.5
python scripts/combiner_metrics.py --input assets/cases/magic-t-equal-h-bends.json --output magic-t-audit.json --min-efficiency-pct 98 --min-isolation-db 24 --load-return-loss-db 20 --load-return-loss-db 30
```

功分脚本可改 `--reflection-expression`、`--output-expressions`、`--expected-phase-deg`。合成脚本读取 `channel_order`、完整 `data` 与 `audit_config`；模式标签采用 `1:1`、`3:2` 等。所有列出的通道必须是采用功率波归一化的传播模，不能直接对截止模套用 `|S|²`。每项 S 数据由等长 `real`、`imag` 数组表示。阈值失败返回非零；无定义的路径相位报告为 `null`。更多格式和负载计算说明见 [合成参考](references/combining-and-isolation.md)。

案例是历史快照，不能作为当前工程的数据。证据标签不替代原生求解与收敛记录。两项功分例分别有 21/25 个插值输出点；E-T 单臂补偿例另有 25 点离散验证；其余案例按各自来源说明。当前无补偿魔 T 的全带样点效率 98.105–99.537%、最差输入隔离 24.383 dB，条件是第 4 口理想匹配，输出自反射尚未全带低于 −20 dB。

全部案例均不构成 1 kW 连续波额定验证。功率容量须另核实圆角、真实电导率、介质与电阻损耗、接触、散热及故障负载。文献的带宽/功率结论与本案例结果分别标注；不随技能分发论文全文或 HFSS 二进制工程。
