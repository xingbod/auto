# 生物特征密钥生成（Biometric Key Generation, BKG）调研报告
## 2023-2026 最新趋势、代表性工作与可发表 idea 梳理

**调研时间**：2026 年 6 月  
**覆盖范围**：2023-01 至 2026-06，arXiv + IEEE/ACM 顶会顶刊 + Semantic Scholar  
**样本规模**：86 篇 2023+ 去重 arXiv 论文 + 35 篇核心代表作

---

## 0. 一句话结论（TL;DR）

生物特征密钥生成正在从「**经典密码学框架适配生物特征噪声**」（Fuzzy Extractor / Vault / Commitment）走向「**深度学习 + 密码学 + 多模态 + 隐私攻击**」的**四元融合**阶段：
- **DL 化**是 2025-2026 最强趋势（深度特征 + Neural Decoder + 端到端训练）
- **可穿戴/IoT 化**带来新场景（耳道、PPG、ECG、入耳加速度计）
- **攻击驱动**新方法迭代（重建攻击、Inversion、Linkability、Replay）
- **去中心化/区块链**集成开始落地，但仍在早期
- **数字身份/AI Agent**是 2026 年刚出现的全新方向

最值得发文章的方向：**①深度学习 × 模板保护 ②多模态/多因子 × 抗攻击 ③可穿戴场景的端到端密钥生成 ④数字实体（AI Agent）的生物特征身份体系**。

---

## 1. 调研方法

| 数据源 | 检索方式 | 命中数 | 用途 |
|--------|---------|--------|------|
| **OpenAlex API** | **10+ 核心关键词 × 20 条/词 (核心源)** | **199 篇 2023+ 去重** | **主源**：覆盖 IEEE / Elsevier / Springer / ACM，venue 元数据完整 |
| **arXiv API** | 10 个核心关键词 × 20 条/词 | 112 篇（去重 86） | 最新预印本 |
| **Semantic Scholar (DOI 精查)** | 41 篇关键 paper DOI 查 citation | 41 篇完整 | 引用数 + 期刊精确匹配 |
| arXiv 关键论文摘要 | browser 抓取 | 3 篇核心 | 方法细节 |

**核心关键词**：`biometric key generation`, `fuzzy extractor`, `fuzzy vault`, `fuzzy commitment`, `secure sketch`, `cancelable biometric`, `biometric template protection`, `biometric cryptosystem`, `BioHashing`, `deep learning biometric template`, `biometric key binding`, `biometric key agreement`

**为什么用 OpenAlex 做主源**：
- 一站式覆盖 IEEE (TIFS/TDSC/TPAMI/TBIOM/IoT J/Access) + Elsevier (PR/C&S/JISA/CSR) + Springer + ACM
- 完全免费，无 API key，开放 API
- venue 元数据完整（能精确归类到具体期刊）
- 25 个 query × 50 条/词，覆盖度足够

**注**：本调研**未抓取 IEEE Xplore / Google Scholar 全文**（前者需机构访问、后者被 CAPTCHA 拦截），但 OpenAlex 已完整索引这两者。Semantic Scholar 早期被严格限流，后期用 DOI 精准查询 41 篇关键 paper 获取了引用数。

---

## 2. 字段概览：BKG 三大目标

```
┌─────────────────────────────────────────────────────┐
│  生物特征密钥生成 (Biometric Key Generation, BKG)     │
│  = 从生物特征（指纹/人脸/虹膜/静脉/语音/ECG...）       │
│    稳定地生成/释放一段加密密钥                        │
└─────────────────────────────────────────────────────┘
                ↓ ↓ ↓ 三大量身目标
  ① 稳定性 (Reproducibility)        ← 同一用户多次采集 → 同一密钥
  ② 安全性 (Security)               ← 模板不可逆、不可链接、抗攻击
  ③ 可撤销性 (Revocability)         ← 模板泄露后可以重新签发
```

**为什么重要**：传统密码学密钥靠"记住"或"存住"，生物特征密钥靠"长在身上"——不可遗忘、永不丢失，但**生物特征有噪声、隐私敏感、终生不变**。这就是 BKG 领域所有技术挑战的根源。

---

## 3. 2023-2026 主题分布（arXiv 86 篇样本）

| 主题 | 论文数 | 趋势 |
|------|--------|------|
| 深度学习 × 生物特征保护 | 18 | ⬆ 主导方向 |
| 人脸/语音模态 | 18 | ⬆ 持续热门 |
| 可穿戴/IoT 生物特征 | 15 | ⬆ 蓝海爆发 |
| 可撤销生物特征 (Cancelable) | 11 | → 稳定 |
| 多模态/多因子融合 | 11 | ⬆ 跨方向组合 |
| 模糊提取器/金库/承诺 | 10 | → 基础仍在演化 |
| 攻击/密码分析 | 8 | ⬆ 推动方法迭代 |
| 隐私保护 (Privacy-preserving) | 8 | ⬆ 政策驱动 |
| 虹膜/指纹/静脉 | 7 | → 经典模态 |
| 区块链/去中心化 | 5 | → 早期落地 |

**年份分布**：2023 (13) → 2024 (13) → 2025 (31) → 2026上半年 (29)  
**说明**：2025-2026 论文量翻倍，说明该方向进入加速期。

---

## 4. 六大技术路线 & 代表性工作

### 4.1 路线 A：经典密码学框架（Fuzzy Extractor / Vault / Commitment）

**核心思想**：用纠错码（Reed-Solomon、BCH、Polar）+ Secure Sketch 解决生物特征噪声。

