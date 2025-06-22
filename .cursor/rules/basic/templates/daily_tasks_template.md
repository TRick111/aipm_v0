---
date: { { date } }
type: daily_tasks
version: 1.1
---

| 体重 (kg) | 体脂肪率 (%) |
| :-------: | :----------: |
|           |              |

# 📋 {{date}} - 日次タスク

## 📅 今日の予定

{{#calendar}}
{{#events}}

-   {{start_time}}-{{end_time}} {{summary}}{{#location}} at {{location}}{{/location}}
    {{/events}}
    {{^events}}
-   特になし
    {{/events}}
    {{/calendar}}

## 🔥 今日のフォーカス

-   [ ]

## 📝 タスクリスト

{{#tasks_by_project}}

### {{project_name}}

{{#tasks}}

-   [ ] {{task}} {{#due}}(期限: {{due}}){{/due}}
        {{/tasks}}
        {{/tasks_by_project}}

## 📓 メモ・気づき

-

## 💡 明日のタスク候補

-   [ ]

## ⚠️ インピーディメント

-
