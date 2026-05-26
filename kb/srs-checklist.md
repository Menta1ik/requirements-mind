# SRS Checklist

Используется агентом A2 для валидации Software Requirements Specification.
Основан на: ISO/IEC/IEEE 29148:2018, IEEE 830, BABOK v3.

## Трассируемость к BRD (проверяется первой)

- [ ] Все Business Goals из BRD покрыты хотя бы одним FR
- [ ] Все Business Rules из BRD отражены в FR или NFR
- [ ] Все Stakeholders из BRD имеют User Class в разделе 2.3
- [ ] Все In-Scope items из BRD имеют FR или Use Case
- [ ] Ни один FR не противоречит BRD Constraints
- [ ] Scope SRS не выходит за рамки Scope BRD

## Обязательные секции

| Секция | Обязательна | Критерий полноты |
|---|---|---|
| 0. Document Control | ✅ | Версия, статус, ссылка на BRD |
| 1.2 Scope | ✅ | Что система делает И не делает |
| 1.3 System Overview | ✅ | Контекстная диаграмма или описание |
| 2.3 User Classes | ✅ | Все роли из BRD Stakeholders покрыты |
| 2.4 Operating Environment | ✅ | OS, браузеры, окружения |
| 2.6 Assumptions & Dependencies | ✅ | Технические допущения + из BRD |
| 3. Functional Requirements | ✅ | Каждый FR: ID, описание, MoSCoW, источник в BRD, критерий верификации |
| 4.1 Performance | ✅ | Конкретные метрики (ms, RPS, concurrent users) |
| 4.2 Reliability & Availability | ✅ | SLA uptime %, MTTR |
| 4.3 Security | ✅ | Auth, encryption, audit logs |
| 4.4 Usability | ⚠️ | Если применимо |
| 5.2 System Interfaces | ✅ | Таблица интеграций |
| 6. Use Cases | ✅ | Happy Path + альтернативы + error scenarios |
| 7.1 Data Entities | ✅ | Основные сущности |
| 7.2 Data Dictionary | ✅ | Типы данных, форматы, ограничения |
| 8. Verification Table | ✅ | Каждый FR и NFR имеет метод проверки |
| Glossary | ✅ | Все термины из текста |

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
- Любое Business Goal из BRD не покрыто FR
- Любой FR без MoSCoW приоритета
- Любой NFR без измеримой метрики
- Нет таблицы интеграций
- Нет Verification таблицы
- Прямые противоречия с BRD