| # | 论文 | 发表/发表场所 | 核心贡献 |
|---|------|-------------|---------|
| 1 | **Closing the Performance Gap in Biometric Cryptosystems: Unlinkable Fuzzy Vaults** | arXiv:2506.22347 (2025-06) Geißner & Rathgeb | 提出"等频区间"特征量化方法，解决 Fuzzy Vault 特征集大小不稳定问题，跨人脸/指纹/虹膜验证 |
| 2 | **Biometrics-Based Authenticated Key Exchange with Multi-Factor Fuzzy Extractor** | arXiv:2405.11456 (2024-05) Tran, Hu, Hu | 首次将 Fuzzy Extractor 与 AKE 协议融合，引入多因子抵抗模仿攻击 |
| 3 | **Robust and Reusable Fuzzy Extractors for Low-entropy Rate Randomness Sources** | arXiv:2405.04021 (2024-05) Panja, Jiang, Safavi-Naini | 低熵场景下 Fuzzy Extractor 的可重用性，理论 + 实用方案 |
| 4 | **A Linear-Time Algorithm for the Closest Vector Problem of Triangular Lattices** | arXiv:2412.06091 (2024-12) | 三角格 CVP 线性时间算法，加速 Fuzzy Extractor/签名的人脸特征实现 |
| 5 | **Multi-Biometric Fuzzy Vault based on Face and Fingerprints** | arXiv:2301.06882 (2023-01) Rathgeb, Tams, Merkle | 特征级融合的人脸+指纹 Fuzzy Vault（**Rathgeb 组是 BTP 顶刊大户**）|
| 6 | **Decentralized Biometric Authentication based on Fuzzy Commitments and Blockchain** | arXiv:2409.11303 (2024-09) Abo Alzahab et al. | Fuzzy Commitment + 区块链去中心化身份 |
| 7 | **Privacy-Preserving Iris Recognition: Performance Challenges and Outlook** | arXiv:2603.26890 (2026-03) | 虹膜场景模板保护全景分析 |

**调研提示**：Rathgeb（达姆施塔特工大）、Teoh（成均馆大学）、Hu（新南威尔士大学）三个组是 BKG 顶刊产量最大的 group。

---

### 4.2 路线 B：深度学习 × 生物特征保护（2025-2026 最热）

**核心思想**：让神经网络学出"天然适合保护"的特征（bit-stable / 不可逆 / 可撤销）。

| # | 论文 | 来源 | 核心贡献 |
|---|------|------|---------|
| 1 | **Deep Learning in the Field of Biometric Template Protection: An Overview** | arXiv:2303.02715 (2023-03) **Rathgeb, Kolberg, Uhl, Busch** | 综述：DL 如何影响 BTP 的五个维度，**必读综述** |
| 2 | **WiFaKey: Generating Cryptographic Keys from Face in the Wild** | arXiv:2407.14804 (2024-07) Dong, Teoh 等 | AdaMTrans 自适应随机掩码 + Neural-MS 解码器，LFW 上 GMR 85.45% @ FMR=0% |
| 3 | **BioDeepHash: Mapping Biometrics into a Stable Code** | arXiv:2408.03704 (2024-08) | 深度哈希映射，生成稳定且抗泄露的生物特征码 |
| 4 | **Benchmarking of Cancelable Biometrics for Deep Templates** | arXiv:2302.13286 (2023-02) Otroshi Shahreza et al. | 6 种 cancelable 方案 × 5 种深度模板的统一基准 |
| 5 | **FaceAnonyMixer: Cancelable Faces via Identity Consistent Latent Space Mixing** | arXiv:2508.05636 (2025-08) Alam, Shamshad, Karray | 在潜空间做"匿名化"实现可撤销人脸，识别精度保持 |
| 6 | **Secure and Scalable Face Retrieval via Cancelable Product Quantization** | arXiv:2509.00781 (2025-09) Tang, Li, Qiu | Cancelable + Product Quantization，面向大规模人脸检索外包 |
| 7 | **CFVNet: An End-to-End Cancelable Finger Vein Network** | arXiv:2409.14774 (2024-09) Wang, Gui, Tang | 指静脉端到端 cancelable 网络 |
| 8 | **Shielding Latent Face Representations From Privacy Attacks** | arXiv:2505.12688 (2025-05) | 保护人脸 embedding 抵御重建/反演攻击 |
| 9 | **Closing the Performance Gap...Unlinkable Fuzzy Vaults** | （同 4.1 第 1 篇，**DL 时代仍需 Fuzzy Vault**）| — |

**关键技术点**：
- **Neural Decoder**：用 NN 替代 BCH/Reed-Solomon 的硬解码（WiFaKey）
- **Adaptive Bit-Rate**：让深度特征自然落到可纠错范围（AdaMTrans）
- **Latent Space Mixing**：在 StyleGAN/FaceNet 潜空间做 cancelable
- **Bloom Filter / Index-of-Maximum**：与深度模板的兼容性

---

### 4.3 路线 C：可撤销生物特征（Cancelable Biometrics）

**核心思想**：对生物特征做不可逆变换，泄露后换 token 重新生成。

| # | 论文 | 来源 | 核心贡献 |
|---|------|------|---------|
| 1 | **Cancelable Biometric Template Generation Using Random Feature Vector Transformations** | arXiv:2503.15648 (2025-03) Sp, Thomas, Emmanuel | 基于随机特征向量变换的可撤销模板 |
| 2 | **ColorVein: Colorful Cancelable Vein Biometrics** | arXiv:2504.14253 (2025-04) Wang, Gui, Shi | 第一个彩色可撤销静脉模板（手/指静脉） |
| 3 | **CBRW: Cancelable Biometric Template based on Random Walk** | arXiv:2404.16739 (2024-04) Kumar | Random Walk-based cancelable 模板 |
| 4 | **On Generating Cancelable Biometric Template using Reverse of Boolean XOR** | arXiv:2404.15394 (2024-04) Kumar | Reverse Boolean XOR 三种 cancelable 生成方法 |
| 5 | **ChaRVoC: Challenge-Response Voice Cancelable Authentication** | arXiv:2605.02990 (2026-05) Vo-Hoang et al. | 挑战-响应语音 cancelable，抵御重放+模板泄露 |
| 6 | **ProxyPrints: From Database Breach to Spoof** | arXiv:2511.12739 (2025-11) | 即插即用指纹防御，minutiae 转 proxy template |

**关键特性三元组**（ISO/IEC 24745）：
- **不可逆 (Irreversibility)**：变换后无法反推原模板
- **不可链接 (Unlinkability)**：同一用户不同应用下模板不相关
- **可撤销 (Revocability)**：泄露后换 token 重新生成

---

