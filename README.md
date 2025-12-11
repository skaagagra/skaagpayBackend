# Skaagpay Backend

A Django-based backend for a mobile recharge application with wallet facility.

## Features
- **Phone Login**: Simple authentication using phone numbers.
- **Wallet System**: Top-up via screenshot verification (Admin approved).
- **Recharge**: Immediate and Scheduled mobile recharges.

## API Endpoints

### Headers
For all authenticated requests, pass the user ID in the header (MVP Auth):
`X-User-ID: <USER_ID>`

### Authentication
#### 1. Login / Register
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "phone_number": "9876543210"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Login Successful",
    "user": { "id": 1, "phone_number": "...", ... }
  }
  ```

#### 2. User Profile
- **URL**: `/api/auth/profile/`
- **Method**: `GET`, `PATCH`
- **Header**: `X-User-ID: <USER_ID>`
- **Payload (PATCH)**:
  ```json
  {
    "full_name": "John Doe",
    "address": "123 Main St",
    "fcm_token": "<DEVICE_TOKEN>"
  }
  ```

### Wallet
#### 1. Get Balance
- **URL**: `/api/wallet/balance/`
- **Method**: `GET`

#### 2. Request Top-Up
- **URL**: `/api/wallet/topup/`
- **Method**: `POST`
- **Body** (form-data):
  - `amount`: `500.00`
  - `screenshot`: [File Upload]

#### 3. Transaction History
- **URL**: `/api/wallet/transactions/`
- **Method**: `GET`

### Recharge
#### 1. Submit Recharge (Immediate)
- **URL**: `/api/recharge/request/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "mobile_number": "9998887776",
    "operator": "Jio",
    "amount": 199.00
  }
  ```

#### 2. Schedule Recharge
- **URL**: `/api/recharge/request/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "mobile_number": "9998887776",
    "operator": "Jio",
    "amount": 199.00,
    "is_scheduled": true,
    "scheduled_at": "2025-12-11T05:00:00Z"
  }
  ```
  *Note: Balance is NOT deducted immediately. It is deducted when the schedule runs.*

## Scheduled Recharge Processing
To process scheduled recharges, a management command is provided. This should be set up as a Cron job or Scheduled Task (e.g., to run every hour or every day at 5 AM).

**Command:**
```bash
python manage.py process_recharges
```

**Logic:**
1. Finds all recharges with status `SCHEDULED` and `scheduled_at <= NOW`.
2. Checks user's wallet balance.
3. If sufficient: Deducts balance -> Marks `PENDING` (for admin processing).
4. If insufficient: Marks `FAILED`.

## Admin Panel
- Access at: `/admin/`
- **Wallet TopUp Requests**: View screenshots and change status to `APPROVED` to credit wallets.
- **Recharge Requests**: View all requests.
