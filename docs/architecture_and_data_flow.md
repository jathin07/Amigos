# Amigos Tourism Application Architecture

This document provides a comprehensive technical overview of the Amigos application, including system architecture, data flow, component structure, and database design.

## 1. High-Level System Architecture

The application follows a decoupled client-server architecture. The frontend is a Single Page Application (SPA), while the backend is a RESTful API.

```mermaid
graph TD
    Client[Web Browser]
    
    subgraph Frontend [React SPA Vite]
        UI[React Components]
        State[Component State/Hooks]
        Routing[React Router]
        Tailwind[Tailwind CSS]
    end
    
    subgraph Backend [Flask REST API]
        Controller[Flask Routes/Blueprints]
        Logic[Business Logic]
        ORM[SQLAlchemy ORM]
    end
    
    Database[(Relational Database)]
    
    Client <-->|Interacts| UI
    UI <--> State
    UI <--> Routing
    UI <--> Tailwind
    
    State <-->|HTTP/JSON Fetch| Controller
    
    Controller <--> Logic
    Logic <--> ORM
    ORM <-->|SQL Queries| Database
```

## 2. Component Structure (Frontend)

The frontend uses React and is structured around reusable UI components and specialized pages.

```mermaid
graph TD
    App[App.jsx Router]
    
    Layout[Global Layout]
    App --> Layout
    
    Navbar[Navbar.jsx]
    Footer[Footer.jsx]
    Layout --> Navbar
    Layout --> Footer
    
    Pages[Pages]
    Layout --> Pages
    
    subgraph Public Pages
        Home[Home.jsx]
        Packages[Packages.jsx]
        PlanTrip[BookingForm.jsx / Plan Trip]
        Destinations[Destinations.jsx]
    end
    
    subgraph Admin Pages
        AdminLogin[AdminLogin.jsx]
        AdminDashboard[AdminDashboard.jsx]
    end
    
    Pages --> Home
    Pages --> Packages
    Pages --> PlanTrip
    Pages --> Destinations
    Pages --> AdminLogin
    Pages --> AdminDashboard
    
    subgraph Reusable Components
        PackageCard[PackageCard.jsx]
        PlacesCarousel[PlacesCarousel.jsx]
        FadeIn[FadeIn Effect]
    end
    
    Home --> PlacesCarousel
    Packages --> PackageCard
    Home --> FadeIn
    Packages --> FadeIn
```

## 3. Data Flow Diagram

The data flow illustrates how user actions propagate from the frontend to the backend database.

```mermaid
sequenceDiagram
    participant User
    participant Browser as React Frontend
    participant API as Flask Backend
    participant DB as SQLite/Database

    User->>Browser: Submits "Plan a Trip" Form
    activate Browser
    
    Browser->>Browser: Validates Form Data & Updates State
    
    Browser->>API: POST /plan-trip (JSON payload)
    activate API
    
    API->>API: Parses JSON & validates data
    
    API->>DB: SQLAlchemy session.add(Lead)
    activate DB
    DB-->>API: Returns new Lead ID
    deactivate DB
    
    API-->>Browser: 201 Created (Success JSON)
    deactivate API
    
    Browser->>User: Displays Success Toast/Alert
    deactivate Browser
```

## 4. Entity-Relationship (ER) Diagram

The backend relies on a relational database managed by SQLAlchemy. Below is the main schema structure.

```mermaid
erDiagram
    DESTINATION {
        int id PK
        string name
        string state
        string description
        string image_url
        string tags
        datetime created_at
    }
    
    PACKAGE {
        int id PK
        string title
        string description
        int duration_days
        int duration_nights
        float price_per_person
        string thumbnail_url
        string highlights
        datetime created_at
    }
    
    PACKAGE_DESTINATION {
        int id PK
        int package_id FK
        int destination_id FK
    }
    
    TEAM_MEMBER {
        int id PK
        string name
        string role
        string phone
        boolean active
    }
    
    LEAD {
        int id PK
        string name
        string phone
        string email
        string lead_type
        int package_id FK
        string travel_dates
        int travelers
        string budget
        string notes
        string status
        int contact_person_id FK
        string itinerary_pdf_url
        datetime created_at
    }
    
    TRIP_ORGANIZER {
        int id PK
        int lead_id FK
        int team_member_id FK
    }
    
    TRIP_FINANCE {
        int id PK
        int lead_id FK
        float revenue
        float transport_cost
        float hotel_cost
        float food_cost
        float activity_cost
        float other_cost
        float total_cost
        float profit
        datetime created_at
    }
    
    ADMIN {
        int id PK
        string email
        string password_hash
    }
    
    CUSTOMER {
        int id PK
        string name
        string email
        string phone
        string secondary_contact
        string address
        string preferences
        datetime created_at
    }
    
    BOOKING {
        int id PK
        int lead_id FK
        int customer_id FK
        int package_id FK
        datetime start_date
        datetime end_date
        float total_price
        string status
        datetime created_at
    }
    
    TRAVELER {
        int id PK
        int booking_id FK
        string name
        int age
        string gender
        string id_proof
        string special_requests
    }
    
    PAYMENT {
        int id PK
        int booking_id FK
        float amount
        datetime date
        string payment_method
        string transaction_id
        string status
    }
    
    TASK {
        int id PK
        int assigned_to_id FK
        int linked_lead_id FK
        string description
        datetime due_date
        string status
        datetime created_at
    }

    PACKAGE ||--o{ PACKAGE_DESTINATION : contains
    DESTINATION ||--o{ PACKAGE_DESTINATION : belongs_to
    
    PACKAGE ||--o{ LEAD : referenced_by
    TEAM_MEMBER ||--o{ LEAD : handles
    
    LEAD ||--o{ TRIP_ORGANIZER : managed_by
    TEAM_MEMBER ||--o{ TRIP_ORGANIZER : organizes
    
    LEAD ||--o| TRIP_FINANCE : tracks_finances
    
    CUSTOMER ||--o{ BOOKING : makes
    LEAD ||--o| BOOKING : converts_to
    PACKAGE ||--o{ BOOKING : booked_as
    
    BOOKING ||--o{ TRAVELER : includes
    BOOKING ||--o{ PAYMENT : has
    
    TEAM_MEMBER ||--o{ TASK : assigned_to
    LEAD ||--o{ TASK : has_task

```

## 5. Technical Stack Summary

### Frontend 
* **Framework:** React 18, Vite
* **Styling:** Tailwind CSS (Custom animations in `tailwind.config.js`)
* **Routing:** react-router-dom
* **State Management:** Native Hooks (`useState`, `useEffect`)

### Backend
* **Framework:** Python, Flask
* **ORM:** Flask-SQLAlchemy
* **CORS:** Flask-CORS for cross-origin API integration
* **Database:** Relational db (e.g. SQLite mapped by SQLAlchemy models)

### Key Architectural Decisions
1. **Separation of Concerns:** Clear boundary between the UI implementation detail and data persistence via API routes.
2. **REST Principles:** Usage of standard HTTP methods (GET, POST, etc.) for entity manipulation.
3. **Responsive & Animated UI:** Utilization of an Intersection Observer implementation alongside Tailwind transitions to enrich the user experience without sacrificing performance.
4. **Relational Data Mapping:** A highly normalized schema optimized for full travel operations involving customers, leads, bookings, payments, task management, financial costing, and tour packages representation.
