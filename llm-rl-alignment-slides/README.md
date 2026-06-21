# LLM 对齐强化学习方法 · 教学 Slides

> 从 PPO → DPO → GRPO,22 张幻灯片,从浅到深讲清楚大模型对齐的强化学习方法

## 打开方式

直接双击或用浏览器打开 `index.html`:

```bash
open /Users/dxb/llm-lab/slides/index.html
```

或从命令行:

```bash
# macOS
open /Users/dxb/llm-lab/slides/index.html

# Linux
xdg-open /Users/dxb/llm-lab/slides/index.html
```

## 操作说明

| 快捷键 | 功能 |
|--------|------|
| `→` `空格` `PageDown` | 下一页 |
| `←` `PageUp` | 上一样 |
| `Home` | 跳到首页 |
| `End` | 跳到末页 |
| `P` | 打印 / 导出 PDF |
| 触屏左右滑动 | 翻页 |

## 内容大纲

```
01  封面
02  学习目标
03  起点:SFT 解决了什么、没解决什么
04  强化学习基础:把 LLM 套进 RL 框架
05  最朴素的策略梯度:REINFORCE
06  PPO:让策略更新稳定下来
07  RLHF 三件套:经典做法(ChatGPT 同款)
08  RLHF 的工程痛点
09  DPO 的核心洞察
10  Bradley-Terry 偏好模型
11  从 Bradley-Terry 到 DPO 公式
12  DPO 数值演算:走一遍
13  DPO 代码逐行解读
14  β 怎么选:超参里最重要的一个
15  DPO 家族:砍什么补什么的演化
16  GRPO:推理模型的新范式
17  PRM vs ORM:过程奖励 vs 结果奖励
18  在线 vs 离线:训练范式
19  演进时间线:2017 → 2025
20  全景对比表
21  实战选型:决策树
22  本课要点 + 思考题
```

## 文件信息

- 路径: `/Users/dxb/llm-lab/slides/index.html`
- 大小: 约 42 KB(单文件,无外部依赖)
- 主题: 深色,适合投影
- 字体: 系统字体 + 中文 fallback(PingFang / Microsoft YaHei / Hiragino)

## 设计要点

- **单文件**: 嵌入 CSS / JS,不联网也能用
- **键盘翻页**: 课堂投屏常用快捷键
- **进度条**: 顶部蓝色条显示阅读进度
- **页码**: 右上 + 右下同时显示当前/总页数
- **打印友好**: P 键调用浏览器打印,可用"另存为 PDF"导出
- **触屏支持**: 移动设备左右滑动翻页

## 配合资源

- 同目录 `../tiny_llm/`: 迷你 LLM 框架,可对照 slide 13"代码逐行解读"自己跑
- 同目录 `../scripts/03_dpo.py`: DPO 训练脚本,对应 slide 11-14

## 二次修改

CSS 变量都在 `:root` 里,改配色只需修改:

```css
:root {
  --bg: #0e1116;       /* 背景 */
  --fg: #e6edf3;       /* 主文字 */
  --accent: #5b8def;   /* 强调色 (蓝) */
  --policy: #5b8def;   /* policy 模型 */
  --ref:    #8b949e;   /* reference 模型 */
  --critic: #10b981;   /* critic/value (绿) */
  --reward: #f59e0b;   /* reward (橙) */
  --chosen: #22c55e;   /* 偏好对-好 (绿) */
  --bad:    #ef4444;   /* 偏好对-坏 (红) */
  --loss:   #a78bfa;   /* 损失函数 (紫) */
}
```
