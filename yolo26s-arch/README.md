# YOLO26s 架构图 · Detection 与 Segmentation 双版本

数据源: Ultralytics 官方 `yolo26.yaml` / `yolo26-seg.yaml` + arXiv:2606.03748

## 文件清单

| 文件 | 用途 | 尺寸 |
| :--- | :--- | :--- |
| **Detection 版本（YOLO26s · 9.5M）** | | |
| `yolo26s-det-architecture.html` | **主文件**,浏览器打开最佳 | 单文件 15KB |
| `yolo26s-det-architecture.jpg` | 位图,适合邮件/PPT | 1720×2191 (376KB) |
| `yolo26s-det-architecture.png` | 位图 1x 备选 | 1.2MB |
| **Segmentation 版本（YOLO26s-seg · 11.5M）** | | |
| `yolo26s-seg-architecture.html` | **主文件**,浏览器打开最佳(Google Fonts 加载) | 单文件 38KB |
| `yolo26s-seg-architecture.svg` | 矢量,可直接拖到 PowerPoint/Keynote | 30KB |
| `yolo26s-seg-architecture.png` | 位图 1x,普通使用 | 1480×1180 (182KB) |
| `yolo26s-seg-architecture@2x.png` | **位图 2x,贴论文/PPT 推荐** | 2960×2360 (462KB) |
| `yolo26s-seg-architecture.pdf` | PDF 中转,亦可直接用 | 28KB |

## 架构总览（detection 版）

```
INPUT 640×640×3
    ↓
BACKBONE  (Conv Stem + C3k2 × 6 + SPPF)
    ├── P2/4  (128ch, 160×160) ──┐
    ├── P3/8  (256ch, 80×80)   ──┤
    ├── P4/16 (512ch, 40×40)   ──┤
    └── P5/32 (1024ch, 20×20)  ──┘
                    ↓
NECK (FPN top-down + PAN bottom-up)
    ├── P3'' (256ch) ─┐
    ├── P4'' (512ch) ─┼─→ HEAD
    └── P5'' (1024ch) ┘
                    ↓
HEAD · Detect26 (Dual-Head)
    ├── One-to-One (默认, NMS-free e2e) → (N, 300, 6)
    └── One-to-Many (辅助, 需 NMS)      → (N, nc+4, 8400)
```

## 性能 (YOLO26s · detection)

- 参数量: 9.5 M
- FLOPs: 20.7 B
- 推理: T4 TensorRT 2.5ms · CPU ONNX 87.2ms
- 准确率: 48.6 mAP (COCO val2017) · 47.8 mAP (e2e)

## 架构总览（segmentation 版）

```
INPUT 640×640×3
    ↓
BACKBONE  (C3k2 + C2PSA + SPPF)
    ├── P3/8 tap ──┐
    ├── P4/16 tap ─┤
    └── P5/32 tap ─┘
                    ↓
NECK (PANet · FPN top-down + PAN bottom-up)
    ├── P3 out (256ch) ─┐
    ├── P4 out (512ch) ─┼─→ HEAD
    └── P5 out (1024ch) ┘
                    ↓
HEAD · Segment26
    ├── Box regression (DFL-free, reg_max=1)
    ├── Classification (BCE, Task-Aligned)
    ├── Mask coefficients (32-dim)
    ├── Proto module (P3/P4/P5 multi-scale → 256ch × 640×640)
    ├── Semantic seg aux loss
    └── Dual detection head
        ├── 1-to-1 (NMS-free e2e, default) → (N, 300, 6)
        └── 1-to-Many (auxiliary, NMS)     → (N, nc+4, 8400)
```

## 关键创新 (YOLO26 vs YOLO11)
- **DFL-free 回归**: 取消 Distribution Focal Loss,简化 head 和 export
- **NMS-free e2e**: 默认推理路径无 NMS,部署更简单
- **MuSGD 优化器**: SGD + Muon 混合,LLM 训练思想迁移
- **Progressive Loss**: 训练重心从辅助头→推理头
- **STAL**: 小目标正样本覆盖增强(细胞任务关键)
- **Up-proto 多尺度**: P3/P4/P5 融合 → 更高 mask 质量

## 性能 (YOLO26s-seg)

- 参数量: 11.5M (s scale)
- FLOPs: 37.4 G
- 推理: T4 TensorRT 2.5ms · CPU ONNX 87ms
- 准确率 (vs YOLO11): +2.5 box AP · +3.7 mask AP (COCO)

## 适用性 (细胞分割)

- STAL + Sem loss 对小目标/密集细胞友好
- DFL-free 简化部署(显微镜硬件 / 边缘设备)
- NMS-free e2e 减少后处理 → 实时分析
- 多尺度 Proto 适合不同尺寸细胞(2-200px 共存)
- CPU ONNX 比 YOLO11n 快 43% (YOLO26n 参考值)

## 重新生成

```bash
# 1. 提取 SVG
python3 -c "import re; html=open('yolo26s-seg-architecture.html').read(); svg=re.search(r'(<svg[\\s\\S]*?</svg>)', html).group(1); open('yolo26s-seg-architecture.svg','w').write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\\n'+svg)"

# 2. SVG → PDF (svglib)
python3 -c "from svglib.svglib import svg2rlg; from reportlab.graphics import renderPDF; renderPDF.drawToFile(svg2rlg('yolo26s-seg-architecture.svg'), 'yolo26s-seg-architecture.pdf')"

# 3. PDF → PNG (sips)
sips -s format png --resampleHeightWidthMax 2960 yolo26s-seg-architecture.pdf --out yolo26s-seg-architecture@2x.png
```

## 同步到 Windows 桌面

macOS 生成目录: `/Users/dxb/auto/yolo26s-arch/`
Windows 目标目录: `C:\Users\dongdongyang\Desktop\细胞分割任务\`

由于 Hermes Agent 运行在 macOS,无法直接写入 Windows 盘符。同步方式:
- OneDrive / Dropbox / iCloud 同步(把目录加进云盘)
- 微信/邮件发送给自己
- U 盘拷贝

---

DONG XINGBO · YOLO26s-seg architecture for cell segmentation
