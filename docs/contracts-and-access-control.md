# Contracts & Access Control

This guide explains how NADOO-IT controls who can see and do what using contracts. It covers the core HR models, manager contracts, and the practical rules used by the UI and APIs.

## Overview
- Access is centered on the relationship between a User (via `Employee`) and a `Customer`.
- An `EmployeeContract` grants the basic membership and visibility for a user within a customer’s context.
- Manager contracts extend an `EmployeeContract` with capabilities for specific domains (employees, programs, executions, time accounts, etc.).

Key code:
- Models: `app/nadooit_hr/models.py`
- Program ownership: `app/nadooit_program_ownership_system/models.py`
- API check example: `app/nadooit_api_executions_system/views.py`
- OS permissions and pages: `app/nadooit_os/views.py`

---

## Core models

User and Employee
- `User` holds identity and `user_code`.
- `Employee` (1:1 with User) represents the person in the HR system.

Customer
- From `nadooit_crm.Customer`.

EmployeeContract
- Links an `Employee` to a `Customer`.
- Fields (high-level):
  - `employee`, `customer`
  - `is_active` (bool), `start_date`, `end_date`, `deactivation_date`
- Meaning:
  - If `is_active=True`, the employee is currently part of the customer and gains visibility in that customer’s context.

---

## Manager contracts (capabilities)
Each manager contract is a `OneToOneField` to the underlying `EmployeeContract` and grants specific abilities via boolean fields and a `.get_abilities()` helper.

- EmployeeManagerContract
  - `can_add_new_employee`, `can_delete_employee`, `can_give_manager_role`
  - Use case: manage employees belonging to the same customer as the base contract.

- CustomerManagerContract
  - `can_give_manager_role` (customer-level delegation helper)

- CustomerProgramManagerContract
  - `can_create_customer_program`, `can_delete_customer_program`, `can_give_manager_role`
  - Use case: manage Customer Programs for the same customer.

- CustomerProgramExecutionManagerContract
  - `can_create_customer_program_execution`, `can_delete_customer_program_execution`, `can_give_manager_role`
  - Use case: manage program executions for the same customer.

- TimeAccountManagerContract
  - `can_create_time_accounts`, `can_delete_time_accounts`, `can_give_manager_role`
  - Use case: manage time accounts in the same customer.

Notes
- “Give manager role” booleans are used to delegate by creating corresponding manager contracts for other employees of the same customer.

---

## Access rules in practice

Visibility scope
- A user can view/act only within customers where they have an active `EmployeeContract`.
- UIs and services often derive roles with helpers like `get__user__roles_and_rights__for__http_request` (see `nadooit_os.views`).

Program ownership and executions
- `CustomerProgram.customer` links programs to a customer.
- To create an execution via API (`/api/executions`):
  1) API key and user must be valid/active.
  2) The user must have an active `EmployeeContract` for the program’s owning `customer`.
  - This check is implemented with an `EmployeeContract.objects.filter(..., is_active=True).exists()` query.

Managing employees
- Requires an `EmployeeManagerContract` on top of the base `EmployeeContract` for the same customer.
- Specific actions are gated by booleans (`can_add_new_employee`, `can_delete_employee`).

Managing customer programs
- Requires `CustomerProgramManagerContract` with `can_create_customer_program` / `can_delete_customer_program`.

Managing program executions
- Requires `CustomerProgramExecutionManagerContract` with `can_create_customer_program_execution` / `can_delete_customer_program_execution`.

Managing time accounts
- Requires `TimeAccountManagerContract` with `can_create_time_accounts` / `can_delete_time_accounts`.

Delegation
- Where available, `can_give_manager_role` allows the holder to assign manager contracts of the same type to other employees of the same customer.

---

## Permissions matrix (quick reference)

- Visibility within a Customer’s data
  - Required: Active `EmployeeContract` for that `Customer`.

- Manage employees (add/delete)
  - Required: `EmployeeManagerContract` on the same `EmployeeContract`.
  - Flags: `can_add_new_employee`, `can_delete_employee`.

