import logging
from datetime import datetime, date, timezone, timedelta
import uuid
from app.core.extensions import cache
from app.domain.exceptions import ValidationException
from .repository import (
    SummaryQueryRepository,
    CRMQueryRepository,
    BookingQueryRepository,
    FinanceQueryRepository,
    OperationsQueryRepository
)

logger = logging.getLogger(__name__)

CACHE_PREFIX = "dashboard:v1"

class DashboardQueryService:
    def __init__(self):
        self.summary_repo = SummaryQueryRepository()
        self.crm_repo = CRMQueryRepository()
        self.booking_repo = BookingQueryRepository()
        self.finance_repo = FinanceQueryRepository()
        self.ops_repo = OperationsQueryRepository()

    def _get_current_month_range(self) -> tuple[date, date]:
        today = date.today()
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return start_date, end_date

    def _resolve_cache(self, widget_name: str, ttl_seconds: int, query_func) -> dict:
        """
        Orchestration helper implementing cache-aside with graceful fallback.
        """
        key = f"{CACHE_PREFIX}:{widget_name}"
        now = datetime.now(timezone.utc)

        # 1. Try to read from cache
        try:
            cached = cache.get(key)
            if cached and isinstance(cached, dict):
                expires_at_str = cached.get("expires_at")
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    remaining_ttl = int((expires_at - now).total_seconds())
                    if remaining_ttl > 0:
                        return {
                            "data": cached["data"],
                            "generated_at": cached["generated_at"],
                            "as_of": cached["generated_at"],
                            "cache_ttl": remaining_ttl,
                            "cache_status": "CACHE_HIT"
                        }
        except Exception as e:
            logger.warning(f"CACHE_UNAVAILABLE: Redis read failed for {key}. Error: {e}")
            # Fallback status will be set on DB query
            db_data = query_func()
            now_iso = now.isoformat()
            return {
                "data": db_data,
                "generated_at": now_iso,
                "as_of": now_iso,
                "cache_ttl": 0,
                "cache_status": "DB_FALLBACK"
            }

        # 2. Cache Miss - Query database
        try:
            db_data = query_func()
        except Exception as e:
            logger.error(f"DASHBOARD_COMPUTE_ERROR: Database query failed for widget {widget_name}. Error: {e}")
            raise e

        # 3. Store in cache
        now_iso = now.isoformat()
        expires_at = now + timedelta(seconds=ttl_seconds)
        cached_payload = {
            "data": db_data,
            "generated_at": now_iso,
            "expires_at": expires_at.isoformat()
        }

        try:
            cache.set(key, cached_payload, timeout=ttl_seconds)
            status = "CACHE_MISS"
        except Exception as e:
            logger.warning(f"CACHE_UNAVAILABLE: Redis write failed for {key}. Error: {e}")
            status = "DB_FALLBACK"

        return {
            "data": db_data,
            "generated_at": now_iso,
            "as_of": now_iso,
            "cache_ttl": ttl_seconds if status == "CACHE_MISS" else 0,
            "cache_status": status
        }

    # --- Widget Query Endpoints ---

    def get_summary_cards(self) -> dict:
        def query():
            today = date.today()
            start, end = self._get_current_month_range()
            revenue = self.summary_repo.get_revenue_this_month(start, end)
            expenses = self.summary_repo.get_expenses_this_month(start, end)
            
            return {
                "active_leads": self.summary_repo.get_active_leads_count(),
                "open_proposals": self.summary_repo.get_open_proposals_count(),
                "confirmed_bookings": self.summary_repo.get_confirmed_bookings_count(),
                "trips_today": self.summary_repo.get_trips_today_count(today),
                "outstanding_payments": self.summary_repo.get_outstanding_payments_count(today),
                "pending_vendor_payments": self.summary_repo.get_pending_vendor_payments_count(),
                "revenue_this_month": revenue,
                "profit_this_month": round(revenue - expenses, 2)
            }
        return self._resolve_cache("summary_cards", 300, query)

    def get_lead_pipeline(self) -> dict:
        def query():
            return self.crm_repo.get_lead_funnel()
        return self._resolve_cache("lead_pipeline", 300, query)

    def get_booking_pipeline(self) -> dict:
        def query():
            return self.booking_repo.get_booking_funnel()
        return self._resolve_cache("booking_pipeline", 300, query)

    def get_finance_summary(self) -> dict:
        def query():
            today = date.today()
            start, end = self._get_current_month_range()
            return self.finance_repo.get_finance_summary(today, start, end)
        return self._resolve_cache("finance_summary", 300, query)

    def get_upcoming_trips(self, page: int = 1, page_size: int = 10) -> dict:
        # We don't cache this widget directly with simple _resolve_cache because pagination parameters affect results.
        # But we can cache with a compound key: dashboard:v1:upcoming_trips:page:page_size
        widget_key = f"upcoming_trips:{page}:{page_size}"
        
        def query():
            today = date.today()
            limit_date = today + timedelta(days=14)
            return self.booking_repo.get_upcoming_trips(today, limit_date, page, page_size)
            
        return self._resolve_cache(widget_key, 900, query)

    def get_operations_overview(self) -> dict:
        def query():
            return self.ops_repo.get_operations_overview()
        return self._resolve_cache("operations_overview", 600, query)

    def get_revenue_trend(self) -> dict:
        def query():
            # Retrieve rolling 6-month historical aggregates
            today = date.today()
            months = []
            current_year = today.year
            current_month = today.month

            for i in range(5, -1, -1):
                # Calculate year and month back i steps
                m = current_month - i
                y = current_year
                while m <= 0:
                    m += 12
                    y -= 1
                months.append((y, m))

            trend_months = []
            for y, m in months:
                trend_months.append(self.finance_repo.get_monthly_metrics(y, m))

            return {
                "trend_months": trend_months,
                "period": "6M"
            }
        return self._resolve_cache("revenue_trend", 1800, query)

    # --- Cache Invalidation Operations ---

    def invalidate_widget(self, widget_name: str) -> bool:
        """Invalidate a specific cached widget prefix."""
        key = f"{CACHE_PREFIX}:{widget_name}"
        try:
            cache.delete(key)
            logger.info(f"Cache key invalidated: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache invalidation failed for key {key}: {e}")
            return False

    def invalidate_upcoming_trips(self) -> bool:
        """Helper to clear upcoming trips paginated cache keys (clears using wildcard delete or pattern if supported, otherwise deletes keys)."""
        # Flask-Caching SimpleCache doesn't support wildcards, but we can clear by prefix or delete standard patterns.
        # Since pagination is usually page 1-5, we delete page 1-10 to be safe.
        try:
            for page in range(1, 11):
                for size in [5, 10, 20]:
                    key = f"{CACHE_PREFIX}:upcoming_trips:{page}:{size}"
                    cache.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Failed to clear upcoming trips cache: {e}")
            return False
