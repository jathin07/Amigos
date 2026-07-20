# 00 Business Domain Knowledge
## Domain Architecture and Travel Agency CRM & Trip Management Operations

---

## 1. Introduction
Amigos Tourism is a **Travel Agency Management System** designed to digitize and simplify the daily operations of a travel agency.

The platform is not intended to function as only a travel booking website. Instead, it manages the complete lifecycle of a trip—from the moment a customer makes an enquiry until the trip is completed and its financial performance is analyzed.

The objective is to replace scattered spreadsheets, WhatsApp conversations, manual calculations, and paper records with a centralized system where all trip-related information is organized and easily accessible.

---

## 2. Business Vision
The long-term vision of Amigos Tourism is to become an integrated platform that enables the agency to manage:
- Customer enquiries
- Customer relationships (CRM)
- Customized trip planning
- Package management
- Booking management
- Team coordination
- Trip operations
- Vendor coordination
- Payment tracking
- Financial reporting
- Customer history

Every department of the agency should be able to work from a single system.

---

## 3. Business Objectives
The platform should help Amigos Tourism achieve the following objectives:

### Customer Management
- Capture every enquiry.
- Never lose customer information.
- Maintain customer history.
- Improve follow-up efficiency.

### Sales Management
- Understand customer requirements.
- Discuss and customize trips.
- Prepare proposals.
- Convert enquiries into bookings.

### Operations Management
- Organize every confirmed trip.
- Coordinate hotels, transport, and activities.
- Assign responsibilities to team members.
- Ensure smooth execution of trips.

### Financial Management
- Track customer payments.
- Track operational expenses.
- Calculate profit and loss.
- Generate business reports.

---

## 4. Nature of Business
Amigos Tourism operates as a travel agency that provides both predefined tour packages and fully customized travel experiences.

The agency handles trips of different sizes, ranging from individual travelers to large educational and corporate groups. The system should therefore be flexible enough to support different business scenarios without requiring separate applications.

---

## 5. Business Actors

### 5.1 Customer
The billing entity or primary purchaser of the trip services. A customer can be an individual traveler or represent an organization.

### 5.2 Organization
Corporate or institutional client entities (colleges, companies, schools) that organize recurring group trips.

### 5.3 Vendor
External partners providing logistics services (accommodations, transport operators, guides, event organizers).

### 5.4 Team Member & Business Roles
While users log in using team member accounts, they perform specific business roles:
- **Admin**: Oversees master data, revenue thresholds, payments, and system configurations.
- **Sales Executive / CRM Handler**: Handles customer calls, follows up on leads, and drafts custom proposals.
- **Operations Executive**: Assigns vendors, configures day-by-day trip details, and prepares checklists.
- **Trip Coordinator**: Executes logistics on the ground, checks checklist rows, and records on-trip expenses.

---

## 6. Customer Categories

- **Individual Traveler**: A single traveler planning a personal trip (solo, business, pilgrimage).
- **Couple / Honeymoon**: Two travelers planning romantic couple vacations.
- **Family**: Family groups planning combined vacations (including kids/grandparents).
- **Friends Group**: Trekking groups, bike riders, or friends travelling together.
- **College Industrial Visit (IV)**: Educational tours requiring department name, student strength, and faculty counts.
- **School Tour**: Educational school trips requiring school details, teacher-to-student ratios, and class grades.
- **Corporate Tour**: Businesses organizing annual team outings, employee reward trips, or engagement programs.
- **Association / Club Tour**: Sports clubs, Lions/Rotary clubs, and religious groups.
- **Custom Group Tour**: Family reunions, temple groups, or custom adventure clubs.

---

## 7. Lead Sources

Every enquiry received by Amigos Tourism is treated as a **Lead**.
- **Quick Booking**: A callback request with name, phone, and destination.
- **Plan My Trip**: A detailed form containing preferred destination, dates, budget, and special instructions.
- **Package Booking**: Enquiries associated with a predefined package catalog.
- **Google Forms**: Leads imported from external registration sheets (e.g. college IV events).
- **Admin Created Lead**: Manual lead entry for walk-ins, phone enquiries, or personal referrals.

---

## 8. Customer Journey

```text
Lead Created (CRM)
  ↓
Trip Requirement Discussion (CRM)
  ↓
Trip Plan / Itinerary Design (CRM)
  ↓
Proposal Created (Proposal)
  ↓
Proposal Approved (Finalized)
  ↓
Proposal Status Locked ("Waiting for Advance" - NO Booking exists yet)
  ↓
Advance Payment Received (Finance)
  ↓
Booking & Customer Profile Created (Booking)
  ↓
Operations Planning & Vendor Allocation (Operations)
  ↓
Preparation Checklist Completed (Operations)
  ↓
Trip Executed (Operations)
  ↓
Trip Completed & Finance Closed (Finance)
  ↓
Customer History Preserved (CRM)
```

---

## 9. Business Lifecycles

### 9.1 Lead Lifecycle
```text
New ──> Assigned ──> Contacted ──> Requirement Gathering ──> Proposal Sent ──> Negotiation ──> Won/Lost
```

### 9.2 Proposal Lifecycle
```text
Draft ──> Under Discussion ──> Revised ──> Approved ──> Waiting Advance ──> Converted ──> Archived
```

