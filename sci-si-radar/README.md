# SCI 期刊特刊雷达 (SCI Special Issue Radar)

> 每天凌晨 3:00 自动扫描 SCI 期刊的特刊 (Special Issue / Research Topic / Topical Collection) call for paper,主题限定 计算机视觉 / 医学人工智能 / 图像处理,结果通过邮件发送。

## 抓取策略

cron LLM 用 `browser` 工具硬抓 5 大出版商,**每源独立失败重试 2 次**;Frontiers 完整兜底。

> ⚠️ **网络现实**: MDPI/Elsevier/IEEE/Wiley 都对 Headless Chrome 做了反爬。
> - `MDPI`: Akamai 锁,失败率约 50-60%
> - `Elsevier`: HeadlessChrome 检测,失败率约 40-50%
> - `IEEE Xplore`: Error 418 (Unusual Traffic),失败率约 60-70%
> - `Wiley`: Akamai 锁,失败率约 50-60%
> - `Frontiers`: 100% 成功(列表 JS,详情 server-rendered)
>
> **接受部分失败**: 单源失败就跳过该源,最终发邮件时明确标注"哪些源今日未抓到"。

## 目标期刊清单 (12 本核心)

### MDPI (5 本,命中率最高,黄金区期刊)
| 期刊 | ISSN | 2yr IF (近似) | 备注 |
|---|---|---|---|
| Sensors | 1424-8220 | 4.7 | 计算机视觉 + 医学传感 + 图像处理 |
| Applied Sciences | 2076-3417 | 2.7 | 应用导向,涵盖 CV/AI/Image |
| J. Imaging | 2313-433X | 3.0 | 纯图像期刊 |
| Diagnostics | 2075-4418 | 3.6 | 医学诊断 + 医学 AI/影像 |
| Electronics | 2079-9292 | 2.9 | 含 CV/image processing section |

### Elsevier (3 本,顶刊)
| 期刊 | ISSN | IF | 备注 |
|---|---|---|---|
| Pattern Recognition | 0031-3203 | 8.0 | CV/模式识别旗舰 |
| Medical Image Analysis | 1361-8415 | 10.0 | 医学影像顶刊 |
| Computer Vision and Image Understanding | 1077-3142 | 4.3 | CV 经典期刊 |

### Springer (2 本)
| 期刊 | ISSN | IF | 备注 |
|---|---|---|---|
| International Journal of Computer Vision | 0920-5691 | 7.0 | CV 顶刊(IJCV) |
| Machine Vision and Applications | 0932-8092 | 2.4 | 应用导向 |

### IEEE (1 本)
| 期刊 | ISSN | IF | 备注 |
|---|---|---|---|
| IEEE Access | 2169-3536 | 3.4 | 多学科,IF 高,开放 |

### Wiley (1 本)
| 期刊 | ISSN | IF | 备注 |
|---|---|---|---|
| International Journal of Imaging Systems and Technology | 0899-9457 | 2.0 | 医学/工业成像 |

### Frontiers (兜底,10 本,100% 抓到)
| 期刊 | RT 数量级 |
|---|---|
| computer-science | 300+ |
| artificial-intelligence | 200+ |
| imaging | 100+ |
| radiology | 80+ |
| neuroimaging | 60+ |
| neuroscience | 200+ |
| human-neuroscience | 80+ |
| medicine | 200+ |
| signal-processing | 60+ |
| medical-engineering | 50+ |

合计:12 主流 SCI 期刊 + 10 Frontiers 期刊 = **22 个数据源**。

## URL 模式 (LLM browser 直接用)

```
MDPI:        https://www.mdpi.com/journal/{slug}/special_issues
Elsevier:    https://www.sciencedirect.com/journal/{slug}/special-issues
Springer:    https://link.springer.com/journal/{issn}/special-issues
IEEE:        https://ieeeaccess.ieee.org/special-sections/
Wiley:       https://onlinelibrary.wiley.com/journal/{issn}/homepage/for-authors.html
Frontiers:   https://www.frontiersin.org/journals/{slug}/research-topics
```

## 项目结构

```
~/auto/sci-si-radar/
├── README.md             # 本文件
├── index.html            # GitHub Pages 历史汇总(每日追加)
├── archive/
│   └── YYYY-MM-DD.md     # 每日 Markdown 完整记录
└── data/
    └── rt-cache.json     # 抓取的 RT 缓存(7 天内复用)
```

## 邮件发送

- 收件人: 717608039@qq.com
- 工具: `himalaya message send` (走 clawtoken@163.com SMTP)
- 主题: `SCI 特刊雷达 · YYYY-MM-DD`
- 格式: HTML 邮件(左 border 颜色编码优先级,绿/黄/红/灰)

## 触发

cron job `0 3 * * *` (CST 凌晨 3 点)。

## 评分维度

每条候选按 4 维打分(总分 100):

| 维度 | 权重 | 标准 |
|---|---|---|
| 主题匹配 | 50% | 强=3 关键词同时命中 / 中=2 命中 / 弱=1 命中 |
| Deadline 余量 | 25% | > 90 天 满分 / 30-90 天 80% / 14-30 天 50% / < 14 天 20% |
| 期刊质量 | 15% | IF ≥ 5 满分 / 3-5 80% / 2-3 60% / < 2 30% |
| 主题热度 | 10% | views / 文章数 / 影响力 |

## GitHub Pages

`index.html` 自动构建,公开访问:
https://www.drdongai.com/auto/sci-si-radar/

## 维护

- 改 cron: `hermes cron update <job_id> --prompt "..."`
- 调试: `hermes cron run <job_id>` 立即跑一次
- 增/删目标期刊: 编辑本 README,然后让 cron LLM 重读
