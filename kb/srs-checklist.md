# SRS Checklist

Используется агентом A2 для валидации Software Requirements Specification.
Основан на: ISO/IEC/IEEE 29148:2018, IEEE 830, BABOK v3.

## Augment-policy (как читать колонку «Обязательна»)

С версии v2.2 каждой секции присвоен **augment-policy** для случая, когда документ дорабатывается из baseline (`rm_mode: augment`):

- `required` — критическая секция смысла. **Обязательна в любом режиме.** Если в baseline её нет — A2 ставит `FAILED`. Это: функциональные требования с ID, измеримые NFR, Use Cases с альтернативами, таблица интеграций.
- `optional-augment` — рекомендуемая секция формы. В режиме `draft` обязательна (`FAILED`), в режиме `augment` отсутствие репортится как **warning** в блоке «⚠️ Augment-soft» отчёта валидации. Это секции с форматом (Data Entities как отдельный 7.1, Operating Environment как отдельный 2.4) — в baseline они могут быть встроены в другие разделы или иметь иные заголовки.
- `if-applicable` — секция «по применимости». Без изменений между режимами.

A2 определяет режим через frontmatter `context.md` (`rm_mode: draft | augment`).

## Трассируемость к BRD (проверяется первой)

- [ ] Все Business Goals из BRD покрыты хотя бы одним FR
- [ ] Все Business Rules из BRD отражены в FR или NFR
- [ ] Все Stakeholders из BRD имеют User Class в разделе 2.3
- [ ] Все In-Scope items из BRD имеют FR или Use Case
- [ ] Ни один FR не противоречит BRD Constraints
- [ ] Scope SRS не выходит за рамки Scope BRD

> **Примечание:** трассируемость к BRD — `required` в любом режиме. Bus.Goals без покрытия FR — FAILED всегда.

## Обязательные секции

| Секция | Обязательна | Augment-policy | Критерий полноты |
|---|---|---|---|
| 0. Document Control | ✅ | optional-augment | Версия, статус, ссылка на BRD |
| 1.2 Scope | ✅ | required | Что система делает И не делает |
| 1.3 System Overview | ✅ | optional-augment | Контекстная диаграмма или описание |
| 2.3 User Classes | ✅ | required | Все роли из BRD Stakeholders покрыты |
| 2.4 Operating Environment | ✅ | optional-augment | OS, браузеры, окружения |
| 2.6 Assumptions & Dependencies | ✅ | required | Технические допущения + из BRD |
| 3. Functional Requirements | ✅ | required | Каждый FR: ID, описание, MoSCoW, источник в BRD, критерий верификации |
| 4.1 Performance | ✅ | required | Конкретные метрики (ms, RPS, concurrent users) |
| 4.2 Reliability & Availability | ✅ | required | SLA uptime %, MTTR |
| 4.3 Security | ✅ | required | Auth, encryption, audit logs |
| 4.4 Usability | ⚠️ | if-applicable | Если применимо |
| 5.2 System Interfaces | ✅ | required | Таблица интеграций |
| 6. Use Cases | ✅ | required | Happy Path + альтернативы + error scenarios |
| 7.1 Data Entities | ✅ | optional-augment | Основные сущности (в baseline может называться «Модель данных» / «Data Model» — это допустимо) |
| 7.2 Data Dictionary | ✅ | optional-augment | Типы данных, форматы, ограничения (в baseline может быть таблицей внутри другого раздела) |
| 8. Verification Table | ✅ | required | Каждый FR и NFR имеет метод проверки |
| Glossary | ✅ | optional-augment | Все термины из текста |

## Качество требований

- [ ] Каждый FR имеет MoSCoW приоритет
- [ ] NFR содержат измеримые метрики (не «быстро», а «P95 < 200ms»)
- [ ] Каждый Use Case имеет Happy Path + минимум 1 альтернативный + error scenarios
- [ ] Нет FR без критерия верификации
- [ ] Нет дублирующихся требований
- [ ] Нет требований которые невозможно верифицировать
- [ ] Все Use Cases связаны с FR
- [ ] Все термины есть в Glossary

## Блокирующие проблемы (FAIL)

Документ получает статус FAIL если:
- Отсутствует любая секция с `augment-policy: required` (в любом режиме).
- В режиме `rm_mode: draft` — отсутствует любая секция с `augment-policy: optional-augment`.
- Любое Business Goal из BRD не покрыто FR.
- Любой FR без MoSCoW приоритета.
- Любой NFR без измеримой метрики.
- Нет таблицы интеграций.
- Нет Verification таблицы.
- Прямые противоречия с BRD.

В режиме `rm_mode: augment` отсутствие `optional-augment` секций → **warning** в блоке «⚠️ Augment-soft» отчёта, не блокер.
