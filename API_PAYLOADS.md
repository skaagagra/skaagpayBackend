# Recharge & Bill Payment API Payloads

**Endpoint:** `POST /api/recharge/request/`
**Headers:** 
- `Content-Type: application/json`
- `X-User-ID: <user_id>` (Required for current MVP auth)

## 1. Mobile Recharge (Prepaid)
Use for standard mobile top-ups.

```json
{
  "mobile_number": "9876543210",
  "amount": 299.00,
  "operator": "Airtel",
  "category": "MOBILE_PREPAID"
}
```

## 2. DTH Recharge
Use for DTH payments.
*   **mobile_number**: Enter the Subscriber ID or VC Number here.
*   **operator**: Must be one of the configured DTH operators (e.g., "Airtel TV", "Tata Sky").

```json
{
  "mobile_number": "3000123456", 
  "amount": 450.00,
  "operator": "Tata Sky",
  "category": "DTH"
}
```

## 3. Green Gas Payment
Use for Green Gas Agra payments.
*   **mobile_number**: Enter the **CRN No.** here.
*   **operator**: MUST be "Green Gas Agra".
*   **category**: MUST be "GAS".

```json
{
  "mobile_number": "CRN12345678",
  "amount": 950.00,
  "operator": "Green Gas Agra",
  "category": "GAS"
}
```

## Field Descriptions
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mobile_number` | String | Yes | The Phone Number, DTH Subscriber ID, or CRN Number. |
| `amount` | Decimal | Yes | The amount to recharge/pay. |
| `operator` | String | Yes | Name of the operator (e.g., "Airtel", "Green Gas Agra"). |
| `category` | String | Yes | `MOBILE_PREPAID`, `DTH`, or `GAS`. |
