# CLI 操作与恢复

本参考基于 `notebooklm-py 0.8.3`，2026-09-29 核对发布包的 CLI。它是社区项目，使用 Google 未公开接口；账号额度与 Google 服务可用性仍然适用。企业版官方 API 是另一条路线，本 skill 不混用。

一手资料：[项目](https://github.com/teng-lin/notebooklm-py)、[v0.8.3](https://github.com/teng-lin/notebooklm-py/releases/tag/v0.8.3)、[固定版本 CLI 文档](https://github.com/teng-lin/notebooklm-py/blob/v0.8.3/docs/cli-reference.md)。升级后重查 `--help`，不能把 main 分支文档当作本机版本支持的承诺。

## 安装与认证

需要 Python 3.10+。按宿主的第三方软件审查规则检查依赖后，可安装已验证版本：

```sh
uv tool install 'notebooklm-py[browser]==0.8.3'
notebooklm --version
notebooklm --profile learning login
notebooklm --profile learning auth check --test --passive --json
```

`login` 打开浏览器供用户本人登录，可能下载浏览器组件。已有可用 profile 则复用，不强制重新登录。需要多个账号时明确选 profile；命令中的 `learning` 是示例，不代表已有账号。Cookie、storage state 与浏览器资料目录留在 CLI 默认的认证目录，不放进项目。

不默认导出主浏览器 Cookie，不用 Google master token，不运行上游 skill/MCP 安装命令。本 skill 只需要 CLI。认证失败后暂停云端部分，继续本地工作；登录问题不等于课程制作必须停止。

## 命令配方

下面是分步配方，**不是可直接整段运行的脚本**。先创建实际文件、读取每一步 JSON，再用真实完整 ID 替换示例。通过 shell 时正确引用路径与文本；长指令写文件传 `--prompt-file`，不要把用户文本插入未引用的命令。

### 笔记本与来源

```sh
notebooklm --profile learning list --json
notebooklm --profile learning create '课程标题 [本次 run-id]' --json
notebooklm --profile learning source list -n NOTEBOOK_ID --json
notebooklm --profile learning source add '/absolute/course/lessons/01.md' --type file --title '讲义 M01' -n NOTEBOOK_ID --json
notebooklm --profile learning source add 'https://example.org/selected-reference' --type url -n NOTEBOOK_ID --json
notebooklm --profile learning source wait SOURCE_ID -n NOTEBOOK_ID --timeout 30 --interval 3 --json
```

上传文件前检查存在且是本次选定文件，并显式传 `--type file`：CLI 对某些不存在路径可能按文本处理，不能把路径字符串误当导入成功。不要对整个目录做未经筛选的批量上传。

`source add` 没有通用 `--wait` 参数；上传后使用 `source wait`。等待超时保留 source ID，随后继续查状态，不再 `source add`。来源失败时查看错误，必要时修正本地内容；任何删除行为单独判断授权。

新建前记录标题和 run-id；创建返回后记录 notebook ID。若创建结果未知，先 `list` 找同一 run-id 的笔记本；同名不保证同一个，不能自动复用无法确认的对象。

### 默认产物

下面两条 report 命令是二选一。严格自定义结构用 custom；沿用内置学习指南用 study-guide + append：

```sh
notebooklm --profile learning generate report --format custom --prompt-file '/absolute/course/prompts/guide.txt' --language zh_Hans -n NOTEBOOK_ID -s SOURCE_ID --no-wait --json
notebooklm --profile learning generate report --format study-guide --append '面向初学者，按课程大纲逐节讲解，包含案例、练习和答案依据' --language zh_Hans -n NOTEBOOK_ID -s SOURCE_ID --no-wait --json
notebooklm --profile learning generate quiz --prompt-file '/absolute/course/prompts/quiz.txt' --difficulty medium --quantity standard -n NOTEBOOK_ID -s SOURCE_ID --no-wait --json
```

多个来源重复 `-s ID`。对 report，`--append` 在 custom 模式不起作用。quiz 与 flashcards 在 0.8.3 **没有 `--language` 参数**，在 prompt 里明确“用简体中文生成”并检查结果；不要为了它们修改账号全局 `language set`。

使用返回的原始 `task_id` 非阻塞查询。0.8.3 的 task ID 与生成完成后 artifact ID 是同一标识；仍记录实际响应，不推测 ID。先落 manifest 再等下一步：

```sh
notebooklm --profile learning artifact poll TASK_ID -n NOTEBOOK_ID --json
notebooklm --profile learning artifact list -n NOTEBOOK_ID --json
notebooklm --profile learning download report '/absolute/course/exports/study-guide.md' -n NOTEBOOK_ID --artifact REPORT_ID --no-clobber --json
notebooklm --profile learning download quiz '/absolute/course/exports/quiz.json' -n NOTEBOOK_ID --artifact QUIZ_ID --format json --no-clobber --json
```

不同请求的返回字段可能不同。检查 JSON 后读字段，不硬编码为所有命令都有 `.id`；退出码为 0 的 poll 也不代表生成完成，必须检查状态。

轮询使用宿主支持的可中断等待并适当退避，例如 10、20、30 秒；不要紧循环。30 秒的 source wait 超时可恢复；没有硬性墙钟承诺。上下文或当前运行即将结束时保存状态并说明仍在生成，不谎报完成，不擅自建立定时任务。

### 可选产物

```sh
notebooklm --profile learning generate flashcards --prompt-file '/absolute/course/prompts/flashcards.txt' --difficulty medium --quantity standard -n NOTEBOOK_ID -s SOURCE_ID --no-wait --json
notebooklm --profile learning generate audio --prompt-file '/absolute/course/prompts/audio.txt' --language zh_Hans --format deep-dive -n NOTEBOOK_ID -s SOURCE_ID --no-wait --json
notebooklm --profile learning download flashcards '/absolute/course/exports/flashcards.json' -n NOTEBOOK_ID --artifact CARDS_ID --format json --no-clobber --json
notebooklm --profile learning download audio '/absolute/course/exports/audio.m4a' -n NOTEBOOK_ID --artifact AUDIO_ID --no-clobber --json
```

视频、幻灯片、信息图按需查看对应 `generate TYPE --help` 与 `download TYPE --help`。不要把音频文件仅改扩展名伪装成 MP3；读取实际编码/格式。

## Manifest 约定

从模板开始，字段填真实数据。为每条记录使用实际状态；本地文件路径优先相对课程根目录。

- `sources[]`：本地 `path` 与 `sha256` 或远端 `url`，`role`（original / authored），`version`，`source_id`，`status`。
- `artifacts[]`：`kind`，`prompt_path` 与 `prompt_sha256`，`source_ids`，`task_id`，`artifact_id`，`generation_status`，`download_status`，下载后的 `path` 与 `sha256`。远端生成状态保留实际返回值（如 in_progress / completed / failed），本地下载状态使用 not_started / pending / downloaded / failed；离线演练可用 not_executed_offline。
- `pending_operations[]`：`operation`，`started_at`，`status`（pending / unknown / reconciled / failed），以及标题、文件摘要或来源列表等最小核对依据。返回 ID 后回填并标记 reconciled。
- `quality_review`：not_started / partial / passed / needs_revision；只有有检查证据才置 passed。

例如报告已在云端生成但尚未下载，应记录 `generation_status: "completed"`、`download_status: "not_started"`，本地 `path` 与 `sha256` 留 null。只有实际文件存在且通过格式检查后才记 downloaded；内容质量是否通过另记在 quality_review。

文件变更的 SHA 不等于远端已更新。若用户要求更新课程，先核对既有 source 状态，再补充新版本并选择新的 ID 生成受影响产物；不要默认删旧来源。

## 故障恢复

| 状态 | 接下来的动作 |
| --- | --- |
| CLI 缺失 | 遵守宿主安装授权规则；本地课程照常做 |
| 未登录或 session 过期 | 用户在浏览器登录；随后恢复同一 notebook ID |
| 来源处理中 | 查询/等待原 source ID，ready 后才生成 |
| 来源失败或缺失 | 记录原因和课程覆盖缺口，修正后再继续 |
| 生成已提交、仍处理中 | poll 原 task ID，不重新 generate |
| 超时、不确定是否已提交 | list 查询并比对；不能唯一确认时保留状态再询问 |
| 额度或频率限制 | 保存任务与错误，按服务反馈退避；不无限重试、不换账号规避限制 |
| 下载失败 | 检查原 artifact 状态后重试下载，不重新生成 |
| 内容质量不合格 | 修讲义/提示，只重做对应产物并留版本记录 |

不自动调用清理、删除、分享、`ask --new` 或全局语言切换命令；这些操作超出默认制作课程范围。
