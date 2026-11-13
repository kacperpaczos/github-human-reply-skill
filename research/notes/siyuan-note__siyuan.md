# siyuan-note/siyuan

## Opening an issue
Four templates (bug + feature, EN and zh-CN); blank issues disabled; contact links to siyuan-community/ideas and @b3logos.

(a) Bugs: the template forces four confirmations (searched existing issues, reproducible with the default theme, extensions ruled out), then Describe the problem / Steps to reproduce / Expected result / Screenshot / Runtime information / Log file / More info.

(b) Feature requests: features ARE issues here, but the template demands four checkboxes - searched, one request per issue, broadly applicable rather than personal customization, not graph-related (new graph features are refused). 18 closed not planned (#21292, #21396, #21308).

(c) Fix proposals: the PR template says file an issue first and discuss; only text/language changes may be sent straight to PR (#20851: "请填写 PR 模板，然后我们会评估需求"). Marketplace ideas go to siyuan-community/ideas.

Titles are short phrases, mostly Chinese, no prefixes (#21404); labels Bug / Enhancement.

## Issues and pull requests
Fixes land as commits pushed straight to dev by 88250 with a commit link, then the issue is closed by hand - 0 of 150 closed via PR or commit. Contributor PRs are bilingual (English + 描述), fill Description / Type of change / Checklist, target dev (GitHub auto-retargets), and carry one purpose or they are rejected; in #21207 TCOTC asked for installer-size comparison and 88250 answered with per-platform percentages. Merged PRs often draw no comment (#21300).

## How the conversation goes
Median first reply 0.6 h, one comment per issue; 97 of 150 closed by the maintainer, 88250 in most threads. Replies quote the fix commit, the test counts ("54 项相关测试和 pnpm run lint 通过") and ask for a retest. Missing info: "请关闭所有插件、代码片段并在默认主题下录屏演示，如果还能重现我们会重开。" (#21298). "No" is polite and reasoned (#21396). Duplicates get "Duplicate of #21399" (#21404). Reporters reply in short Chinese, sometimes re-reporting the same bug, once pasting a raw email thread (#21347). English reporters get bilingual EN+中文 replies (#21386).

## Maintainer voice
#21298, 88250: "请关闭所有插件、代码片段并在默认主题下录屏演示，如果还能重现我们会重开。"
#21396, 88250: "综合功能收益、交互复杂度和维护成本，我们目前没有将思源改造为 Blender 式自由工作台的计划，因此关闭此提议。"
#21292, 88250: "独立标签页涉及数据库与文档块的关联等设计，暂时不计划支持，先关闭该 issue。"
#21308, 88250: "手机端目前以单文档阅读和编辑为主…暂不考虑增加文档树分屏或悬浮小窗"
#20845, 88250: "We'd prefer not to add promotional deployment badges for individual third-party services to the README."

## If you are an outsider here
Tick every confirmation in the template; one issue per request.
Paste the runtime-info block from Settings - About; attach a screen recording.
File the issue before opening the PR; only text/language work may skip it (#20851).
Write Chinese or English; replies come back bilingual (#21386).
Re-file as a new issue rather than reviving a thread locked after 30 days idle; link the old one.

## What this sample cannot tell
No forum or idea-repo data, so how a rejected request is reworked, and how the 19 vague "other" issues are triaged, is invisible.