### 9.3 Booking Lifecycle
```text
Proposal Accepted ──> Waiting for Advance ──> Confirmed ──> Planning ──> Ready ──> Ongoing ──> Completed ──> Closed
```

### 9.4 Trip Lifecycle
```text
Planning ──> Ready ──> Started ──> Ongoing ──> Completed ──> Closed
```

---

## 10. Customer Relationship Management (CRM)
The CRM module manages the sales process prior to conversion. It focuses on logging client interactions, managing followups, and tracking assignment history.

---

## 11. Proposal Management
A proposal is the commercial representation of a customized trip plan prepared for a customer. It combines itinerary, pricing, inclusions, exclusions, and commercial terms into a single sales document. Revisions can occur continuously, but only one proposal version may be marked as the final approved document. Once finalized, the proposal status shifts to `WAITING_FOR_ADVANCE`. No Booking is created at this stage.

---

## 12. Booking Operations
A booking represents a committed customer. It is created and confirmed only **after** the first payment installment is received.
Booking generation triggers:
- Traveler metadata logs.
- Booking preserves a copy of important customer, package, and pricing information so historical records remain unchanged even if master information is updated later.
- Copying checklist items from checklist templates.

---

## 13. Operations Management
Operations starts only after financial commitment is validated. This guarantees operational work begins only after customer commitment:
```text
Booking Confirmed ──> Operations Owner Assigned ──> Trip Plan Day Schedules ──> Vendor Allocation ──> Checklist items ──> Trip Ready ──> Trip Execution
```
A Booking cannot transition to `Ready` status unless all checklist items are marked complete.

---

## 14. Vendor Management & Relationship Lifecycle
Vendors represent third-party operators. Confirmed vendor allocations cannot be modified without administrative approval. The vendor lifecycle follows:
```text
Vendor Onboarding (GST/Bank info)
  ↓
Services Quoted
  ↓
Price Negotiated
  ↓
Vendor Confirmed
  ↓
Allocated to TripDay
  ↓
Payment Disbursed
  ↓
Performance Rated
```

---

## 15. Finance Management
Finance handles cash flows. Finance is responsible for validating customer commitments before operational execution begins. It owns:
- Customer payments tracking against installments schedules.
- Vendor allocation payment tracking.
- Expense tracking (categorized under fuel, tolls, meals, homestays).
- Derived summaries: Revenue, operational expenses, refunds, profit margins, and outstanding balances.
- Finance Lock: Expense rows are locked from modifications once the parent Booking status is marked `Completed` or `Closed`.

---

## 16. Assignment Philosophy

Work inside Amigos is ownership-based. The assignment sequence flows:

```text
Lead Inception ──> Lead Owner (CRM Executive) ──> Operations Owner (Operations Executive) ──> Trip Coordinator ──> Task Assignee
```

Every assignment change is captured in `AssignmentHistory`.

---

## 17. Customer History
Completed bookings contribute to customer history. Maintaining repeat customer history (previous trips, preferred hotels, preferred vehicles, preferred payment patterns) enables the agency to speed up repeat bookings for colleges, schools, and corporate groups by auto-filling previous details and itinerary constraints.

---

## 18. Business Rules

1. **Advance before Booking**: No Booking record may exist before an advance payment has been validated.
2. **Single Final Proposal**: Multiple proposal drafts can coexist, but only one proposal can be marked final per lead.
3. **Immutable Proposals**: A proposal is locked and cannot be updated once a booking has been created from it.
4. **Operations Owner Assignment**: Every booking must have exactly one Operations Owner assigned to manage preparation checklists.
5. **Checklist Completions**: A booking cannot transition to `Ready` status unless all Checklist tasks are completed.
6. **Locked Allocations**: Confirmed vendor allocations cannot be modified without administrative approval.
7. **Expense Locking**: Expenses cannot be created, modified, or deleted once a trip status is `Completed` or `Closed`.
8. **Aggregation Reports**: Reports are generated from historical business data and do not modify operational records.

---

## 19. Core Business Invariants
1. Every enquiry becomes a Lead.
2. Every Lead has one Primary Contact Person.
3. Organizations are reusable entities.
4. Packages and Destinations are reusable reference models.
5. Every operational expense belongs to a booking.

---

## 20. Future Vision
As Amigos Tourism grows, the platform should evolve to include:
- Customer Portal
- Vendor Portal
- AI Trip Planner & AI Quote Generator
- Online Payments integration (Razorpay)
- WhatsApp & Email Automation
- GPS Trip Tracking & Mobile Coordinator App

---

## 21. Business Glossary

| Term | Meaning |
| :--- | :--- |
| **Lead** | A customer enquiry representing potential travel business. |
| **Proposal** | A sales quotation detailing customized itineraries and price offers. |
| **Booking** | A confirmed operational trip backed by customer payment. |
| **Traveler** | A person traveling on a booking trip. |
| **Customer** | The billing account or purchaser of the tour package. |
| **Organization** | An institutional client (college, school, company). |
| **ContactPerson** | The primary communicator representing the customer or organization. |
| **Vendor** | An external service provider (transport, hotel, activities). |
| **AssignmentHistory** | The audit log tracking change of ownership histories across modules. |
| **Trip Plan** | The execution plan detailing daily logistics schedules. |