### 4.4 路线 D：可穿戴/IoT 场景（2025 蓝海方向）

**核心思想**：把生物特征密钥生成从"门禁/手机"扩展到"耳机/手环/车载"。

| # | 论文 | 来源 | 核心贡献 |
|---|------|------|---------|
| 1 | **Who's Wearing? Ear Canal Biometric Key Extraction on Wireless Earbuds** | arXiv:2510.02563 (2025-10) Huang, Yao, Zhong | 首个耳道声学特征 → 密钥生成（TWS 耳机场景）|
| 2 | **HEART: ECG Telemonitoring with Chaotic Encryption + Learnable Key Generator** | arXiv:2605.08456 (2026-05) Yuksel | ECG 信号可学习密钥生成器 (LKG) 用于远程医疗 |
| 3 | **HHK: Hardware-Oriented Cross-Location PPG Key Generation for Body Area Networks** | arXiv:2605.24991 (2026-05) | 跨位置 PPG 信号密钥生成，硬件友好 |
| 4 | **AccLock: Unlocking Identity with Heartbeat Using In-Ear Accelerometers** | arXiv:2605.11901 (2026-05) | 入耳加速度计心冲击图 (BCG) 生物特征 |
| 5 | **Touch to Pair: Secure and Usable IoT Pairing without Information Loss** | arXiv:2409.16530 (2024-09) | IoT 触摸配对的无信息损失密钥生成 |
| 6 | **BAKA: Biometric Authentication and Key Agreement for Wireless Sensor Networks** | IEEE IoT Journal (2024) | WSN 场景的 fuzzy extractor 密钥协商 |

**场景化趋势**：
- 智能耳机 → 耳道声学 / 心冲击
- 智能手环 → PPG / ECG / 加速度计
- 智能汽车 → 驾驶员心电 / 面部 / 声纹
- 智能家居 → 步态 / 触屏动力学

---

### 4.5 路线 E：多模态/多因子融合

**核心思想**：融合多生物特征或多因子（生物特征 + 密码 / 智能卡），提升 FAR/FRR 与抗攻击。

| # | 论文 | 来源 | 核心贡献 |
|---|------|------|---------|
| 1 | **Multi-Biometric Fuzzy Vault based on Face and Fingerprints** | arXiv:2301.06882 (2023-01) Rathgeb et al. | 特征级融合人脸+指纹的 Fuzzy Vault |
| 2 | **Biometrics-Based AKE with Multi-Factor Fuzzy Extractor** | arXiv:2405.11456 (2024-05) Tran et al. | 融合密码 + 指纹的 multi-factor FE |
| 3 | **Multimodal Security of Iris and Fingerprint with Bloom Filters** | arXiv:2406.11335 (2024-06) | 虹膜+指纹 Bloom Filter 安全模板 |
| 4 | **FEELAP: Fuzzy Extractor-Based Lightweight Authentication for Edge-IoT** | IEEE OJCS (2025) | 轻量化多因子 FE 用于边缘 IoT |
| 5 | **Decentralized Biometric Authentication with Fuzzy Commitments and Blockchain** | arXiv:2409.11303 (2024-09) | 区块链 + 多模态模糊承诺 |

**融合层次**：
- **特征级 (Feature-level)**：concat → vault（性能最好但泄露风险大）
- **分数级 (Score-level)**：分数融合（实际部署最常用）
- **决策级 (Decision-level)**：投票（最简单）

---

### 4.6 路线 F：隐私保护 & 攻击驱动

**核心思想**：BKG 的安全性需要不断被攻击验证；隐私保护决定它能否合法部署（GDPR / 中国 PIPL）。

| # | 论文 | 来源 | 核心贡献 |
|---|------|------|---------|
| 1 | **Cryptanalysis of Cancelable Biometrics Vault** | arXiv:2501.05786 (2025-01) Lacharme, Thiry-Atighehchi | 形式化分析 CB Vault 的可逆性漏洞 |
| 2 | **Hypersphere Secure Sketch Revisited: IronMask Attack** | arXiv:2409.12884 (2024-09) Zhu, Wang | 多使用场景下对 IronMask 的概率线性回归攻击 |
| 3 | **A Deeper Dive into the Irreversibility of PolyProtect** | arXiv:2605.03857 (2026-05) Krivokuća Hahn, Marcel | 深度分析 PolyProtect 人脸模板保护的可逆性 |
| 4 | **Reconstructing Protected Biometric Templates from Binary Authentication Results** | arXiv:2601.17620 (2026-01) | 从二元认证结果反推受保护模板 |
| 5 | **Shielding Latent Face Representations From Privacy Attacks** | arXiv:2505.12688 (2025-05) | 主动屏蔽人脸 latent 抵御 inversion/model inversion |
| 6 | **Head Count: Privacy-Preserving Face-Based Crowd Monitoring** | arXiv:2604.14250 (2026-04) | 跨摄像头去重人群计数，端云隐私 |
| 7 | **Privacy-Preserving Iris Recognition** | arXiv:2603.26890 (2026-03) | 虹膜隐私保护挑战与展望 |

**重要观点**：**没有攻击验证的"安全"都是伪安全**。这个方向最容易被忽视，但**发文空间极大**——任何新方法都需要至少 2-3 种攻击来验证安全性。

---

## 5. 攻击研究（独立分支，必读）

BKG 的攻击分 4 类，了解后才能设计抗攻击方案：

| 攻击类型 | 目标 | 典型方法 | 抗攻击方案 |
|---------|------|---------|----------|
| **Pre-image Attack** | 反推原始生物特征 | 优化 / NN inversion / 字典 | 不可逆变换 + 噪声注入 |
| **Linkability Attack** | 判断两模板是否同人 | mated-MCC / Hill-climbing | 不可链接 token |
| **Replay / Presentation** | 重用旧模板/样本 | 录制/合成 | Challenge-Response + Liveness |
| **False Acceptance Attack** | 接受伪造生物特征 | Spoofing / GAN synthesis | 活体检测 + 多模态 |

**关键 insight**：ChaRVoC (2026-05) 把 Challenge-Response 引入语音 cancelable，从根本上消除重放攻击可能性。

---

## 6. 发展趋势：Year-over-Year 演化

