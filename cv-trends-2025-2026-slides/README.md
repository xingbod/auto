# 2025-2026 顶会最热方向 · Slides & 报告

CVPR · ICCV · ECCV · BMVC 全量论文分析。

## 文件说明

```
cv-trends-2025-2026-slides/
├── index.html               # 主 slides（97 张，单文件，浏览器直接打开）
├── report.md                # 中文综合报告（22KB，深度分析）
├── README.md                # 本文件
└── data/
    ├── topic_stats_cvpr.json       # CVPR 2024/2025/2026 主题统计
    ├── topic_stats_eccv_iccv.json  # ECCV 2024 + ICCV 2025 主题统计
    └── cvpr25_best_arxiv.json      # CVPR 2025 best paper arXiv 信息
```

## 如何使用

### 打开 slides

```bash
# macOS
open cv-trends-2025-2026-slides/index.html

# Linux
xdg-open cv-trends-2025-2026-slides/index.html

# 或者直接拖到浏览器
```

### 演讲操作

- `←` / `→`  翻页（前/后）
- `Space`      下一页
- `Home`       跳到封面
- `End`        跳到 Q&A
- `P`          打印为 PDF（适合分享）

## 调研规模

- **数据规模**：18,798 篇 accepted papers
- **会议覆盖**：CVPR 2024/2025/2026, ICCV 2025, ECCV 2018-2024, BMVC 2025
- **主题聚类**：45 个预定义方向 + 关键词匹配
- **交叉验证**：CVPR 2025 best paper 命中我们识别的 5/7 个爆款方向

## 内容结构

```
1. 封面 + 目录 + 研究方法           4 张
2. Top 15 方向一览                 1 张
3. 15 个方向详述                   90 张
   - 方向概览 + 4 个数字格         15 张
   - 代表论文详情（2 篇/方向）      30 张
   - 论文延伸机会（4 idea/篇）     30 张
   - 方向级展望 + 资源 + 算力      15 张
4. 终极建议矩阵 + ECCV 2026 预测   2 张
5. Q&A                            1 张
                                ───────
                                 97 张
```

## 关键发现

**CVPR 2026 爆款方向（增长率 100%+）**：

| 方向 | CVPR 24 | CVPR 25 | CVPR 26 | 增长 |
|------|---------|---------|---------|------|
| 视觉推理/Agent/CoT | 16 | 42 | 160 | +281% |
| RLHF/偏好对齐 | 42 | 78 | 172 | +121% |
| 机器人/VLA/具身 | 53 | 81 | 176 | +117% |
| 多模态大模型 MLLM | 37 | 111 | 230 | +107% |
| World Models | 5 | 22 | 45 | +105% |
| 4D/动态场景 | 42 | 60 | 117 | +95% |

**最易出成果方向（综合推荐）**：

- 🟢 **强烈推荐**：视觉推理/Agent、World Models、个性化生成、RLHF+GRPO、机器人/VLA
- 🟡 **稳赚不赔**：3DGS 应用、视频生成、自动驾驶、医学影像
- 🔴 **谨慎入场**：纯 Diffusion、基础 Mamba、NeRF、光流/图像匹配

## 报告作者

Hermes Agent · 2026-06-21
