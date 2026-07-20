# 06 DTO Specification
## Index Registry of Modular Request & Response Data Transfer Objects

To maintain modular clean architectures and prevent large document bloating, the Request and Response DTO structures are partitioned across 15 separate files organized under the `docs/api-specification/` directory:

---

## 1. DTO Specification Documents Registry

1. **[00_api_standards.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/00_api_standards.md)**: 
   Defines global conventions, response/error envelopes, pagination query standards, and decimals formats.
2. **[01_shared_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/01_shared_dtos.md)**: 
   Contains reusable component templates (`PaginationMeta`, `Money`, `FileAttachment`, `Address`, `AuditInfo`).
3. **[02_auth_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/02_auth_dtos.md)**: 
   Detailed request/response contracts for authentications and credentials management.
4. **[03_master_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/03_master_dtos.md)**: 
   Catalogs, reference fields, and the aggregate package creation models.
5. **[04_crm_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/04_crm_dtos.md)**: 
   Leads enquiries, activities logger schemas, and followup tasks.
6. **[05_proposal_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/05_proposal_dtos.md)**: 
   Customized itinerary proposals and versioning restoration models.
7. **[06_booking_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/06_booking_dtos.md)**: 
   Aggregate booking logs, traveler profiles, payments schedule, and document attachments.
8. **[07_operations_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/07_operations_dtos.md)**: 
   Trip logistics, planning activity day-wise details, checklist items, and coordinator tasks.
9. **[08_finance_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/08_finance_dtos.md)**: 
   Logs for trip expenses, outstanding balances, and gross margins summaries.
10. **[09_assignment_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/09_assignment_dtos.md)**: 
    Workload handovers mapping and `AssignmentHistory` tracking audits.
11. **[10_notification_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/10_notification_dtos.md)**: 
    Notification payloads and delivery preferences settings.
12. **[11_dashboard_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/11_dashboard_dtos.md)**: 
    Pre-aggregated metric charts and pipeline widgets DTO templates.
13. **[12_report_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/12_report_dtos.md)**: 
    Asynchronous reporting summaries formats.
14. **[13_lookup_dtos.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/13_lookup_dtos.md)**: 
    Selector lookups for lead source types and payment method codes.
15. **[14_common_actions.md](file:///c:/Users/jathi/workspace/amigos/docs/api-specification/14_common_actions.md)**: 
    Workflow action DTOs (`ConfirmBookingRequest`, `CancelBookingRequest`, `MarkTripReadyRequest`).

---

## 2. API Development Order
Modular DTO structures match the backend development pipeline:
```text
Auth (02) ──> Master Data (03) ──> CRM (04) ──> Proposals (05) ──> Bookings (06) ──> Assignments (09) ──> Operations (07) ──> Finance (08)
```