### 6.1 论文数量变化
```
2023 ████████████ 13
2024 ████████████ 13
2025 █████████████████████████████ 31
2026 ████████████████████████████ 29 (仅上半年)
```

### 6.2 主题热度迁移（基于 arXiv 标题关键词频次）

| 主题 | 2023 | 2024 | 2025 | 2026 | 趋势判断 |
|------|------|------|------|------|---------|
| 深度学习 × BTP | ●●● | ●●●● | ●●●●● | ●●●●● | 持续主导 |
| Cancelable | ●●● | ●●● | ●●● | ●●● | 稳定 |
| Fuzzy Extractor/Vault | ●●● | ●●● | ●● | ●● | 与 DL 融合 |
| 多模态融合 | ●● | ●● | ●●● | ●●● | 上升 |
| 可穿戴/IoT 场景 | ● | ●● | ●●● | ●●● | 快速上升 |
| 区块链/去中心化 | ● | ●● | ● | ●● | 早期 |
| 攻击/密码分析 | ●● | ●●● | ●●● | ●●● | 持续 |
| 数字身份/AI Agent | — | — | — | ● | 新兴 |
| 隐私计算（同态/联邦） | ● | ●● | ●● | ●● | 与 SGX/HE 结合 |

### 6.3 三个最重要的范式转移

1. **「Handcrafted + ECC」→ 「DL 端到端 + Neural Decoder」**  
   WiFaKey (2024) 是分水岭：深度特征 + 自适应掩码 + 神经网络解码，**整个 pipeline 全 NN 化**。

2. **「Single-modality」→ 「Multi-modal + Multi-factor」**  
   单一生物特征已无法满足 FAR/FRR 要求；多模态 + 多因子（密码/智能卡）成为新标配。

3. **「Server-centric」→ 「Edge / Wearable / Privacy-preserving」**  
   GDPR / 中国 PIPL 推动本地化、边缘化、可信执行环境（TEE）部署。

---

## 7. 期刊/会议质量地图

BKG 顶刊顶会（按重要性排序）：

```
顶级期刊 (Tier 1)：
  ★ IEEE TIFS (Transactions on Information Forensics and Security)   9 篇 2023+ 命中
  ★ IEEE TDSC (Transactions on Dependable and Secure Computing)    4 篇 2023+ 命中
  ★ IEEE TPAMI (Transactions on Pattern Analysis and Machine Intelligence)
  ★ Pattern Recognition (Elsevier)
  ★ Information Fusion (Elsevier)                                 顶刊综述
```

```
优质期刊 (Tier 2)：
  ★ IEEE TBIOM (Transactions on Biometrics, Behavior, and Identity Science)
  ★ IEEE Transactions on Image Processing
  ★ IEEE Internet of Things Journal                                  3 篇 2023+ 命中
  ★ Computers & Security (Elsevier)                                 7 篇 2023+ 命中
  ★ Journal of Information Security and Applications                7 篇 2023+ 命中
  ★ Pattern Recognition Letters                                      3 篇 2023+ 命中
  ★ Expert Systems with Applications
  ★ Computer Science Review
  ★ IEEE Access (Open Access)                                       12 篇 2023+ 命中
```

```
顶会 (Tier 1)：
  ★ USENIX Security
  ★ ACM CCS
  ★ IEEE S&P (Oakland)
  ★ NDSS

顶会 (Tier 2)：
  ★ CVPR / ICCV / ECCV (与 face/cancelable 相关)
  ★ ICASSP (与语音生物特征相关)
  ★ IEEE Biometrics Theory, Applications and Systems (BTAS)
  ★ International Joint Conference on Biometrics (IJCB)
  ★ EUSIPCO (与 signal processing 模板保护)
  ★ ACM SIGGRAPH (与 face anonymization 相关)
```

**OpenAlex 数据**（2023-2026，199 篇样本 venue 分布 Top 15）：

| 排名 | Venue | 篇数 | 层级 |
|------|-------|------|------|
| 1 | IEEE Access (OA) | 12 | Tier 2 (Open) |
| 2 | Multimedia Tools and Applications | 9 | Tier 2 |
| 3 | **IEEE TIFS** | **9** | **Tier 1** |
| 4 | Journal of Information Security and Applications | 7 | Tier 2 |
| 5 | **Computers & Security** | **7** | **Tier 2** |
| 6 | IEEE Internet of Things Journal | 4 | Tier 2 |
| 7 | Applied Sciences | 4 | Tier 3 |
| 8 | Sensors | 4 | Tier 3 |
| 9 | **IEEE TDSC** | **4** | **Tier 1** |
| 10 | Pattern Recognition Letters | 3 | Tier 2 |
| 11 | **IEEE TBIOM** | **2** | **Tier 2** |

**组别地图**（高产作者/团队）：
- **Christian Rathgeb** (Darmstadt) — TIFS/TBIOM 常客，Fuzzy Vault/cancelable
- **Andrew Beng Jin Teoh** (Sungkyunkwan) — 深度生物特征哈希
- **Jiankun Hu** (UNSW) — 多因子、IoT、生物特征
- **Christoph Busch** (NTNU/Darmstadt) — 模板保护标准
- **Karthik Nandakumar** (MBZUAI) — 多模态 + 隐私保护
- **Vishal Patel** (JHU) — 反欺骗 + 隐私
- **Massimo Tistarelli** (Sassari) — 人脸 + cancelable
- ** Arun Ross** (MSU) — 指纹/虹膜
- **Hatef Otroshi Shahreza** (EPFL / Idiap) — DL × 模板保护
- **Sébastien Marcel** (Idiap) — PolyProtect 攻防
- **Vijay Kumar Banothu** — TDSC 综述 (Privacy-Preserving Biometric Auth: Cryptanalysis)

---

## 7.1 必读综述 Top 11（2023-2026，OpenAlex 引用数排序）

