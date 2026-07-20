# 11 Dashboard DTOs
## Dashboard Widget and Panel Aggregated Data Responses

Dashboard endpoints return read-only DTOs for client panels.

---

## 1. Response DTOs

### 1.1 `SummaryCardsResponse`
```json
{
  "total_leads": 125,
  "total_bookings": 48,
  "monthly_revenue": 852000.00,
  "active_coordinators": 12
}
```

### 1.2 `LeadPipelineWidgetResponse`
```json
{
  "new_leads": 40,
  "proposal_sent": 25,
  "negotiation": 15,
  "won": 20
}
```

### 1.3 `RevenueWidgetResponse`
```json
{
  "monthly_target": 1000000.00,
  "revenue_collected": 852000.00,
  "outstanding_balance": 148000.00
}
```
