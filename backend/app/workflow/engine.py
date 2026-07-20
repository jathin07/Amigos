from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from app.domain.events import DomainEvent, ApplicationEvent

logger = logging.getLogger("app.workflow")


class EventBus:
    """
    Lightweight in-memory event bus.

    Domain Events:
        - Executed synchronously.
        - Exceptions propagate to caller.

    Application Events:
        - Currently executed synchronously.
        - Can later be redirected to Celery/RQ without changing business code.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self.app = None

    def initialize(self, app) -> None:
        self.app = app
        logger.info("EventBus initialized.")

    def register(
        self,
        event: DomainEvent | ApplicationEvent,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:

        self._subscribers[event.value].append(handler)

        logger.debug(
            "Registered handler '%s' for event '%s'",
            handler.__name__,
            event.value,
        )

    def subscribe(self, event: DomainEvent | ApplicationEvent):
        """
        Decorator registration.
        """

        def decorator(handler):
            self.register(event, handler)
            return handler

        return decorator

    def publish(
        self,
        event: DomainEvent | ApplicationEvent,
        payload: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:

        payload = payload or kwargs

        handlers = self._subscribers.get(event.value, [])

        logger.info(
            "Publishing event '%s' to %d handler(s).",
            event.value,
            len(handlers),
        )

        for handler in handlers:

            try:
                handler(payload)

            except Exception:

                logger.exception(
                    "Handler '%s' failed while processing '%s'.",
                    handler.__name__,
                    event.value,
                )

                # Domain Events must fail the transaction.
                if isinstance(event, DomainEvent):
                    raise

                # Application Events are infrastructure concerns.
                logger.warning(
                    "Application event '%s' failed.",
                    event.value,
                )


event_bus = EventBus()