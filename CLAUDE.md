# pim-contracts

Pydantic v2 схемы/события/енумы для всей экосистемы. Код: `src/pim_contracts/` (`events/`, `enums.py`, `constants.py`). Ветка `main`.

## Команды
- `.venv/bin/pytest`

## Ключевое
- Только типы и константы; никакой бизнес-логики и БД.
- SemVer: новое опциональное поле = minor, удаление/переименование/смена типа = major (требует плана миграции потребителей). Версия в `pyproject.toml`.
- Любое изменение = проверь, кто использует (`price-list-processor`, `inventory-monitor`, типы витрины), и опиши это в ответе.
