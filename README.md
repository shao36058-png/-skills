# HFSS 波导功分与合成 Skill

用于 HFSS 矩形波导 E/H 面功分器、功率合成器、魔 T 和电阻隔离结构的检查、优化与复数 S 数据审核。保持技能名称 **`hfss-et-divider`**，版本 **0.3.0**。

本仓库只维护这一项技能。圆波导 TE₀₁ 弯头、模式转换器和定向耦合器仍在 [TE₀₁ 技能合集](https://github.com/shao36058-png/skills)。

[技能入口](SKILL.md) · [21 项历史案例](references/case-library.md) · [魔 T 完整参数](references/magic-t-14ghz.md) · [电阻材料与厚度](references/resistive-isolation.md) · [效率与隔离](references/combining-and-isolation.md) · [AEDT 操作流程](references/aedt-workflow.md)

## 本次补充

保留原有 23–25 GHz 与 BJ140 13.75–14.5 GHz 两项 E-T 功分案例，新增 19 项合成网络快照，覆盖 H-T、E-T 路径补偿、五端口、删去隔离支路、过模输出、中央电阻膜、实体片、普通镍铬、氧化铝卡和四端口魔 T。每项都有参数、终端条件、复数数据和复评结果；未达标试验也明确保留为对照。

最新方案采用等长 H 面输入弯头，**取消额外相位补偿**。两输入各 0.5 W、0°，3 口沿 Z 为和输出，4 口沿 Y 接理想匹配负载：

| 13.75–14.5 GHz 全带输出样点指标 | 结果 |
|---|---:|
| 有效输出合成效率 | 98.105–99.537% |
| 最差独立输入隔离 | 24.383 dB |
| 最差输入 S11 / S22 | −24.444 / −24.636 dB |
| 最差输出 S33 | −18.451 dB |
| 路径相位差最大绝对值 | 0.03785° |

![魔 T 无补偿布局结果](docs/magic-t-14ghz-results.svg)

上述隔离以 4 口理想匹配为条件，4 口负载回波损耗 20 dB 时，反射相位扫描下隔离可降至约 19.158 dB；输出反射也未达到全带 −20 dB。25 点是插值输出，不是 25 次独立全波求解。这些是名义电磁结果，未完成 1 kW 连续波热设计或实物认证。

## 分类与检索


**作者分类：电子工程 → 射频与微波工程 / Electronics Engineering → RF and Microwave Engineering。**

| 技能 | 器件细分 |
|---|---|
| HFSS E/H 面功分器、魔 T 与隔离合成器 | 波导无源器件 → 功率分配与合成 / Waveguide Power Dividers and Combiners |

职业参考：[Electronics Engineers, Except Computer（SOC 17-2072）](https://skillsmp.com/occupations/electronics-engineers-except-computer)。技能的 `metadata` 记录作者建议分类，`description` 提供中英文器件名称，方便识别与检索。

这些是作者维护的分类信息。SkillsMP 的职业和类别标签由平台维护；其公开文档未承诺依据这些自定义字段自动分类。本节不表示网页上的“分类待定”已解除。

## 安装与使用

使用 [skills CLI](https://github.com/vercel-labs/skills)，为 Codex 安装：

```bash
npx skills add https://github.com/shao36058-png/-skills --skill hfss-et-divider --agent codex
```

在助手中输入：

```text
使用 $hfss-et-divider 检查当前 HFSS 波导合成器。
频段 13.75–14.5 GHz，BJ140 接口，两输入等幅同相。
先核对物理端口、积分线和负载终端，读取已有结果，
同时评估输入隔离、自反射、有效合成效率与单路/失衡工况。
按当前任务要求修改工程，保留求解精度，并控制内存。
```

用户决定原位修改或新建工程；技能不强制副本。实际连接和求解需要可用的 HFSS / AEDT 自动化环境。离线脚本不连接 AEDT、不触发求解。Python 3.10+；功分脚本仅需标准库，合成脚本另需 NumPy。

## 离线复核合成网络

在仓库根目录执行：

```bash
python scripts/combiner_metrics.py --input assets/cases/magic-t-equal-h-bends.json --output magic-t-audit.json --min-efficiency-pct 98 --min-isolation-db 24 --load-return-loss-db 20 --load-return-loss-db 30
```

脚本按完整传播模矩阵 `b=S a`，独立计算输入隔离与相干效率，并输出单源、反相、幅相失衡和负载失配复评。无定义路径相位写为 null；阈值未通过返回非零。多个负载时相位扫描仅为共同相位扫描，不能称为独立负载最坏情况。输入格式和限制见 [合成与隔离](references/combining-and-isolation.md)。

[机器索引](assets/case-index.json) 对应 [案例目录](references/case-library.md)。每份 JSON 的源摘要用于追溯历史快照；历史数据不能冒充当前工程结果，离线无源检查也不能替代全波收敛。

## BJ140：13.75–14.5 GHz 原有功分案例


波导截面 **15.80 × 7.90 mm**，横臂总长 **60 mm**，输入支路从 T 结外壁到端口 **30 mm**。膜片左右对称伸入宽边方向，开口高度为 7.90 mm。

| 参数 / mm | 第一片 | 第二片 |
|---|---:|---:|
| 开口全宽 | 7.800 | 10.150 |
| 每侧深入长度 | 4.000 | 2.825 |
| 中心距 T 结外壁 | 4.230 | 14.550 |
| 沿传播方向厚度 | 0.250 | 0.250 |

| 指标 | 保存结果 |
|---|---:|
| 全带输出样点中最差输入 S22 | −28.33 dB |
| 最大反射功率 | 0.147% |
| 14 GHz 处输入 S22 | −28.62 dB |
| 14 GHz 两路传输 S12 / S32 | −3.0156 / −3.0169 dB |
| 最大两路幅度差 | 0.00133 dB |
| 相对 180° 的最大相位误差 | 0.03682° |

![BJ140 输入匹配与二路传输](docs/bj140-14ghz-results.svg)

本例修正了“换成 BJ140 截面及 14 GHz 频段后，仍沿用原 24 GHz 膜片尺寸”的强失配。沿用 ΔS=0.005 的网格收敛要求，实际完成 11 次自适应迭代，最后 ΔS=0.0026741；原生求解和插值扫频均正常完成。详细定义与证据范围见 [BJ140 案例](references/bj140-14ghz.md)。

这些结果来自**空气 / PEC 模型的 25 个插值输出样点**，不是 25 次独立离散求解，也不构成真实铜件的连续功率额定值。两路每路约 −3.01 dB 对应等分，输出在一致端口极性下相差约 180°。

## 原有功分数据复核

```bash
python scripts/divider_metrics.py --input assets/bj140-14ghz-case.json --max-reflection-db -25 --min-frequency-ghz 13.75 --max-frequency-ghz 14.5
python scripts/divider_metrics.py --input assets/reference-case.json --max-reflection-db -25 --min-frequency-ghz 23 --max-frequency-ghz 25
```

标准库脚本重新计算反射、传输、幅差、相位及功率残余，并派生膜片尺寸。更换端口编号时使用 `--reflection-expression` 和 `--output-expressions`。保留 [23–25 GHz 原案例](references/et-design.md) 和 [BJ140 完整参数](references/bj140-14ghz.md)。原有两个案例是插值输出；新增的 E-T 单臂补偿合成案例则包含 25 点离散验证，扫频证据分别记录。

## 内容与分发

- `SKILL.md`：任务路由、判断与验证要求。
- `references/`：参数、21 项案例目录、隔离与材料经验、AEDT 操作和内存控制。
- `scripts/divider_metrics.py`：标准库功分复核；`scripts/combiner_metrics.py`：NumPy 合成复核。
- `assets/`：历史复数数据、参数、来源摘要及机器索引；`docs/`：自有仿真数据图。

不分发引用论文全文、HFSS 二进制工程或完整场解。市场展示取决于平台索引，本仓库更新不代表已被 SkillsMP 重新收录或分类。许可采用 [MIT](LICENSE)。

**English:** One Agent Skill for HFSS rectangular-waveguide E/H-plane power dividers and combiners, magic tees, matching irises/posts and resistive isolation. Includes 21 historical cases, full complex modal-S combining audits, load-mismatch sensitivity and memory-aware AEDT workflows. Case results are nominal electromagnetic evidence, not a CW power rating.
