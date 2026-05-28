# BRD Checklist

Используется агентом A2 для валидации Business Requirements Document.
Основан на: ISO/IEC/IEEE 29148:2018, BABOK v3, PMBOK 7.

## Augment-policy (как читать колонку «Обязательна»)

С версии v2.2 каждой секции присвоен **augment-policy** для случая, когда документ дорабатывается из baseline (`rm_mode: augment`):

- `required` — критическая секция смысла. **Обязательна в любом режиме.** Если в baseline её нет — A2 ставит `FAILED`. Это секции про бизнес-цели, измеримые метрики, scope, основные стейкхолдеры — без них документ не имеет ценности.
- `optional-augment` — рекомендуемая секция формы. В режиме `draft` она обязательна (`FAILED`), в режиме `augment` её отсутствие репортится как **warning** в блоке «⚠️ Augment-soft» отчёта валидации, но не блокирует переход в `approved`. Это секции, которые в baseline могут называться иначе или быть встроены в другие разделы.
- `if-applicable` — секция «по применимости». Если бизнес-контекст её требует — обязательна, иначе пропускается. Без изменений между режимами.

A2 определяет режим через frontmatter `context.md` (`rm_mode: draft | augment`).

## Обязательные секции

| Секция | Обязательна | Augment-policy | Критерий полноты |
|---|---|---|---|
| 0. Document Control | ✅ | optional-augment | Версия, статус, автор, approvers, revision history |
| 1. Executive Summary | ✅ | required | Problem Statement + Proposed Solution присутствуют |
| 2.2 Business Problem | ✅ | required | Проблема сформулирована чётко, не расплывчато |
| 2.3 AS-IS | ✅ | optional-augment | Текущее состояние описано |
| 2.4 TO-BE | ✅ | optional-augment | Желаемое состояние описано |
| 2.5 Gap Analysis | ✅ | optional-augment | Разрыв между AS-IS и TO-BE указан |
| 3.1 In Scope | ✅ | required | Минимум 3 пункта |
| 3.2 Out of Scope | ✅ | required | Минимум 2 пункта (что явно НЕ входит) |
| 3.3 Assumptions | ✅ | required | Минимум 3 допущения |
| 3.4 Constraints | ✅ | required | Минимум 2 ограничения |
| 4.1 Stakeholder Register | ✅ | required | Таблица: роль, имя/должность, интересы, влияние |
| 4.2 RACI Matrix | ✅ | optional-augment | Все роли из Stakeholder Register покрыты |
| 5.1 Business Goals | ✅ | required | SMART формат, минимум 2 цели |
| 5.3 Success Criteria / KPIs | ✅ | required | Измеримые метрики (не «улучшить», а «+20% за 6 мес») |
| 5.4 Business Rules | ✅ | required | Минимум 3 правила |
| 5.5 Functional Requirements | ✅ | required | Высокий уровень, минимум 5 требований |
| 5.6 Non-Functional Requirements | ✅ | required | Упомянуты: performance, security, availability |
| 5.7 Data Requirements | ⚠️ | if-applicable | Если система работает с данными — обязательно |
| 5.8 Compliance & Regulatory | ⚠️ | if-applicable | Если применимо — обязательно |
| 6.2 High-level Use Cases | ✅ | optional-augment | Таблица: ID, название, актор, цель, приоритет |
| 7.1 Risk Register | ✅ | required | Минимум 3 риска с митигацией |
| 7.2 Open Issues | ✅ | optional-augment | Все открытые вопросы с ответственным и дедлайном |
| 8. Glossary | ✅ | optional-augment | Все специфические термины из текста |

## Качество требований

- [ ] Нет противоречий между секциями
- [ ] Все термины из текста есть в Glossary
- [ ] Все stakeholders из RACI есть в Stakeholder Register
- [ ] Все цели из раздела 2 покрыты в разделе 5
- [ ] Нет допущений спрятанных в тексте (все вынесены в 3.3)
- [ ] Нет открытых вопросов без ответственного и дедлайна
- [ ] Business Goals в SMART формате
- [ ] KPIs измеримы (числа, проценты, сроки)

## Блокирующие проблемы (FAIL)

Документ получает статус FAIL если:
- Отсутствует любая секция с `augment-policy: required` (в любом режиме).
- В режиме `rm_mode: draft` — отсутствует любая секция с `augment-policy: optional-augment`.
- Business Goals не измеримы.
- Нет In Scope / Out of Scope.
- Нет Stakeholder Register.
- Нет Risk Register.
- Прямые противоречия между секциями.

В режиме `rm_mode: augment` отсутствие `optional-augment` секций → **warning** в блоке «⚠️ Augment-soft» отчёта, не блокер.
