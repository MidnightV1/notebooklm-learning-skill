# NotebookLM Learning Skill

把“我想学什么”变成课程讲义，再通过 NotebookLM CLI 制作学习指南、测验及可选的闪卡、音频等学习材料。

这是一个供 AI 助手读取的 **Agent Skill**，包含流程、教学标准、CLI 配方与进度模板。它不运行独立后台服务，不绑定某个模型，也不捆绑 Google 凭据。

## 使用效果

你可以这样说：

> 用 NotebookLM 帮我学上下文工程。我是产品经理，懂基本的 LLM 概念，想学完后能评审 Agent 的记忆和压缩方案。要中文讲义、学习指南和测验。

也可以：

> 把我提供的三篇资料做成课程，先只交付本地讲义和练习，不上传。

> 继续上次的学习包，读取 manifest，下载已经生成的测验，不重复生成。

流程：澄清必要信息 → 核实来源 → 设计目标与练习 → 编写讲义 → 导入 NotebookLM → 生成指定产物 → 下载并检查。

默认产物是讲义、学习指南、测验。多媒体按需生成。认证不可用时先交付本地课程和生成指令，明确尚未完成的云端部分。

## 安装 skill

支持上传 `.skill` 的工具可从 [Releases](https://github.com/MidnightV1/notebooklm-learning-skill/releases) 下载打包文件。使用本地技能目录时按下面的方式安装。

先把仓库克隆到你用于保存项目的目录：

```sh
git clone https://github.com/MidnightV1/notebooklm-learning-skill.git
cd notebooklm-learning-skill
```

Claude Code：

```sh
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/notebooklm-learning" ~/.claude/skills/notebooklm-learning
```

其他支持 Agent Skills 的工具：把 `skills/notebooklm-learning/` 放进该工具的技能目录。若使用 `~/.agents/skills`：

```sh
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/notebooklm-learning" ~/.agents/skills/notebooklm-learning
```

如果 `~/.agents/skills` 已经指向 `~/.claude/skills`，只做一次安装。目标已存在时先检查内容，别覆盖。链接安装后保留仓库目录，后续在仓库运行 `git pull --ff-only` 更新。宿主可能需要开启新会话才能重新发现技能。

## 配置 NotebookLM CLI

课程设计与本地输出不依赖 CLI。云端步骤需要 Python 3.10+、Google 账号及社区项目 [notebooklm-py](https://github.com/teng-lin/notebooklm-py)。按你的软件审查规则检查后安装：

```sh
uv tool install 'notebooklm-py[browser]==0.8.3'
notebooklm --profile learning login
notebooklm --profile learning auth check --test --passive --json
```

本人在打开的浏览器中登录。无需向助手发送密码、Cookie 或 token。首次登录可能下载浏览器组件。

CLI 使用未公开接口，Google 更新可能使它失效，生成仍受账号套餐和额度约束。本 skill 固定已检查的版本，升级后应重新核对命令。

## 交付与恢复

课程落到当前工作区的 `outputs/<course-slug>/`，或宿主指定的交付物目录。主讲义保留为可编辑 Markdown；NotebookLM 输出放进 `exports/`。

`manifest.json` 记录完整 notebook/source/artifact ID、来源及提示词摘要和进度。它由助手维护，不是一个自动执行的任务引擎。网络超时后先核对远端，再接续原任务；不盲目重复生成。

原始资料与 AI 编写的讲义分开标识。NotebookLM 对讲义的引用不算独立事实核验。课程质量检查覆盖目标、练习、答案、来源和文件可读性。

## 验证

```sh
uv run --with 'notebooklm-py==0.8.3' python scripts/check_cli_contract.py
```

脚本以禁用网络的 `--help` 调用检查 skill 里的命令是否被指定版本接受，不会登录、上传或生成。情境测试在 [evals/evals.json](evals/evals.json)，测试边界和实际结果见 [验证记录](docs/validation.md)。

## 文件

- [SKILL.md](skills/notebooklm-learning/SKILL.md)：主流程与触发条件。
- [学习设计](skills/notebooklm-learning/references/learning-design.md)：课程与质量标准。
- [CLI 参考](skills/notebooklm-learning/references/cli.md)：命令、版本差异和恢复策略。
- [模板](skills/notebooklm-learning/assets/)：课程简报和进度记录。

课程资料、导出文件与 Google 认证信息不属于本仓库。不要提交它们。本项目与 Google 及 notebooklm-py 作者无隶属关系。

## License

MIT。`notebooklm-py` 是独立第三方依赖，本仓库不包含其源代码。
