# Agents for Image Restoration 最近工作调研

## TL;DR
- 2024-2026 的主线是从 all-in-one restoration model 走向 MLLM/Agent 驱动的诊断、规划、工具调用、质量反馈闭环。
- RestoreAgent (NeurIPS 2024) 是明确 agent 化的代表节点；2025-2026 快速扩展到 multi-agent、RL feedback、video、self-evolving、domain-specific agents。
- 论文机会优先级: benchmark/protocol > budgeted tool routing > downstream-aware restoration agent > degradation reasoning > self-evolving memory。

## 代表工作
- 2024 RestoreAgent (NeurIPS 2024 / arXiv): 把 MLLM 用作自治决策器: 识别退化 → 选择工具 → 执行恢复 → 评估反馈
- 2024 LLMRA (arXiv): 多模态大模型作为 restoration assistant, 把自然语言意图转成恢复策略
- 2024 InstructIR (arXiv): 用户用文字指令控制复原强度与目标, 从 fixed task 走向 instruction following
- 2024 Chain-of-Restoration (arXiv): 多任务恢复模型按 step-by-step 组合, 让通用模型做 zero-shot 复原链
- 2024 An Intelligent Agentic System (arXiv): 复杂退化场景下引入 agentic workflow, 强调诊断、规划、工具调用闭环
- 2025 Multi-Agent Image Restoration (arXiv): 多 agent 分工协作: degradation diagnosis / restoration / evaluation / refinement
- 2025 Hybrid Agents (arXiv): 混合 agent 把规则、MLLM、专用 restoration model 组合成可控系统
- 2025 Q-Agent (arXiv): 质量驱动 CoT, 用 MLLM robust reasoning 评估图像质量并指导恢复
- 2025 Restore-R1 (arXiv): 用 multimodal LLM perceptual feedback 做 RL, 学 efficient restoration agent
- 2025 SimpleCall (arXiv): label-free 环境里用 MLLM 感知反馈做轻量工具调用 agent
- 2025 InstructRestore (arXiv): 区域级 customized restoration, 解决一张图不同区域退化/需求不同的问题
- 2025 JarvisIR (arXiv): 面向自动驾驶感知的智能图像恢复, 连接 restoration 与 downstream perception
- 2025 MoA-VR (arXiv): Mixture-of-Agents for all-in-one video restoration, 从 image 扩展到 video
- 2026 RetouchIQ (arXiv): MLLM agents + generalist reward, 指令式 retouching 与主观质量对齐
- 2026 VQ-Jarvis (arXiv): retrieval-augmented video restoration agent, sharp vision + fast thought
- 2026 TIR-Agent (arXiv): 训练 exploratory and efficient agent, 更强调探索策略和推理成本
- 2026 PaAgent (arXiv): portrait-aware agent, subjective-objective RL 对齐人像修复审美
- 2026 DiTTo (arXiv): scalable order-aware all-in-one restoration agent, 关注任务顺序建模
- 2026 EvoIR-Agent (arXiv): experience-driven learning 的自进化 IR agent, 把历史经验回灌到决策
- 2026 Self-Evolving Agentic IR (arXiv): deliberate planning + intuitive execution, 强化“慢思考规划/快执行”分工
- 2026 OPERA (arXiv/OpenAlex): 端到端 joint planning-execution optimization, 从拼装 pipeline 走向联合优化
- 2026 Derain-Agent (arXiv/OpenAlex): plug-and-play rainy image restoration agent, 单退化垂直场景的 agent 化
- 2026 IAMAgent (arXiv/OpenAlex): interactive and adaptive multi-agent system, 强调人与系统交互迭代

## 数据文件
- raw_items.json: OpenAlex + arXiv + DBLP 原始结果
- filtered_papers.json: 规则粗筛结果
- selected_papers_clean.json: 人工清洗后的相关工作列表

## Slides
- /Users/dxb/auto/agents-image-restoration-slides/index.html