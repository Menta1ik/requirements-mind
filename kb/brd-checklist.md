# BRD Checklist

Используется агентом A2 для валидации Business Requirements Document.
Основан на: ISO/IEC/IEEE 29148:2018, BABOK v3, PMBOK 7.

## Обязательные секции

| Секция | Обязательна | Критерий полноты |
|---|---|---|
| 0. Document Control | ✅ | Версия, статус, автор, approvers, revision history |
| 1. Executive Summary | ✅ | Problem Statement + Proposed Solution присутствуют |
| 2.2 Business Problem | ✅ | Проблема сформулирована чётко, не расплывчато |
| 2.3 AS-IS | ✅ | Текущее состояние описано |
| 2.4 TO-BE | ✅ | Желаемое состояние описано |
| 2.5 Gap Analysis | ✅ | Разрыв между AS-IS и TO-BE указан |
| 3.1 In Scope | ✅ | Минимум 3 пункта |
| 3.2 Out of Scope | ✅ | Минимум 2 пункта (что явно НЕ входит) |
| 3.3 Assumptions | ✅ | Минимум 3 допущения |
| 3.4 Constraints | ✅ | Минимум 2 ограничения |
| 4.1 Stakeholder Register | ✅ | Таблица: роль, имя/должность, интересы, влияние |
| 4.2 RACI Matrix | ✅ | Все роли из Stakeholder Register покрыты |
| 5.1 Business Goals | ✅ | SMART формат, минимум 2 цели |
| 5.3 Success Criteria / KPIs | ✅ | Измеримые метрики (не «улучшить», а «+20% за 6 мес») |
| 5.4 Business Rules | ✅ | Минимум 3 правила |
| 5.5 Functional Requirements | ✅ | Высокий уровень, минимум 5 требований |
| 5.6 Non-Functional Requirements | ✅ | Упомянуты: performance, security, availability |
| 5.7 Data Requirements | ⚠️ | Если система работает с данными — обязательно |
| 5.8 Compliance & Regulatory | ⚠️ | Если применимо — обязательно |
| 6.2 High-level Use Cases | ✅ | Таблица: ID, название, актор, цель, приоритет |
| 7.1 Risk Register | ✅ | Минимум 3 риска с митигацией |
| 7.2 Open Issues | ✅ | Все открытые вопросы с ответственным и дедлайном |
| 8. Glossary | ✅ | Все специфические термины из текста |

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
- Отсутствует любая секция помеченная ✅
- Business Goals не измеримы
- Нет In Scope / Out of Scope
- Нет Stakeholder Register
- Нет Risk Register
- Прямые противоречия между секциями