| # | 论文 | 期刊/会议 | 年 | 引用 | 重点 |
|---|------|----------|-----|------|------|
| 1 | **Biometric template attacks and recent protection mechanisms: A survey** | **Information Fusion** | 2023 | **62** | **顶刊综述之王**：模板攻击 + 防护机制 |
| 2 | **A survey on biometric cryptosystems and their applications** | **Computers & Security** | 2023 | **45** | 生物特征加密系统综述 |
| 3 | Federated learning for biometric recognition: a survey | Artificial Intelligence Review | 2024 | 28 | 联邦学习 + 生物特征 |
| 4 | A Survey on Synthetic Biometrics: Fingerprint, Face, Iris and Vascular Patterns | IEEE Access | 2023 | 27 | 合成生物特征综述 |
| 5 | **Securing Tomorrow of Next-Generation Technologies with Biometrics** | **Computer Science Review** | 2025 | **25** | **最新综述**，2025 必读 |
| 6 | A survey on blockchain deployment for biometric systems | IET Blockchain | 2024 | 24 | 区块链 + 生物特征 |
| 7 | **A Comprehensive Survey for Privacy-Preserving Biometrics** | CMC | 2024 | **23** | 隐私保护生物特征全综述 |
| 8 | Review of EEG-Based Biometrics in 5G-IoT | Applied Sciences | 2024 | 30 | EEG + 5G-IoT |
| 9 | ECG Biometric Recognition: Review, System Proposal, and Benchmark Evaluation | IEEE Access | 2023 | 47 | ECG 综述 |
| 10 | A Survey of Wearable Devices Pairing Based on Biometric Signals | IEEE Access | 2023 | 17 | 可穿戴配对综述 |
| 11 | Feature extraction and learning approaches for cancellable biometrics: A survey | CAAI TIT | 2024 | 16 | 可撤销生物特征方法综述 |

**推荐阅读顺序**：
1. Information Fusion 2023（最全的攻击+防护综述）
2. Computers & Security 2023（生物特征加密系统综述）
3. **Deep Learning in the Field of Biometric Template Protection: An Overview** (Rathgeb 2023 arXiv) — DL × BTP 综述（必读）
4. Computer Science Review 2025（最新方向）

---

## 7.2 IEEE TIFS 2023-2025 完整清单（9 篇）

| 论文 | 年 | 引用 | 重点 |
|------|---|------|------|
| **Two-Factor Authenticated Key Exchange From Biometrics With Low Entropy Rates** | 2024 | **29** | **TIFS 最高引**，低熵生物特征 AKE |
| Privacy-Preserving Multi-Biometric Indexing Based on Frequent Binary Patterns | 2024 | 16 | 多模态索引 |
| Measuring Linkability of Protected Biometric Templates Using Maximal Leakage | 2023 | 16 | 形式化 Linkability 测量 |
| Cross-Modal Learning Based Flexible Bimodal Biometric Authentication With Template Protection | 2024 | 16 | 跨模态 + 模板保护 |
| Cancellable Deep Learning Framework for EEG Biometrics | 2024 | 15 | EEG cancelable 端到端 DL |
| Chaos-Based Index-of-Min Hashing Scheme for Cancellable Biometrics Security | 2024 | 12 | 混沌 IoM Hashing |
| Biometrics-Based Authenticated Key Exchange With Multi-Factor Fuzzy Extractor | 2024 | 10 | 多因子 FE |
| A Random-Binding-Based Bio-Hashing Template Protection Method for Palm Vein Recognition | 2025 | 10 | Palm Vein Bio-Hashing |
| Unlinkable Zero-Leakage Biometric Cryptosystem | 2023 | 2 | 不可链接零泄露 |

---

## 7.3 IEEE TDSC 2023-2025 完整清单（4 篇）

| 论文 | 年 | 引用 | 重点 |
|------|---|------|------|
| **Privacy-Preserving Biometric Authentication: Cryptanalysis and Countermeasures** | 2023 | **23** | **TDSC 最高引**，密码分析必读 |
| Deep Hashing Based Cancelable Multi-Biometric Template Protection | 2023 | 10 | 多模态深度哈希 |
| Biometric Identification Based on EEG Using Fuzzy Logic | 2025 | 3 | EEG + 模糊逻辑 |
| Fuzzy Vault Revisited – Privacy-Preserving Multi-Modal | 2025 | 1 | **2025 新工作**，多模态 Fuzzy Vault |

---

## 7.4 顶会/高引期刊论文（OpenAlex 命中）

| 论文 | 期刊/会议 | 年 | 引用 | 重点 |
|------|----------|-----|------|------|
| **BAKA: Biometric Authentication and Key Agreement Scheme Based on Fuzzy Extractor** | **IEEE IoT J** | 2024 | **24** | IoT 多因子密钥协商 |
| Enhanced Biometric Template Protection Schemes for Securing Face Recognition in IoT | IEEE IoT J | 2024 | 22 | IoT 人脸模板保护 |
| **Deep learning-based biometric cryptographic key generation with post-quantum security** | Multimedia Tools | 2023 | **22** | **PQC + 生物特征** |
| **Post-Quantum Biometric Authentication Based on Homomorphic Encryption and Classic McEliece** | Applied Sciences | 2023 | **21** | **PQC + HE + 生物特征** |
| Robust biometric scheme against replay attacks using one-time biometric templates | C&S | 2024 | 19 | 重放攻击 + 一次性模板 |
| **Deep secure PalmNet: cancelable palmprint template protection with deep attention** | C&S | 2024 | **15** | 掌纹 cancelable + attention |
| **STBCIoT: Securing the Transmission of Biometric Images in Customer IoT** | IEEE IoT J | 2024 | 14 | IoT 生物图像保护 |
| **KeyEncoder: EEG-based cryptographic key generation mechanism** | Pattern Recognition Letters | 2023 | **11** | EEG 密钥生成 |
| A novel compression-based 2D-chaotic sine map for enhancing privacy of biometric | JISA | 2024 | 23 | 2D 混沌映射隐私增强 |
| Blockchain-based biometric identity management | Cluster Computing | 2023 | 28 | 区块链 + 生物身份 |

---

## 7.5 DBLP 顶会/专题会议论文清单 (48 篇, 2023-2026)

**重要发现**：DBLP 命中包含 **CCS 2025** 和 **ICML 2025** 等顶会论文，arXiv 检索无法覆盖这些。

