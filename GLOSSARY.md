# GLOSSARY

Словарь предметной области (Ubiquitous Language) и архитектурные инварианты `pim-contracts`.

---

## 1. Доменная онтология

- **PIM (Product Information Management)**: Центральная подсистема управления каталогами товаров, категориями, характеристиками и мастер-данными.
- **Master Record (Golden Record, Золотая запись)**: Каноническое представление товара, категории или характеристики (`MasterProductRecord`, `MasterCategoryRecord`, `MasterCharacteristicRecord`), прошедшее дедупликацию, обогащение и нормализацию в `inventory-monitor` и экспортируемое витринам (например, `santeh24.kz`).
- **Translation (Перевод)**: Перевод текстов Master Record на язык витрины, ключ — код языка (сейчас только `kk`): `MasterProductTranslation` (с 1.6.0), `MasterCategoryTranslation` и `MasterCharacteristicTranslation` (с 1.7.0). `status`: `machine` — черновик Claude, `reviewed` — проверен человеком; `is_outdated` — RU-исходник изменился после перевода. Пустое поле перевода → витрина показывает RU.
- **AMQP Topology**: Структура точек обмена (exchanges), очередей (queues) и ключей маршрутизации (routing keys) RabbitMQ для межсервисного асинхронного взаимодействия.
- **Canonical Product Feed Event (`CanonicalProductFeedEvent`)**: Единое каноническое событие пакета товаров из фида поставщика.
- **Stock Update Event (`ProductStockUpdateEvent`)**: Событие изменения складских остатков и статуса наличия товара.
- **Price Update Event (`ProductPriceUpdateEvent`)**: Событие изменения ценовых предложений (розничных и оптовых). PLP его не публикует, оставлено для совместимости v1.x.
- **SourceType**: Перечисление источников входящих данных (`MOYSKLAD_API`, `TOPMAX_API`, `MULTI_SOURCE_SCRAPER`, `TELEGRAM_EXCEL`, `MANUAL_IMPORT`, `UNKNOWN`).
- **Currency**: Поддерживаемые валюты (`KZT`, `RUB`, `USD`, `EUR`).

---

## 2. Инварианты контрактов (SemVer & Forward Compatibility)

- **`extra = "ignore"`**: Все Pydantic-схемы обязаны игнорировать неизвестные поля. Это обеспечивает обратную совместимость при добавлении новых полей продюсером без поломки старых версий консьюмеров.
- **Обязательные значения по умолчанию**: Новые поля в контрактах обязаны иметь значения по умолчанию (`default=...` или `default_factory=...`), квалифицируя обновление как минорное (SemVer minor).
- **Запрет Breaking Changes**: Удаление полей, изменение их типов или переименование недопустимо без повышения мажорной версии (SemVer major) и плана согласованной миграции зависимых микросервисов.
- **Отсутствие логики**: Пакет содержит исключительно декларативные типы данных, DTO, схемы Pydantic v2, перечисления и константы. Категорически запрещено добавление бизнес-логики, работы с базами данных или внешними сетевыми API.
