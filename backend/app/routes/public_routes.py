from flask import Blueprint, jsonify, request, current_app
from marshmallow import ValidationError
from app.models import Destination, Package, Lead
from app.schemas import LeadSchema
from app import cache
from app.core.extensions import db
from app.exceptions import ValidationException, DatabaseException
import requests
import os
import yaml
import re
from datetime import datetime

public_bp = Blueprint('public', __name__)


# -------------------------
# Health Check
# -------------------------
@public_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


# -------------------------
# Get Destinations (Grouped by State)
# -------------------------
@public_bp.route('/destinations', methods=['GET'])
def get_destinations():

    destinations = Destination.query.order_by(Destination.state).all()

    grouped_data = {}

    for dest in destinations:

        if dest.state not in grouped_data:
            grouped_data[dest.state] = []

        grouped_data[dest.state].append({
            "name": dest.name,
            "image": f"/images/places/{dest.image_url}"
        })

    response = [
        {"state": state, "places": places}
        for state, places in grouped_data.items()
    ]

    return jsonify(response), 200


# -------------------------
# Get Packages
# -------------------------
@public_bp.route('/packages', methods=['GET'])
def get_packages():

    packages = Package.query.order_by(Package.id.desc()).all()

    result = []

    for pkg in packages:
        result.append({
            "id": pkg.id,
            "title": pkg.title,
            "description": pkg.description,
            "duration_days": pkg.duration_days,
            "duration_nights": pkg.duration_nights,
            "price_per_person": pkg.price_per_person,
            "thumbnail_url": pkg.thumbnail_url,
            "highlights": pkg.highlights
        })

    return jsonify(result), 200