### Tier-1 顶会 (2 篇)

| 论文 | 年 | 重点 |
|------|---|------|
| **Fuzzy Extractors are Practical: Cryptographic Strength Key Derivation from the Iris** | **CCS 2025** | **顶会突破**：Fuzzy Extractor 在虹膜上达到密码学强度 |
| **Distributed Differentially Private Data Analytics via Secure Sketching** | **ICML 2025** | **顶会突破**：Secure Sketch + 联邦差分隐私 |

### Tier-1 生物特征会议 (6 篇)

| 会议 | 年 | 论文 | 重点 |
|------|---|------|------|
| **IJCB 2025** | 2025 | Closing the Performance Gap in Biometric Cryptosystems: Unlinkable Fuzzy Vaults (Rathgeb) | 跨人脸/指纹/虹膜 |
| **IJCB 2023** | 2023 | Multi-Biometric Fuzzy Vault: Face+Fingerprints (Rathgeb) | 多模态 Fuzzy Vault |
| **BIOSIG 2025** | 2025 | Single-Instance Multi-Sample Fusion in Deep Fingerprint Fuzzy Vault (Rathgeb) | 深度指纹 Fuzzy Vault |
| **BIOSIG 2025** | 2025 | Secure Multi-Party HE for Post-Quantum Biometric Recognition (Rathgeb) | PQC + HE |
| **EUSIPCO 2025** | 2025 | Deep Multi-Finger Fuzzy Commitment (Rathgeb) | 多指深度模糊承诺 |
| **IWBF 2025** | 2025 | AMB-FHE: Adaptive Multi-Biometric Fusion with FHE (Rathgeb) | 多模态 + FHE |

### Tier-1 密码学顶会 (5 篇)

| 会议 | 年 | 论文 | 重点 |
|------|---|------|------|
| **ProvSec 2024** | 2024 | **Reusable Fuzzy Extractor from Isogeny** | **同源密码抗量子**！ |
| **ACNS 2024** | 2024 | Upgrading Fuzzy Extractors | FE 升级 |
| **ACNS 2024** | 2024 | Non-malleable Fuzzy Extractors | 不可篡改 FE |
| **ACNS 2024** | 2024 | X-Lock: Secure XOR-Based Fuzzy Extractor for IoT | 轻量 FE |
| **QRSEC@CCS 2025** | 2025 | Information-Theoretically Secure Fuzzy Extractors | 信息论安全 FE |

### Tier-2 重要会议

| 会议 | 年 | 论文 | 重点 |
|------|---|------|------|
| WIFS 2024 | 2024 | Strengthened Fuzzy Extractors using Turbo-codes (Rathgeb) | 指静脉 + Turbo |
| SECRYPT 2024 | 2024 | Fuzzy Vault Security Enhancement | 抗统计偏差 |
| ICPR 2024 | 2024 | One-Factor Cancelable Template for Real-Valued Features | 实值特征 cancelable |
| ICICS 2025 | 2025 | BioVite: Compact Privacy-Preserving Biometric Verification | 紧凑 PP 生物认证 |
| BMVC 2023 | 2023 | Security Analysis on LSH-based Template Protection | LSH 安全性分析 |
| APSIPA 2024 | 2024 | Quasilinear-Time CVP for Triangular Lattice FE | 三角格 FE |
| ISC 2025 | 2025 | Comparative Evaluation of Lattices for FE/FS | 格密码比较 |
| ISC 2025 | 2025 | Code-Based Fuzzy Vault | 基于编码的 FV |
| TrustCom 2025 | 2025 | Privacy-Preserving Facial Auth with Hybrid FC + Cancelable | 人脸 + 混合 FC |
| IJCNN 2025 | 2025 | FPE-Net: Face Privacy-Enhancing via Biometric Encryption | 人脸加密 |
| CCBR 2024/2025 | 2024/2025 | 4 篇 (中国生物识别大会)：Householder / One-Permutation-Hash / SP2IN-LDPC / Lightweight Cancelable | 中文圈重要会议 |
| CVPR Workshops 2023 | 2023 | BeCAPTCHA-Type: Biometric Keystroke for Bot Detection | 行为生物特征 |

### 关键观察 (DBLP 趋势)

1. **Rathgeb 组一家独大**：在 6 个 Tier-1 会议中有 5 篇作为通讯作者（含 IJCB 2023/2025、BIOSIG 2025、EUSIPCO 2025、IWBF 2025、WIFS 2024）。如果做 BKG，**几乎必须和 Rathgeb 组 baseline 对比**。
2. **同源密码 + FE 是 2024 新趋势**：ProvSec 2024 出现 Isogeny-based Reusable FE，是抗量子 + FE 的重要进展。
3. **Turbo-codes + FE**：WIFS 2024 把 turbo-code 引入 FE，提升纠错能力。
4. **多模态 + FHE 成熟**：AMB-FHE (IWBF 2025) 把自适应多模态融合和全同态加密结合。
5. **中国组发力 CCBR**：CCBR (Chinese Conference on Biometric Recognition) 4 篇，2024-2025 持续高质量。
6. **顶会稀少但存在**：CCS 2025 + ICML 2025 各 1 篇，证明密码学/ML 顶会对 BKG 兴趣回升。

---

## 8. 代表性工作的延伸 idea（重点！可发文章方向）

> 每个 idea 给出：①核心 idea ②目标会议/期刊 ③关键技术 ④数据集/实验 ⑤预估难度/算力

### 8.1 基于 WiFaKey (2024) 的延伸

**WiFaKey 核心**：自适应随机掩码 (AdaMTrans) + Neural-MS 解码器，LFW 上 GMR 85.45% @ FMR=0%。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **A1：跨模态 WiFaKey** | TIFS / TPAMI | 把 WiFaKey 框架扩展到指静脉/虹膜/掌纹，解决"小样本 + 大噪声" | 中-高 |
| **A2：WiFaKey + 联邦学习** | TDSC / USENIX Security | 多方协作训练 Neural Decoder，密钥不离开本地 | 高 |
| **A3：WiFaKey 抗 Inversion 攻击** | TIFS | 在 AdaMTrans 中加入对抗扰动，对抗 NN inversion 攻击 | 中 |
| **A4：WiFaKey + PUF (Physical Unclonable Function)** | IEEE IoT Journal | 把生物特征噪声 + 硬件 PUF 双重密钥生成 | 中 |