- Manage customer programs (create/delete)
  - Required: `CustomerProgramManagerContract`.
  - Flags: `can_create_customer_program`, `can_delete_customer_program`.

- Manage program executions (create/delete)
  - Required: `CustomerProgramExecutionManagerContract`.
  - Flags: `can_create_customer_program_execution`, `can_delete_customer_program_execution`.

- Manage time accounts (create/delete)
  - Required: `TimeAccountManagerContract`.
  - Flags: `can_create_time_accounts`, `can_delete_time_accounts`.

- Delegate manager roles
  - Required: Corresponding manager contract with `can_give_manager_role=True`.

## Who can see what

- Customer
  - Any user with an active `EmployeeContract` for that `Customer`.

- CustomerProgram
  - Users with an active `EmployeeContract` for `CustomerProgram.customer`.

- CustomerProgramExecution
  - Users with an active `EmployeeContract` for the owning program’s `customer`.

- TimeAccount entities
  - Users with an active `EmployeeContract` for the associated customer; management requires `TimeAccountManagerContract`.

## Admin workflows

Grant base access (visibility)
1) Admin → HR → Employee: ensure the `Employee` exists and is linked to the correct `User`.
2) Admin → HR → Employee Contract: create a contract linking the `Employee` to the `Customer` and set `is_active=True`.

Grant management rights
1) Open the `EmployeeContract` (or go via the specific manager contract admin).
2) Create the appropriate manager contract:
   - EmployeeManagerContract, CustomerProgramManagerContract, CustomerProgramExecutionManagerContract, TimeAccountManagerContract, or CustomerManagerContract.
3) Toggle the capability booleans as required.

End a contract
- Set `is_active=False` and fill `deactivation_date` (or `end_date`) to remove access.
- Consider auditing any manager contracts linked to the base contract.

---

## Examples

- API program execution
  - Alice has an active `EmployeeContract` with ACME. ACME owns program P.
  - Alice’s API request to `/api/executions` with `program_id=P` succeeds (assuming API key and user are valid).
  - Bob, who lacks a contract with ACME or has `is_active=False`, receives `{"error": "User is not an employee of the company"}`.

- Delegation
  - Carol has a `CustomerProgramManagerContract` with `can_give_manager_role=True` at ACME.
  - Carol can grant another employee a `CustomerProgramManagerContract` at ACME.

---

## Delegation cookbook

Grant a manager role to another employee (same customer)
1) Ensure you (the delegator) have the corresponding manager contract with `can_give_manager_role=True` for the target customer.
2) Admin → HR → Employee: verify the target employee exists and has an active `EmployeeContract` for the same customer.
3) Admin → HR → [Manager Contract Type]: create a manager contract linked to the target’s `EmployeeContract`.
4) Enable the specific capability booleans needed (e.g., `can_create_customer_program`).

Revoke delegated rights
1) Open the target’s manager contract (e.g., `CustomerProgramManagerContract`).
2) Toggle off capability booleans or delete the manager contract.
3) If the base access should end, set `is_active=False` on the target’s `EmployeeContract` and set `deactivation_date`.

Audit delegation
- Filter manager contracts by customer to see who currently holds rights.
- Periodically verify that holders still require access; remove stale delegations.

## Troubleshooting
- I cannot see a customer’s data
  - Ensure there is an `EmployeeContract` for that customer and `is_active=True`.
  - Check `end_date` / `deactivation_date` and whether the contract is expired.

- API error: "User is not an employee of the company"
  - The `program_id` belongs to a `Customer` without an active `EmployeeContract` for your user. Create/activate the contract.

- Manager actions disabled
  - Confirm the relevant manager contract exists and the correct boolean capability is set to True.

---

## See also
- Admin Guide: `docs/admin.md`
- API Reference: `docs/api.md`
- Apps & Services Catalog: `docs/apps-and-services.md`
 - Diagrams: `docs/diagrams.md`