# -------------------------
# Submit Lead (Plan My Trip / Package Booking)
# -------------------------
@public_bp.route('/lead', methods=['POST'])
def create_lead():
    import uuid
    import re
    from sqlalchemy import select, func
    from app.models import LeadSource, Destination, TripType
    from app.modules.crm.service import CRMService
    from app.modules.master.country.models import Country
    from app.modules.master.state.models import State
    from app.modules.master.district.models import District

    data = request.get_json(silent=True) or {}

    try:
        validated_data = LeadSchema().load(data)
    except ValidationError as err:
        raise ValidationException("Validation failed", payload=err.messages)

    # Adapt flat JSON payload to nested CRM DTO structure
    contact_person = {
        "name": validated_data.get("name"),
        "phone": validated_data.get("phone"),
        "email": validated_data.get("email")
    }

    source_code = (validated_data.get("lead_type") or "trip_request").upper()
    source = db.session.execute(select(LeadSource).where(LeadSource.code == source_code)).scalars().first()
    if not source:
        source = LeadSource(code=source_code, name=source_code.replace("_", " ").title(), is_active=True)
        db.session.add(source)
        db.session.flush()
    lead_source_id = source.id
    
    trip_type_code = validated_data.get("trip_type")
    trip_type_id = None
    if trip_type_code:
        t_code = trip_type_code.strip().upper().replace(" ", "_")
        t_type = db.session.execute(select(TripType).where(TripType.code == t_code)).scalars().first()
        if not t_type:
            t_type = TripType(code=t_code, name=trip_type_code.strip().title(), is_active=True)
            db.session.add(t_type)
            db.session.flush()
        trip_type_id = t_type.id

    pkg_id = validated_data.get("package_id")
    if pkg_id:
        try:
            uuid.UUID(str(pkg_id))
        except ValueError:
            pkg_id = None

    notes = validated_data.get("notes") or ""
    destinations_payload = []
    dest_name = validated_data.get("preferred_destination")
    if dest_name:
        dest = db.session.execute(
            select(Destination).where(func.lower(Destination.name) == dest_name.lower())
        ).scalars().first()
        if not dest:
            # Query fallback IDs for NOT NULL geography columns
            country_obj = db.session.execute(select(Country)).scalars().first()
            if not country_obj:
                country_obj = Country(name="India", code="IN", phone_code="+91", display_order=1)
                db.session.add(country_obj)
                db.session.flush()
                
            state_obj = db.session.execute(select(State)).scalars().first()
            if not state_obj:
                state_obj = State(name="Kerala", code="KL", country_id=country_obj.id, display_order=1)
                db.session.add(state_obj)
                db.session.flush()
                
            district_obj = db.session.execute(select(District)).scalars().first()
            if not district_obj:
                district_obj = District(name="Ernakulam", code="EKM", state_id=state_obj.id, display_order=1)
                db.session.add(district_obj)
                db.session.flush()

            # Create a new active destination in the catalog
            dest = Destination(
                name=dest_name.strip().title(), 
                code=dest_name.strip().upper().replace(" ", "_")[:20], 
                slug=dest_name.strip().lower().replace(" ", "-"),
                country_id=country_obj.id,
                state_id=state_obj.id,
                district_id=district_obj.id,
                is_active=True
            )
            db.session.add(dest)
            db.session.flush()
        destinations_payload.append({
            "destination_id": dest.id,
            "priority": "High"
        })

    travel_dates = validated_data.get("travel_dates")
    travel_start_date = None
    travel_end_date = None
    if travel_dates:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", travel_dates):
            try:
                dt_obj = datetime.strptime(travel_dates, "%Y-%m-%d").date()
                travel_start_date = dt_obj
                travel_end_date = dt_obj
            except ValueError:
                notes = f"{notes}\n[Expected Travel Dates]: {travel_dates}".strip()
        else:
            notes = f"{notes}\n[Expected Travel Dates]: {travel_dates}".strip()

    budget_str = validated_data.get("budget")
    budget_val = None
    if budget_str:
        try:
            cleaned = re.sub(r"[^\d.]", "", budget_str)
            if cleaned:
                budget_val = float(cleaned)
        except Exception:
            notes = f"{notes}\n[Client Budget]: {budget_str}".strip()

    lead_payload = {
        "contact_person": contact_person,
        "lead_source_id": lead_source_id,
        "package_id": pkg_id,
        "trip_type_id": trip_type_id,
        "travel_start_date": travel_start_date,
        "travel_end_date": travel_end_date,
        "estimated_trip_days": validated_data.get("estimated_trip_days"),
        "traveler_count": validated_data.get("travelers") or 1,
        "male_count": validated_data.get("male_count"),
        "female_count": validated_data.get("female_count"),
        "faculty_count": validated_data.get("faculty_count"),
        "budget": budget_val,
        "notes": notes,
        "destinations": destinations_payload
    }

    try:
        crm_service = CRMService()
        new_lead = crm_service.create_lead(lead_payload)
    except Exception as e:
        db.session.rollback()
        raise DatabaseException(str(e))

    return jsonify({
        "message": "Lead submitted successfully",
        "lead_id": str(new_lead.id)
    }), 201


# -------------------------
# AI Notes Analysis
# -------------------------
@public_bp.route('/ai/analyze-notes', methods=['POST'])
def analyze_notes():
    from app.utils.ai_handler import analyze_notes_with_ai

    data = request.get_json(silent=True) or {}
    notes = data.get('notes', '')

    if len(notes) < 10:
        return jsonify({"suggestion": ""}), 200

    try:
        suggestion = analyze_notes_with_ai(notes)
        return jsonify({"suggestion": suggestion}), 200
    except Exception as e:
        # Fail gracefully without breaking the user experience
        print(f"AI Route Error: {e}")
        return jsonify({"suggestion": ""}), 200


# -------------------------
# Live Weather Proxy Endpoint
# -------------------------
COORDINATES_MAP = {
    "munnar": {"lat": 10.0889, "lon": 77.0595},
    "ooty": {"lat": 11.4102, "lon": 76.6950},
    "coorg": {"lat": 12.4244, "lon": 75.7382},
    "pondicherry": {"lat": 11.9416, "lon": 79.8083},
    "gokarna": {"lat": 14.5479, "lon": 74.3188},
    "wayanad": {"lat": 11.6050, "lon": 76.0830}
}