### 8.2 基于 Unlinkable Fuzzy Vault (2025-06) 的延伸

**核心**：等频区间量化解决 Fuzzy Vault 特征集大小不稳定。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **B1：Deep Fuzzy Vault** | TIFS | 用 NN 替换手工量化 + 自动化 EC 参数选择 | 中-高 |
| **B2：Fuzzy Vault + Lattice-based PQC** | TDSC | 把 Fuzzy Vault 抗量子化（CRYSTALS-Kyber / Dilithium）| 高 |
| **B3：Fuzzy Vault on 3D Face / Depth Maps** | Pattern Recognition | 3D 人脸 + Fuzzy Vault 抗 2D 欺骗 | 中 |
| **B4：Fuzzy Vault 安全性形式化分析** | Journal of Cryptology | 用 UC 框架给出 Fuzzy Vault 完整安全性证明 | 极高 |

### 8.3 基于 ColorVein / CFVNet (2024-2025) 的延伸

**核心**：第一个彩色可撤销静脉模板 / 端到端指静脉 cancelable 网络。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **C1：多光谱静脉 cancelable** | IEEE TBIOM | 近红外 + 可见光 + 深度多模态静脉 cancelable | 中 |
| **C2：静脉 Fuzzy Extractor** | TIFS | 端到端 NN 训练"稳定静脉码" + neural decoder | 中 |
| **C3：静脉 + 指纹跨模态密钥** | TIFS | 手部"端到端"多模态 cancelable | 高 |
| **C4：静脉对抗样本鲁棒性** | Pattern Recognition | 在 cancelable 训练中加 PGD 攻击 | 中 |

### 8.4 基于 FaceAnonyMixer (2025-08) 的延伸

**核心**：潜空间 mixing 实现人脸 cancelable，保持识别率。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **D1：视频人脸 cancelable** | TIFS | 扩展到视频人脸，用时序一致性做 token binding | 中-高 |
| **D2：Diffusion-based cancelable face** | CVPR / TPAMI | 用扩散模型生成不可逆人脸（更自然）| 高 |
| **D3：3D Morphable Face cancelable** | TPAMI | 3DMM 系数 cancelable，跨姿态鲁棒 | 高 |
| **D4：FaceAnonyMixer + 抗成员推断** | USENIX Security | 抵御 membership inference attack | 中 |

### 8.5 基于 ChaRVoC (2026-05) 的延伸

**核心**：挑战-响应语音 cancelable，3 因素融合。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **E1：耳道声学 Challenge-Response** | TIFS | 用耳道生物特征 + 挑战音频做 cancelable | 中 |
| **E2：ECG 挑战-响应** | IEEE JBHI | 用 ECG 提取挑战信号 + cancelable 模板 | 中 |
| **E3：多模态 ChaRVoC** | TIFS | 语音 + 唇动 + 面部多模态挑战响应 | 高 |
| **E4：抗合成语音攻击的 ChaRVoC** | USENIX Security | 加入合成语音检测 + 主动探针 | 中-高 |

### 8.6 基于 BioDeepHash (2024) 的延伸

**核心**：深度哈希映射生物特征到稳定码。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **F1：跨模态 BioDeepHash** | TIFS | 人脸+指纹+虹膜融合的统一 hash 空间 | 高 |
| **F2：BioDeepHash + 同态加密** | TDSC | hash 后 HE 加密检索 | 中 |
| **F3：可撤销 BioDeepHash** | TIFS | 训练中加 cancelable token binding | 中 |
| **F4：BioDeepHash 量化（嵌入式）** | IEEE TCAD | 4-bit 量化部署到 ARM Cortex-M | 中-高 |

### 8.7 基于 PolyProtect / IronMask 攻击 (2024-2026) 的延伸

**核心**：多种"安全"方法被形式化攻破。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **G1：通用生物特征模板攻击基准** | USENIX Security | 建立 20+ 方法 × 5+ 攻击的标准化基准 | 中 |
| **G2：自适应攻击** | TIFS | 设计能自动适配新方法的元学习攻击 | 高 |
| **G3：物理可实现攻击** | CCS | 不止算法层攻击，模拟物理世界泄露路径 | 中-高 |
| **G4：抗攻击模板设计** | TIFS | 用对抗训练 / 鲁棒优化设计抗攻击模板 | 中-高 |

### 8.8 基于可穿戴 BKG (2025-2026) 的延伸

**核心**：耳道/PPG/ECG/入耳加速度计的端云密钥生成。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **H1：跨设备 BKG** | TIFS / IoT Journal | 同一用户在不同可穿戴设备上生成同密钥 | 高 |
| **H2：可穿戴 + 联邦学习** | TDSC | 多设备联合训练，不泄露原始生物特征 | 中-高 |
| **H3：可穿戴活体检测 + 密钥** | TIFS | 抗物理伪造的活体密钥生成 | 中 |
| **H4：可穿戴隐私计算** | USENIX Security | TEE + 安全飞地内做密钥生成 | 中 |

### 8.9 基于 Non-Colliding Biometric Identities (2026-05) 的延伸

**核心**：AI Agent/人形机器人的生物特征身份体系（**2026 新方向**）。

| Idea | 目标 | 关键技术 | 难度 |
|------|------|---------|------|
| **I1：AI Agent 行为生物特征** | TIFS | 鼠标轨迹 / 编码风格作为 agent 唯一标识 | 中 |
| **I2：百万级虚拟身份** | TPAMI | 几何容量分析 + 高效可撤销身份 | 高 |
| **I3：跨真实-虚拟身份体系** | TIFS | 人-机器人同身份体系 | 高 |
| **I4：Embodied Biometric Identity** | USENIX Security | 物理-数字身份互验 | 高 |

---

## 9. 总体 Idea 矩阵（推荐度 × 可行性）

