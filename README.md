# 📦 PIM Contracts (`pim-contracts`)

Единый источник истины (Single Source of Truth) для контрактов, событий очередей и топологии RabbitMQ между микросервисами.

## Установка

### В режиме локальной разработки:
```bash
pip install -e /path/to/pim-contracts
```

### В Docker / CI / Production:
```bash
pip install "git+ssh://git@github.com/almas-istybaev/pim-contracts.git@v1.13.0"
```

## Правила эволюции схем (SemVer):
1. **Forward Compatibility:** Все схемы поддерживают `extra="ignore"`. Если продюсер добавил новое поле, консьюмер старой версии не падает.
2. **Обязательные значения по умолчанию:** Любые новые поля обязаны иметь дефолтное значение.
3. **Запрет breaking changes:** Переименование или удаление полей допустимо только при повышении мажорной версии (например, v2.0.0).

## Что нового

История 1.5–1.11 — в сообщениях тегов (`git tag -n1`).

### 1.13.0
- `MasterCategoryRecord.previous_slugs: list[str]` (по умолчанию `[]`) — прошлые slug категории; витрина отвечает на них 301 на текущий `slug`. По образцу `MasterProductRecord.previous_slugs` (1.5.0).
- Уточнено описание `MasterCategoryRecord.slug`: при переименовании не меняется, админ может сменить вручную.

### 1.12.0
- Именованные типы `TranslationStatus`, `AttributeGroup`, `AttributeSection`, `RelationType` экспортируются из `pim_contracts`: потребители импортируют их вместо собственных `Literal`. Значения не изменились.
- `cost_price` и `ProductPriceUpdateEvent` помечены: PLP их не публикует, оставлены для совместимости v1.x.
- `SCHEMA_VERSION` — версия формата событий, не версия пакета; остаётся `1.0.0`.

### 1.4.0
Только опциональные поля (`None` по умолчанию), старый JSON без них валиден:
- `MasterCharacteristicRecord`: `code`, `group` (`"base" | "category"`), `unit`, `numeric_value`.
- `MasterProductRecord`: `shipping_dimension_unit`, `shipping_weight_unit`, `seo_title`, `seo_description`.