# Simple mood mapping based on weather condition
def map_condition_to_mood(condition: str) -> str:
    mapping = {
        "Clear": "Vibrant",
        "Clouds": "Calm",
        "Rain": "Cozy",
        "Snow": "Serene"
    }
    return mapping.get(condition, "Calm")

# Load static recommendations from YAML file
def load_recommendations():
    try:
        with open(os.path.join(current_app.root_path, "..", "data", "recommendations.yaml"), "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def map_wmo_to_condition(code):
    if code in [0, 1]:
        return "Clear"
    elif code in [2, 3, 45, 48]:
        return "Clouds"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]:
        return "Rain"
    return "Clear"


def map_owm_to_condition(main_cond):
    if main_cond in ["Clear"]:
        return "Clear"
    elif main_cond in ["Clouds", "Mist", "Smoke", "Haze", "Dust", "Fog"]:
        return "Clouds"
    elif main_cond in ["Rain", "Drizzle", "Thunderstorm"]:
        return "Rain"
    return "Clear"


@public_bp.route('/weather', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_weather():
    dest_name = request.args.get('q', '').lower().strip()
    if not dest_name:
        return jsonify({"error": "Missing parameter 'q'"}), 400

    coords = COORDINATES_MAP.get(dest_name)
    if not coords:
        return jsonify({
            "temp": 24,
            "condition": "Clear",
            "humidity": 60,
            "wind_speed": 10,
            "sunset": "6:30 PM"
        }), 200

    lat = coords["lat"]
    lon = coords["lon"]

    # Try OpenWeatherMap first if key is available
    owm_key = current_app.config.get("OPENWEATHER_API_KEY") or os.environ.get("OPENWEATHER_API_KEY")
    if owm_key:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owm_key}&units=metric"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                from datetime import datetime
                sunset_ts = data.get("sys", {}).get("sunset", 0)
                sunset_str = datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p") if sunset_ts else "6:30 PM"
                return jsonify({
                    "temp": round(data.get("main", {}).get("temp", 24)),
                    "condition": map_owm_to_condition(data.get("weather", [{}])[0].get("main", "Clear")),
                    "humidity": data.get("main", {}).get("humidity", 60),
                    "wind_speed": round(data.get("wind", {}).get("speed", 0) * 3.6), # convert m/s to km/h
                    "sunset": sunset_str
                }), 200
        except Exception as e:
            print(f"OpenWeatherMap API failed: {e}. Falling back to Open-Meteo.")

    # Fallback/Default: Open-Meteo (completely free, no API key required)
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=sunset&timezone=auto&forecast_days=1"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            sunset_time = daily.get("sunset", [""])[0]
            sunset_str = "6:30 PM"
            if sunset_time:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(sunset_time, "%Y-%m-%dT%H:%M")
                    sunset_str = dt.strftime("%I:%M %p")
                except Exception:
                    pass

            return jsonify({
                "temp": round(current.get("temperature_2m", 24)),
                "condition": map_wmo_to_condition(current.get("weather_code", 0)),
                "humidity": current.get("relative_humidity_2m", 60),
                "wind_speed": round(current.get("wind_speed_10m", 10)),
                "sunset": sunset_str
            }), 200
    except Exception as e:
        print(f"Open-Meteo API failed: {e}")

    # Ultimate fallback static values in case of complete internet outage
    static_db = {
        "munnar": { "temp": 18, "condition": "Clouds", "humidity": 84, "wind_speed": 11, "sunset": "6:42 PM" },
        "ooty": { "temp": 16, "condition": "Clouds", "humidity": 80, "wind_speed": 12, "sunset": "6:40 PM" },
        "coorg": { "temp": 20, "condition": "Rain", "humidity": 92, "wind_speed": 15, "sunset": "6:48 PM" },
        "pondicherry": { "temp": 31, "condition": "Clear", "humidity": 70, "wind_speed": 18, "sunset": "6:35 PM" },
        "gokarna": { "temp": 29, "condition": "Clear", "humidity": 74, "wind_speed": 14, "sunset": "6:52 PM" },
        "wayanad": { "temp": 22, "condition": "Rain", "humidity": 88, "wind_speed": 9, "sunset": "6:45 PM" }
    }
    fallback_data = static_db.get(dest_name, { "temp": 24, "condition": "Clear", "humidity": 60, "wind_speed": 10, "sunset": "6:30 PM" })
    return jsonify(fallback_data), 200