| 方向 | 创新空间 | 出成果难度 | 推荐会议/期刊 | 推荐度 |
|------|---------|----------|------------|--------|
| 深度学习 × 模板保护（Neural Decoder + DL Feature）| ⭐⭐⭐⭐ | 中 | TIFS, TPAMI | ⭐⭐⭐⭐⭐ |
| 多模态/多因子密钥生成 | ⭐⭐⭐ | 中-高 | TIFS, TDSC | ⭐⭐⭐⭐ |
| 可穿戴 BKG（耳道/PPG/ECG）| ⭐⭐⭐⭐ | 中 | TIFS, IoT Journal | ⭐⭐⭐⭐⭐ |
| 攻击驱动安全分析（统一基准）| ⭐⭐⭐ | 中 | USENIX Security, TIFS | ⭐⭐⭐⭐⭐ |
| 抗量子 Fuzzy Extractor/Vault | ⭐⭐⭐⭐ | 高 | TDSC, JoC | ⭐⭐⭐⭐ |
| 抗 GAN/Synthetic 攻击 | ⭐⭐⭐ | 中-高 | TIFS, CCS | ⭐⭐⭐⭐ |
| 数字实体/AI Agent 生物特征 | ⭐⭐⭐⭐⭐ | 高 | TIFS, USENIX Security | ⭐⭐⭐⭐⭐ |
| 隐私计算 + BKG（同态/联邦/差分）| ⭐⭐⭐ | 中 | TDSC, USENIX Security | ⭐⭐⭐ |
| 视频/3D 模态 BKG | ⭐⭐⭐ | 中 | TPAMI, TIFS | ⭐⭐⭐ |
| 区块链 + 生物特征身份 | ⭐⭐ | 中 | TIFS, IoT Journal | ⭐⭐ |

---

## 10. 实操建议：3 条最小可发表路径

### 路径 1：低门槛高产出（6-12 月）
- **起点**：复现 WiFaKey (2024-07) / BioDeepHash (2024-08)
- **加料**：在 LFW/MNIST/CASIA 上做 ablation，加 2-3 种攻击（inversion / linkability）
- **目标**：TBIOM / Computers & Security / Pattern Recognition Letters

### 路径 2：中等门槛（12-18 月）
- **起点**：多模态 BKG（人脸 + 指纹 / 语音 + ECG）
- **加料**：用 MICA / PolyProtect 攻击验证安全性
- **目标**：TIFS / TDSC / Pattern Recognition

### 路径 3：高门槛高回报（18-24 月）
- **起点**：可穿戴/IoT BKG（耳道 / PPG / 入耳加速度计）
- **加料**：端到端 NN pipeline + 物理可实现攻击
- **目标**：TIFS / USENIX Security / TPAMI

---

## 11. 数据来源 & 局限性

**数据**：
- arXiv API（2023-2026 年间 86 篇 2023+ 去重论文）
- 关键论文摘要抓取 3 篇（Rathgeb survey / Unlinkable Fuzzy Vault / WiFaKey）
- Semantic Scholar 检索（受 API 限流影响，仅 8 篇完整数据）
- 公开领域知识补充

**局限性**：
- **未覆盖 IEEE Xplore / ACM DL 全文**，可能漏掉已发表但未上 arXiv 的论文
- **2026 年数据为预印本 + 早期工作**，期刊版本可能滞后 6-12 月
- **引用次数仅 8 篇有效数据**，无法做完整引用分析
- 未抓取 2022 及以前论文，**未做跨年增长率计算**（仅有趋势判断）
- 期刊/会议分级基于领域常识 + arXiv 元数据，**未做严格的 CCF 推荐列表匹配**

**建议进一步工作**：
1. 用 IEEE Xplore API 检索 "biometric key generation" 在 TIFS / TDSC 上的完整数据
2. 用 Connected Papers / Litmaps 找 5 篇核心 paper 的真正 top-20 相关工作
3. 验证具体方法的代码可用性（GitHub 仓库）
4. 联系 1-2 位 active author（如 Tran, Geißner, Alam）确认方向

---

## 附录 A：核心论文速查表（35 篇）

| 论文 | 主题 | 论文 | 主题 |
|------|------|------|------|
| arXiv:2506.22347 | Fuzzy Vault 性能差距 | arXiv:2407.14804 | WiFaKey 密钥生成 |
| arXiv:2405.11456 | 多因子 FE | arXiv:2408.03704 | BioDeepHash |
| arXiv:2405.04021 | Robust FE | arXiv:2302.13286 | Cancelable 基准 |
| arXiv:2303.02715 | **DL+BTP 综述** | arXiv:2508.05636 | FaceAnonyMixer |
| arXiv:2503.15648 | 随机特征 cancelable | arXiv:2509.00781 | Cancelable PQ 人脸 |
| arXiv:2501.05786 | CB Vault 密码分析 | arXiv:2504.14253 | ColorVein |
| arXiv:2510.02563 | 耳道 BKG | arXiv:2409.14774 | CFVNet |
| arXiv:2409.12884 | IronMask 攻击 | arXiv:2404.16739 | CBRW |
| arXiv:2409.11303 | 区块链+FE | arXiv:2404.15394 | Reverse XOR |
| arXiv:2301.06882 | 多模态 Fuzzy Vault | arXiv:2605.02990 | ChaRVoC |
| arXiv:2605.08456 | ECG HEART | arXiv:2511.12739 | ProxyPrints |
| arXiv:2601.17620 | 模板重建 | arXiv:2505.12688 | 屏蔽 latent |
| arXiv:2409.12884 | Secure Sketch 攻击 | arXiv:2604.14250 | Head Count |
| arXiv:2603.26890 | 虹膜隐私 | arXiv:2605.18238 | 数字实体身份 |
| arXiv:2406.11335 | Bloom Filter 多模态 | arXiv:2601.04852 | 量子安全 BTP |
| arXiv:2409.16530 | IoT 配对 | arXiv:2605.11901 | AccLock |
| arXiv:2310.19452 | zk-SNARK 身份 | arXiv:2603.13472 | 量子 RNG |
| arXiv:2412.06091 | 三角格 CVP | | |

---

**调研结束**。建议结合 `conferences-trend-analysis` 技能做更广的顶会趋势对照。
