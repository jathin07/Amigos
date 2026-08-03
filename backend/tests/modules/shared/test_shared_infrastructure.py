import pytest
import uuid
from app.core.startup import create_app
from app.core.extensions import db
from app.modules.master.country.models import Country
from app.modules.master.country.repository import CountryRepository
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, ValidationException, DomainException
from app.validators.common import validate_code, validate_slug, validate_fk, validate_display_order

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def repo(app):
    return CountryRepository()

def test_base_model_audit_fields(repo):
    country = Country(name="India", code="IND", display_order=1)
    repo.add(country)
    db.session.commit()

    assert country.id is not None
    assert isinstance(country.id, uuid.UUID)
    assert country.created_at is not None
    assert country.updated_at is not None
    assert country.version == 1
    assert country.is_active is True

def test_repository_crud_and_count(repo):
    c1 = Country(name="United States", code="USA")
    c2 = Country(name="Canada", code="CAN")
    repo.add(c1)
    repo.add(c2)
    db.session.commit()

    assert repo.exists(c1.id) is True
    assert repo.get(c1.id).code == "USA"
    assert repo.count() == 2
    assert repo.count(is_active=True) == 2

    c2.is_active = False
    db.session.commit()
    assert repo.count(is_active=True) == 1
    assert repo.count(is_active=False) == 1

    repo.delete(c1)
    db.session.commit()
    assert repo.exists(c1.id) is False
    assert repo.count() == 1

def test_repository_pagination_and_sorting(repo):
    countries = [
        Country(name="Alpha", code="ALP", display_order=3),
        Country(name="Beta", code="BET", display_order=1),
        Country(name="Gamma", code="GAM", display_order=2),
        Country(name="Delta", code="DEL", display_order=4),
        Country(name="Epsilon", code="EPS", display_order=5),
    ]
    for c in countries:
        repo.add(c)
    db.session.commit()

    # Test pagination
    paginated = repo.paginate(page=1, page_size=2)
    assert paginated.total_records == 5
    assert paginated.total_pages == 3
    assert len(paginated.items) == 2
    assert paginated.page == 1
    assert paginated.page_size == 2

    # Test sorting by name desc
    sorted_paginated = repo.paginate(page=1, page_size=5, sort_by="name", sort_order="desc")
    names = [item.name for item in sorted_paginated.items]
    assert names == ["Gamma", "Epsilon", "Delta", "Beta", "Alpha"]

def test_base_service_responses_and_locking(app):
    service = BaseService()

    # Test optimistic locking check
    service.check_optimistic_lock(current_version=1, expected_version=1) # Should pass
    with pytest.raises(DomainException) as exc_info:
        service.check_optimistic_lock(current_version=2, expected_version=1)
    assert exc_info.value.code == "ERR_CONCURRENT_MODIFICATION"

    # Test JSON envelopes inside app context
    with app.test_request_context():
        resp, status = service.success(data={"key": "value"}, message="Operation successful")
        assert status == 200
        json_data = resp.get_json()
        assert json_data["success"] is True
        assert json_data["message"] == "Operation successful"
        assert json_data["data"] == {"key": "value"}

        err_resp, err_status = service.error(message="Invalid request", code="ERR_BAD", status_code=400)
        assert err_status == 400
        err_json = err_resp.get_json()
        assert err_json["success"] is False
        assert err_json["message"] == "Invalid request"
        assert err_json["errors"][0]["code"] == "ERR_BAD"

def test_validators():
    assert validate_code("  test_code_123  ") == "TEST_CODE_123"
    with pytest.raises(ValidationException):
        validate_code("code with spaces")

    assert validate_slug("  My-Test-Slug  ") == "my-test-slug"
    with pytest.raises(ValidationException):
        validate_slug("slug_with_underscore")

    assert validate_display_order("10") == 10
    with pytest.raises(ValidationException):
        validate_display_order("-5")

def test_exceptions():
    be = BusinessException("Business rule violated", code="ERR_BUS")
    assert be.message == "Business rule violated"
    assert be.code == "ERR_BUS"

    nf = NotFoundException("Entity not found")
    assert nf.code == "ERR_NOT_FOUND"

    ve = ValidationException("Invalid field")
    assert ve.code == "ERR_VALIDATION"