# -------------------------
# Destination Insights Endpoint (Phase 2)
# -------------------------
@public_bp.route('/destination_insights', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def destination_insights():
    dest_name = request.args.get('q', '').lower().strip()
    if not dest_name:
        return jsonify({"error": "Missing parameter 'q'"}), 400

    # Reuse weather logic (duplicate for now)
    coords = COORDINATES_MAP.get(dest_name)
    if not coords:
        weather_data = {"temp": 24, "condition": "Clear", "humidity": 60, "wind_speed": 10, "sunset": "6:30 PM"}
    else:
        lat = coords["lat"]
        lon = coords["lon"]
        owm_key = current_app.config.get("OPENWEATHER_API_KEY") or os.environ.get("OPENWEATHER_API_KEY")
        weather_data = None
        if owm_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owm_key}&units=metric"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    from datetime import datetime
                    sunset_ts = data.get("sys", {}).get("sunset", 0)
                    sunset_str = datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p") if sunset_ts else "6:30 PM"
                    weather_data = {
                        "temp": round(data.get("main", {}).get("temp", 24)),
                        "condition": map_owm_to_condition(data.get("weather", [{}])[0].get("main", "Clear")),
                        "humidity": data.get("main", {}).get("humidity", 60),
                        "wind_speed": round(data.get("wind", {}).get("speed", 0) * 3.6),
                        "sunset": sunset_str
                    }
            except Exception as e:
                print(f"OpenWeatherMap API failed (insights): {e}")
        if weather_data is None:
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=sunset&timezone=auto&forecast_days=1"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    current = data.get("current", {})
                    daily = data.get("daily", {})
                    sunset_time = daily.get("sunset", [""])[0]
                    sunset_str = "6:30 PM"
                    if sunset_time:
                        try:
                            dt = datetime.strptime(sunset_time, "%Y-%m-%dT%H:%M")
                            sunset_str = dt.strftime("%I:%M %p")
                        except Exception:
                            pass
                    weather_data = {
                        "temp": round(current.get("temperature_2m", 24)),
                        "condition": map_wmo_to_condition(current.get("weather_code", 0)),
                        "humidity": current.get("relative_humidity_2m", 60),
                        "wind_speed": round(current.get("wind_speed_10m", 10)),
                        "sunset": sunset_str
                    }
            except Exception as e:
                print(f"Open-Meteo API failed (insights): {e}")
        if weather_data is None:
            static_db = {
                "munnar": { "temp": 18, "condition": "Clouds", "humidity": 84, "wind_speed": 11, "sunset": "6:42 PM" },
                "ooty": { "temp": 16, "condition": "Clouds", "humidity": 80, "wind_speed": 12, "sunset": "6:40 PM" },
                "coorg": { "temp": 20, "condition": "Rain", "humidity": 92, "wind_speed": 15, "sunset": "6:48 PM" },
                "pondicherry": { "temp": 31, "condition": "Clear", "humidity": 70, "wind_speed": 18, "sunset": "6:35 PM" },
                "gokarna": { "temp": 29, "condition": "Clear", "humidity": 74, "wind_speed": 14, "sunset": "6:52 PM" },
                "wayanad": { "temp": 22, "condition": "Rain", "humidity": 88, "wind_speed": 9, "sunset": "6:45 PM" }
            }
            weather_data = static_db.get(dest_name, {"temp": 24, "condition": "Clear", "humidity": 60, "wind_speed": 10, "sunset": "6:30 PM"})

    # Mood derived from weather condition
    mood = map_condition_to_mood(weather_data.get("condition", "Clear"))

    # Load recommendations
    recommendations = load_recommendations().get(dest_name.title(), [])

    return jsonify({
        "weather": weather_data,
        "mood": mood,
        "recommendations": recommendations
    }), 200