import uuid
from sqlalchemy import select, func, extract
from sqlalchemy.orm import joinedload

from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import Booking, Traveler, Document, PaymentSchedule, BookingStatusHistory
from app.core.extensions import db
from app.common.pagination import PaginationResult
from app.common.filters import apply_filters
from app.common.search import apply_search
from app.common.sorting import apply_sort
from app.common.pagination import apply_pagination


class BookingRepository(SQLAlchemyBaseRepository[Booking]):
    """
    Repository for persistence logic of the Booking aggregate.
    """
    searchable_fields = [
        "booking_number",
        "group_name",
        "package_name_snapshot",
        "trip_name_snapshot"
    ]

    sortable_fields = [
        "booking_number",
        "booking_date",
        "trip_start_date",
        "trip_end_date",
        "total_amount",
        "created_at"
    ]

    filterable_fields = [
        "booking_status_id",
        "booking_type_id",
        "booking_source_id",
        "customer_id",
        "trip_coordinator_team_member_id",
        "is_deleted"
    ]

    default_sort = [
        ("created_at", "desc")
    ]

    def __init__(self):
        super().__init__(Booking)

    def count_bookings_by_year(self, year: int) -> int:
        """
        Count the number of active bookings created in a calendar year.
        Utilizes dialect-agnostic extract to work on SQLite and Postgres.
        """
        stmt = select(func.count(Booking.id)).where(
            extract("year", Booking.booking_date) == year,
            Booking.is_deleted == False
        )
        return db.session.scalar(stmt) or 0

    def get_details(self, booking_id: uuid.UUID | str) -> Booking | None:
        """
        Retrieves a booking with all internal aggregate children eager-loaded (joinedload).
        Ensures a single database roundtrip, preventing N+1 queries.
        """
        stmt = select(Booking).options(
            joinedload(Booking.travelers),
            joinedload(Booking.payment_schedules),
            joinedload(Booking.documents),
            joinedload(Booking.status_history)
        ).where(
            Booking.id == booking_id,
            Booking.is_deleted == False
        )
        return db.session.scalar(stmt)

    def paginate(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        **filters,
    ) -> PaginationResult[Booking]:
        """
        Paginated listing without child collections to maintain database performance budgets.
        """
        if "is_deleted" not in filters:
            filters["is_deleted"] = False

        stmt = select(Booking)

        stmt = apply_filters(
            stmt,
            Booking,
            filters,
            self.filterable_fields,
        )

        stmt = apply_search(
            stmt,
            Booking,
            search_query,
            self.searchable_fields,
        )

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.session.scalar(total_stmt) or 0

        stmt = apply_sort(
            stmt,
            Booking,
            sort_by,
            sort_order,
            sortable_fields=self.sortable_fields,
            default_sort=self.default_sort,
        )

        stmt = apply_pagination(
            stmt,
            page,
            page_size,
        )

        items = list(db.session.scalars(stmt))

        return PaginationResult(
            items=items,
            page=page,
            page_size=page_size,
            total_records=total,
        )


class _TravelerRepository(SQLAlchemyBaseRepository[Traveler]):
    """
    Internal Traveler repository. Encapsulated within the Booking aggregate.
    """
    def __init__(self):
        super().__init__(Traveler)


class _DocumentRepository(SQLAlchemyBaseRepository[Document]):
    """
    Internal Document repository. Encapsulated within the Booking aggregate.
    """
    def __init__(self):
        super().__init__(Document)


class _PaymentScheduleRepository(SQLAlchemyBaseRepository[PaymentSchedule]):
    """
    Internal PaymentSchedule repository. Encapsulated within the Booking aggregate.
    """
    def __init__(self):
        super().__init__(PaymentSchedule)


class _BookingStatusHistoryRepository(SQLAlchemyBaseRepository[BookingStatusHistory]):
    """
    Internal BookingStatusHistory repository. Encapsulated within the Booking aggregate.
    """
    def __init__(self):
        super().__init__(BookingStatusHistory)
