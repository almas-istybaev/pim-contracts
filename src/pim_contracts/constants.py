"""
AMQP & RabbitMQ Topology Constants for PIM Ecosystem.
Centralizes exchange names, queue names, and routing keys to prevent typographical drift.
"""

# AMQP Exchanges
PIM_EVENTS_EXCHANGE = "pim.events"

# AMQP Queues
PIM_RAW_FEEDS_QUEUE = "pim_raw_feeds"

# AMQP Routing Keys
ROUTING_KEY_FEED_ALL = "pim.feed.#"
ROUTING_KEY_FEED_CANONICAL = "pim.feed.canonical"
ROUTING_KEY_FEED_STOCK_UPDATE = "pim.feed.stock"
ROUTING_KEY_FEED_PRICE_UPDATE = "pim.feed.price"

# Contract Versioning
SCHEMA_VERSION = "1.0.0"
