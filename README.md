# 📦 PIM Contracts (`pim-contracts`)

Единый источник истины (Single Source of Truth) для контрактов, событий очередей и топологии RabbitMQ между микросервисами.

## Установка

### В режиме локальной разработки:
```bash
pip install -e /path/to/pim-contracts
```

### В Docker / CI / Production:
```bash
pip install "git+ssh://git@github.com/almas-istybaev/pim-contracts.git@v1.15.0"
```

## Правила эволюции схем (SemVer):
1. **Forward Compatibility:** Все схемы поддерживают `extra="ignore"`. Если продюсер добавил новое поле, консьюмер старой версии не падает.
2. **Обязательные значения по умолчанию:** Любые новые поля обязаны иметь дефолтное значение.
3. **Запрет breaking changes:** Переименование или удаление полей допустимо только при повышении мажорной версии (например, v2.0.0).

## Что нового

История 1.5–1.11 — в сообщениях тегов (`git tag -n1`).

### 1.21.0
Рекомендации (связи и компаньоны категорий) — только опциональные поля и DTO, payload 1.20.0 валиден. Значения `RelationType` не менялись.
- `MasterProductRelation.kind: "manual" | "rule" | None` — кто создал связь (`None` = manual, продюсер до 1.21.0); `score: float | None` (0..1, у manual 1.0); `reason: list[str]` — коды причин (`same_width`, `same_series`, `same_finish`, `same_color`, `same_brand`, `fits_length`, `price_tier`), неизвестные коды игнорировать.
- `MasterProductRecord.related` — сначала ручные, потом сгенерированные по убыванию `score`.
- Новый `MasterCategoryCompanion` (`category_id`, `category_slug`, `relation_type`, `priority ≥ 1`).
- `MasterCategoryRecord.companions: list[MasterCategoryCompanion]` (уже с наследованием, по `priority`) и `substitute_group: str | None` (группа взаимозаменяемых категорий, с наследованием). Фильтры компаньонов по атрибутам не публикуются.

### 1.20.0
- `MasterCategoryRecord.cutout: str | None` (после `photo`) — публичный URL (CDN) прозрачного 3D-рендера типового товара категории: без фона, ~1:1, обрезан по краям, WebP/PNG с альфой. Загружает контент-менеджер в админке inventory, медиа общее для всех языков. `null` — не загружен, витрина показывает `photo`. Нужен рельсу «Каталог» на главной santeh24.kz.

### 1.19.0
Скидка за комплект — только новые опциональные поля и DTO, payload 1.18.0 валиден:
- `MasterCategoryRecord.bundle_role: str | None` — ключ роли, заданный на самой категории (наследование считает PIM).
- `MasterProductRecord.bundle: MasterProductBundle | None` = `{ role: str | None, max_percent: int 0–100 }` — роль уже с учётом наследования категорий; `max_percent` inventory считает из маржи (себестоимость не публикуется). Розничные данные: в `PartnerProductRecord` нет.
- `BundleRules` = `{ enabled, tiers: [BundleTier{roles, percent}], roles: [BundleRole{key, name, name_kk, min_price}] }` — опубликованное правило; витрина считает скидку сама.
- `MasterBundleSetRecord` = `{ slug, name, translations: {kk: {name}}, image, product_ids }` — готовые комплекты из админки inventory.
- Неизвестная роль у потребителя = аксессуар. `schemas/storefront.schema.json` теперь включает `BundleRules` и `MasterBundleSetRecord`.

### 1.18.0
JSON Schema витринных записей (`MasterProductRecord`, `MasterCategoryRecord`, режим serialization) публикуется в каждом теге: `schemas/storefront.schema.json`, ключ `x-pim-contracts-version` — версия пакета. Публичный URL: `https://raw.githubusercontent.com/almas-istybaev/pim-contracts/vX.Y.Z/schemas/storefront.schema.json`. Схемы DTO не менялись.
- После правки моделей или версии: `.venv/bin/python scripts/storefront_schema.py`; `tests/test_storefront_schema.py` падает, если файл устарел.

### 1.16.0
Слияние дублей товаров — новое опциональное поле в `MasterProductRecord` и `PartnerProductRecord` (после `previous_slugs`):
- `merged_ids: list[int]` (по умолчанию `[]`) — id дублей, слитых в эту карточку; витрина отвечает 301 с URL по id дубля на эту карточку.
- Slug-и дубля (его `slug` и `previous_slugs`) PIM дописывает в `previous_slugs` оставшейся карточки — 301 по ним витрина уже делает (1.5.0).

### 1.15.0
Розница поставщика для конечного покупателя (с его сайта) в событиях фида — новые опциональные поля в `CanonicalProductFeedEvent` и `ProductStockUpdateEvent` (`ProductPriceUpdateEvent` не изменился):
- `supplier_retail_price: Decimal | None` (≥0) — не закупка и не `raw_price`; `null` = неизвестно, а не «сбросить».
- `supplier_retail_source: str | None` — откуда цена (`site`, `kaspi_feed`, …).
- `supplier_retail_observed_at: datetime | None` — UTC-время наблюдения; consumer отбрасывает устаревшие значения.

### 1.14.0
Новые DTO Partner API (inventory отдаёт внешним магазинам-партнёрам, первый — adilux.kz); существующие схемы не изменились:
- `PartnerProductRecord` — контент карточки: поля `MasterProductRecord` в том же порядке без `price`, `price_updated_at`, `cost_price`, `stock`, `stock_quantity`.
- `PartnerOfferRecord` — наше оптовое предложение: `product_id`, `wholesale_price` (ручная оптовая цена, `null` если не задана), `currency` (`KZT`), `available_qty` (≥0), `lead_time_days`, `updated_at`.

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
