# UI Roles & Rights

This page documents the template context flags that control what the UI shows and which pages are accessible. These flags are derived from contracts (see `docs/contracts-and-access-control.md`).

Source:
- `get__user__roles_and_rights__for__http_request(request)` in `app/nadooit_os/views.py`
- Decorators like `@user_passes_test(user_is_Time_Account_Manager, ...)` gate page access

## Context flags exposed to templates
The following keys are injected into template contexts via `get__user__roles_and_rights__for__http_request`:

- `is_time_account_manager`
- `user_is_Time_Account_Manager_and_can_give_manager_role`
- `is_api_key_manager`
- `user_is_api_key_manager_and_can_give_manager_role`
- `is_employee_manager`
- `user_is_Employee_Manager_and_can_give_Employee_Manager_role`
- `user_is_Employee_Manager_and_can_add_new_employee`
- `is_customer_program_manager`
- `user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role`
- `is_customer_program_execution_manager`
- `user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role`

These booleans are computed from manager contracts on top of an active `EmployeeContract`.

## Mapping to contracts
- Time accounts
  - `is_time_account_manager` → `TimeAccountManagerContract`
  - `user_is_Time_Account_Manager_and_can_give_manager_role` → same contract with `can_give_manager_role=True`
- API keys
  - `is_api_key_manager` → API key management right (via HR role checks)
  - `user_is_api_key_manager_and_can_give_manager_role` → delegation boolean for API key managers
- Employees
  - `is_employee_manager` → `EmployeeManagerContract`
  - `user_is_Employee_Manager_and_can_give_Employee_Manager_role` → `can_give_manager_role=True`
  - `user_is_Employee_Manager_and_can_add_new_employee` → `can_add_new_employee=True`
- Programs
  - `is_customer_program_manager` → `CustomerProgramManagerContract`
  - `user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role` → `can_give_manager_role=True`
- Program executions
  - `is_customer_program_execution_manager` → `CustomerProgramExecutionManagerContract`
  - `user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role` → `can_give_manager_role=True`

For full semantics of these contracts and capabilities, see `docs/contracts-and-access-control.md`.

## Where they are used
- Page rendering: flags are included in many OS pages to control visibility of buttons/links and sections.
- Access control: some views are additionally protected by `@user_passes_test` decorators that call the same underlying checks (e.g., `user_is_Time_Account_Manager`).

Examples in code:
- Time account overview view uses `@user_passes_test(user_is_Time_Account_Manager, ...)` and merges role flags into the context.
- OS index page merges the full roles dict so templates can conditionally render options.

## How to test roles locally
1) Ensure your `User` has an `Employee` and an active `EmployeeContract` for a test customer.
2) In admin, create the relevant manager contract and enable the capability booleans.
3) Visit OS pages (e.g., `/nadooit-os/`) and verify the presence/absence of controls.
4) For gated pages (like time account overview), confirm access with and without the required contract.

## Troubleshooting
- A button or section is missing
  - Confirm the corresponding `is_*` flag is true by printing the context or using the Django shell.
  - Verify the underlying manager contract exists and has the required booleans set.
- Access denied to a page
  - The view is likely decorated with `@user_passes_test(...)`. Ensure your manager contract satisfies the check.

## See also
- Contracts & Access Control: `docs/contracts-and-access-control.md`
- Admin Guide: `docs/admin.md`
