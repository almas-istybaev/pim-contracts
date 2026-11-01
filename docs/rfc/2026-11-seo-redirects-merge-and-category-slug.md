# Cross-Domain RFC: 301 со слитых дублей товаров и со старых slug категорий

**Источник (кто просит):** santeh24.kz, `frontend/src/lib/pim.ts` (`syncPIMData`) и `pim-mapper.ts` (`buildSlugIndex`, `buildCategoryRedirects`, `buildWithdrawnRedirects`)
**Целевой репо (владелец данных):** inventory (матчинг/дедуп, slug-и категорий и товаров)
**Зачем:** при слиянии дублей и смене slug категории старые URL отдают 404 или 301 не туда — теряются ссылочный вес и позиции в выдаче.

## Что уже есть в контракте

| Хвост | Контракт | Витрина |
|---|---|---|
| Старый slug категории → новый | `MasterCategoryRecord.previous_slugs` (1.13.0) | `buildCategoryRedirects` → Redis `categoryRedirects` — готово |
| Старый slug товара → текущий | `MasterProductRecord.previous_slugs` (1.5.0) | `buildSlugIndex` → `productRedirects` — готово |
| URL слитого дубля → оставшаяся карточка | **нет** | дубль пропадает из выгрузки; после `MISSING_TTL_DAYS` `buildWithdrawnRedirects` шлёт его на категорию, а не на карточку |

По категориям контракт менять не нужно: остаётся проверить, что inventory заполняет `previous_slugs` при смене slug (см. чек-лист).

## Требуемое

- `MasterProductRecord.merged_ids: list[int] = []` — id дублей, слитых в эту карточку. Витрина отвечает 301 с `/product/{id дубля}` на эту карточку.
- То же поле в `PartnerProductRecord` (инвариант: поля партнёрской карточки = поля мастер-карточки без розницы).
- Slug-и дубля (его `slug` и все его `previous_slugs`) inventory дописывает в `previous_slugs` оставшейся карточки. Это прошлые URL того же товара — отдельное поле не нужно, 301 по ним витрина уже делает.
- Кто заполняет и когда: inventory при слиянии дублей (merge в админке/дедупе), навсегда — список только растёт. Цепочка слияний (A ← B ← C) схлопывается: у A в `merged_ids` и B, и C.

Почему поле на оставшейся карточке, а не `merged_into` на дубле: слитый дубль не попадает в выгрузку `MasterProductRecord`, витрине негде прочитать `merged_into`. Вешать на выжившую — так же, как `previous_slugs`.

**pim-contracts:** minor 1.16.0 (новое опциональное поле с дефолтом).
**Порядок выката:** pim-contracts 1.16.0 → inventory (заполнение) → santeh24.kz (редиректы) / adilux (по желанию).
**Пока не сделано:** витрина продолжает вести URL исчезнувшего дубля на категорию через `buildWithdrawnRedirects` — честный fallback, не заглушка.

## Открытые вопросы

1. Есть ли в inventory история уже сделанных слияний (лог/таблица merge), чтобы заполнить `merged_ids` задним числом? Если нет — старые слияния остаются на `WITHDRAWN_SEED`/category-301.
2. Конфликт: slug дубля совпадает с живым slug другой карточки — `buildSlugIndex` уже игнорирует такой редирект (`from in slugs`), inventory стоит такой slug не дописывать.
