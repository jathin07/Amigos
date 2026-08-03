import uuid
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException
from app.models import (
    Package,
    PackageHighlight,
    PackageInclusion,
    PackageExclusion,
    PackageDestination,
    UserAccount,
)
from .repository import PackageRepository

# Sentinel: distinguish "key was absent in payload" from "key was explicitly []"
_MISSING = object()


class PackageService(BaseService):
    def __init__(self):
        self.repository = PackageRepository()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_team_member_id(self) -> uuid.UUID | None:
        """Resolve current authenticated user's TeamMember ID from JWT."""
        user_id_str = get_jwt_identity()
        if user_id_str:
            try:
                user_id = uuid.UUID(str(user_id_str))
                user_acc = UserAccount.query.get(user_id)
                if user_acc:
                    return user_acc.team_member_id
            except (ValueError, AttributeError):
                pass
        return None

    def _validate_destinations(self, dest_requests: list[dict]) -> None:
        """
        Validate that every destination_id references an existing, active Destination.
        Uses repository helper — does NOT reach into another module's repository.
        """
        seen_positions: set[tuple] = set()
        for item in dest_requests:
            dest_id = item["destination_id"]
            found = self.repository.find_active_destination(dest_id)
            if not found:
                raise BusinessException(
                    f"Destination {dest_id} does not exist or is not active.",
                    code="ERR_INVALID_DESTINATION",
                )
            # Enforce (day_order, sequence) uniqueness within the request
            pos = (item["day_order"], item["sequence"])
            if pos in seen_positions:
                raise BusinessException(
                    f"Duplicate (day_order={item['day_order']}, sequence={item['sequence']}) "
                    "within the destinations list.",
                    code="ERR_INVALID_DESTINATION",
                )
            seen_positions.add(pos)

    def _sync_highlights(self, package: Package, highlights: list[dict]) -> None:
        """Replace the package's highlights collection with the supplied list."""
        # SQLAlchemy cascade="all, delete-orphan" — clear and re-populate
        package.highlights.clear()
        for item in highlights:
            package.highlights.append(
                PackageHighlight(
                    package_id=package.id,
                    highlight_text=item["highlight_text"].strip(),
                    display_order=item.get("display_order"),
                )
            )

    def _sync_inclusions(self, package: Package, inclusions: list[dict]) -> None:
        """
        Replace the package's inclusions collection.
        display_order is NOT persisted — column does not exist on package_inclusions.
        """
        package.inclusions.clear()
        for item in inclusions:
            package.inclusions.append(
                PackageInclusion(
                    package_id=package.id,
                    inclusion_text=item["inclusion_text"].strip(),
                    # display_order intentionally omitted — no DB column
                )
            )

    def _sync_exclusions(self, package: Package, exclusions: list[dict]) -> None:
        """
        Replace the package's exclusions collection.
        display_order is NOT persisted — column does not exist on package_exclusions.
        """
        package.exclusions.clear()
        for item in exclusions:
            package.exclusions.append(
                PackageExclusion(
                    package_id=package.id,
                    exclusion_text=item["exclusion_text"].strip(),
                    # display_order intentionally omitted — no DB column
                )
            )

    def _sync_destinations(self, package: Package, destinations: list[dict]) -> None:
        """Replace the package's destinations collection."""
        package.destinations.clear()
        for item in destinations:
            package.destinations.append(
                PackageDestination(
                    package_id=package.id,
                    destination_id=item["destination_id"],
                    day_order=item["day_order"],
                    sequence=item["sequence"],
                    overnight_stay=item.get("overnight_stay", False),
                    default_duration=item.get("default_duration"),
                )
            )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get(self, package_id: str) -> Package:
        try:
            uid = uuid.UUID(str(package_id))
        except ValueError:
            raise NotFoundException("Package not found", code="ERR_PACKAGE_NOT_FOUND")

        pkg = self.repository.get(uid)
        if not pkg or pkg.is_deleted:
            raise NotFoundException("Package not found", code="ERR_PACKAGE_NOT_FOUND")
        return pkg

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str | None = "title",
        sort_order: str = "asc",
        **filters,
    ):
        filters["is_deleted"] = False
        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

    def create(self, data: dict) -> Package:
        # Duplicate title check
        if self.repository.find_by_title_active(data["title"]):
            raise BusinessException(
                "An active package with this title already exists.",
                code="ERR_PACKAGE_DUPLICATE_TITLE",
            )

        # Validate destinations if supplied
        dest_requests = data.get("destinations", [])
        if dest_requests:
            self._validate_destinations(dest_requests)

        team_member_id = self._resolve_team_member_id()

        pkg = Package(
            title=data["title"].strip(),
            description=data.get("description"),
            duration_days=data["duration_days"],
            duration_nights=data["duration_nights"],
            starting_price=data.get("starting_price"),
            starting_city=data.get("starting_city"),
            thumbnail_url=data.get("thumbnail_url"),
            terms=data.get("terms"),
            is_featured=data.get("is_featured", False),
            is_active=data.get("is_active", True),
            version=1,
        )

        if team_member_id:
            pkg.created_by_team_member_id = team_member_id
            pkg.updated_by_team_member_id = team_member_id

        self.repository.add(pkg)
        # Flush to get the pkg.id before syncing children
        from app.core.extensions import db
        db.session.flush()

        # Sync child collections
        self._sync_highlights(pkg, data.get("highlights", []))
        self._sync_inclusions(pkg, data.get("inclusions", []))
        self._sync_exclusions(pkg, data.get("exclusions", []))
        self._sync_destinations(pkg, dest_requests)

        self.commit()
        return pkg

    def update(self, package_id: str, data: dict, raw_keys: set) -> Package:
        """
        raw_keys must be the set of top-level keys actually present in the
        original JSON body. This enables the three-state collection rule:
          - key absent   → unchanged
          - key = []     → cleared
          - key = [...]  → replaced
        """
        uid = uuid.UUID(str(package_id))
        pkg = self.repository.get(uid)
        if not pkg or pkg.is_deleted:
            raise NotFoundException("Package not found", code="ERR_PACKAGE_NOT_FOUND")

        # Optimistic locking
        self.check_optimistic_lock(pkg.version, data.get("version"))

        # Duplicate title check
        if "title" in data:
            new_title = data["title"].strip()
            if self.repository.find_by_title_active(new_title, exclude_id=uid):
                raise BusinessException(
                    "An active package with this title already exists.",
                    code="ERR_PACKAGE_DUPLICATE_TITLE",
                )

        # Validate destinations if present in payload
        if "destinations" in raw_keys:
            dest_requests = data.get("destinations", [])
            if dest_requests:
                self._validate_destinations(dest_requests)

        # Apply scalar updates
        scalar_fields = (
            "title", "description", "duration_days", "duration_nights",
            "starting_price", "starting_city", "thumbnail_url", "terms",
            "is_featured", "is_active",
        )
        for field in scalar_fields:
            if field in data:
                val = data[field]
                if field == "title" and isinstance(val, str):
                    val = val.strip()
                setattr(pkg, field, val)

        # Three-state collection sync
        if "highlights" in raw_keys:
            self._sync_highlights(pkg, data.get("highlights", []))
        if "inclusions" in raw_keys:
            self._sync_inclusions(pkg, data.get("inclusions", []))
        if "exclusions" in raw_keys:
            self._sync_exclusions(pkg, data.get("exclusions", []))
        if "destinations" in raw_keys:
            self._sync_destinations(pkg, data.get("destinations", []))

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            pkg.updated_by_team_member_id = team_member_id

        pkg.version += 1

        self.repository.add(pkg)
        self.commit()
        return pkg

    def delete(self, package_id: str) -> None:
        uid = uuid.UUID(str(package_id))
        pkg = self.repository.get(uid)
        if not pkg or pkg.is_deleted:
            raise NotFoundException("Package not found", code="ERR_PACKAGE_NOT_FOUND")

        pkg.is_active = False
        pkg.is_deleted = True
        pkg.deleted_at = datetime.now(timezone.utc)

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            pkg.deleted_by_team_member_id = team_member_id
            pkg.updated_by_team_member_id = team_member_id

        pkg.version += 1

        self.repository.add(pkg)
        self.commit()
