# API Reference (Initial)

This page documents the currently exposed API surface at a high level. It will be expanded as more endpoints are formalized.

Base URL (development)
- HTTPS: `https://127.0.0.1:8000/`

Authentication
- Certain endpoints require both an API key and a user code. For current endpoints, include them in the JSON body (not headers):
  - `NADOOIT__API_KEY`
  - `NADOOIT__USER_CODE`

Request format (quick)
- Send JSON in the request body with `Content-Type: application/json`.
- Place credentials in the JSON body, not in headers.
- Use HTTPS; in local dev you may use `-k` with curl to ignore self-signed certs.

Executions API
- Endpoint: `/api/executions`
- Method: typically `POST`
- Example payload:
  ```json
  {
    "NADOOIT__API_KEY": "<your-api-key>",
    "NADOOIT__USER_CODE": "<your-user-code>",
    "program_id": "<uuid>"
  }
  ```
- Notes:
  - Response structure and required fields may evolve; inspect the DRF browsable API in development to discover fields and test requests.
  - Ensure `DJANGO_DEBUG=1` in dev to use the browsable API.

Headers and content type
- Send `Content-Type: application/json`.
- These endpoints expect credentials in the JSON body, not in headers.

Authentication summary
- API keys are stored hashed; send the plaintext key in the JSON body. The server hashes and verifies it.
- The `NADOOIT__USER_CODE` must belong to the key’s user and that user must be active.
- Authorization for program actions depends on contracts: your user must have an active `EmployeeContract` with the customer that owns the program. See `docs/contracts-and-access-control.md`.

Endpoints

Create execution
- Path: `/api/executions`
- Method: POST
- Request JSON fields:
  - `NADOOIT__API_KEY` (string, required): plaintext key for the calling user
  - `NADOOIT__USER_CODE` (string, required): user code of the key owner
  - `program_id` (UUID string, required): ID of the target Customer Program
- Success response (200):
  ```json
  { "success": "Execution created" }
  ```
- Error responses:
  - 400 `{ "error": "Program does not exist" }` (unknown/missing program_id)
  - 400 `{ "error": "User is not an employee of the company" }`
  - 403 `{ "error": "Invalid API Key" }`
  - 403 `{ "error": "User code is not valid" }`
  - 403 `{ "error": "User is not active" }`
  - 400 `{ "error": "Invalid request" }` (malformed JSON/missing required fields)

Check user via API key
- Path: `/api/users/check`
- Method: POST
- Request JSON fields:
  - `NADOOIT__API_KEY` (string, required): plaintext key for the calling user
  - `NADOOIT__USER_CODE` (string, required): user code of the key owner
  - `NADOOIT__USER_CODE_TO_CHECK` (string, required): user code to verify
- Success response (200):
  ```json
  { "success": "User to check is active" }
  ```
- Not active (400):
  ```json
  { "success": "User to check is not active" }
  ```
- Error responses:
  - 403 `{ "error": "Your API Key is not valid" }`
  - 403 `{ "error": "Your User code is not valid" }`
  - 403 `{ "error": "Your User is not active" }`
  - 400 `{ "error": "User does not exist" }`
  - 400 `{ "error": "Invalid request" }`

curl examples

Create an execution
```bash
curl -k -X POST https://127.0.0.1:8000/api/executions \
  -H 'Content-Type: application/json' \
  -d '{
    "NADOOIT__API_KEY": "YOUR_PLAINTEXT_API_KEY",
    "NADOOIT__USER_CODE": "USERCODE123",
    "program_id": "11111111-2222-3333-4444-555555555555"
  }'
```

Check a user via API key
```bash
curl -k -X POST https://127.0.0.1:8000/api/users/check \
  -H 'Content-Type: application/json' \
  -d '{
    "NADOOIT__API_KEY": "YOUR_PLAINTEXT_API_KEY",
    "NADOOIT__USER_CODE": "OWNER_USERCODE",
    "NADOOIT__USER_CODE_TO_CHECK": "TARGET_USERCODE"
  }'
```

Behavior and constraints
- The plaintext API key you send is hashed server-side and matched against the stored hash.
- The `NADOOIT__USER_CODE` must match the user to whom the API key belongs, and that user must be active.
- For `/api/executions`, the user must be an active employee for the customer that owns the `program_id` (checked via `EmployeeContract`).
- `program_id` must refer to an existing program (`CustomerProgram`).

Conventions
- JSON request/response bodies
- Standard HTTP status codes
- Errors returned as JSON with a message and (optionally) field-level details

Common error codes
- 400 Bad Request: missing fields or invalid JSON. Ensure `Content-Type: application/json` and required fields are present.
- 400 Program does not exist: `program_id` is missing or not a valid existing program UUID.
- 403 Invalid API Key: plaintext key missing/incorrect for the provided `NADOOIT__USER_CODE`.
- 403 User code not valid/active: the user tied to the key is inactive or the code does not match the key owner.
- 415 Unsupported Media Type: wrong or missing `Content-Type` header.

Troubleshooting
- 403 Invalid API Key or User: ensure the plaintext key and correct `NADOOIT__USER_CODE` are in the JSON body. Confirm the user is active.
- 400 Program does not exist: verify `program_id` is a valid UUID of an existing program.
- 400 Invalid request: often caused by missing `NADOOIT__API_KEY` or `NADOOIT__USER_CODE` fields; ensure `Content-Type: application/json` and a proper JSON body.
- Use `curl -v` or the DRF browsable API (with `DJANGO_DEBUG=1`) to inspect requests.

Next steps
- Enumerate all available API endpoints with schemas and examples
- Add authentication scheme documentation per endpoint (payload vs header)
- Add versioning guidance if/when versions are introduced

See also
- Admin guide: `docs/admin.md` (creating API keys)
- Contracts & Access Control: `docs/contracts-and-access-control.md`
