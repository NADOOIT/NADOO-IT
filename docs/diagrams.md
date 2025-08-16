# Diagrams

This page provides high-level diagrams clarifying key relationships and how UI roles/flags map to contracts.

## Contracts and Access Control (overview)

```mermaid
classDiagram
  class User { user_code }
  class Employee
  class Customer
  class EmployeeContract {
    +is_active: bool
    +start_date
    +end_date?
  }
  class EmployeeManagerContract {
    +can_add_employee: bool
    +can_delete_employee: bool
  }
  class CustomerProgramManagerContract {
    +can_create_program: bool
    +can_delete_program: bool
  }
  class CustomerProgramExecutionManagerContract {
    +can_create_execution: bool
    +can_delete_execution: bool
  }
  class TimeAccountManagerContract {
    +can_create_time_account: bool
    +can_delete_time_account: bool
  }
  class CustomerProgram
  class Execution

  User --> Employee : 1..1 (linked)
  Employee --> EmployeeContract : 0..*
  EmployeeContract --> Customer : 1

  %% Manager contracts extend rights on top of base access
  Employee --> EmployeeManagerContract : 0..*
  Employee --> CustomerProgramManagerContract : 0..*
  Employee --> CustomerProgramExecutionManagerContract : 0..*
  Employee --> TimeAccountManagerContract : 0..*

  Customer --> CustomerProgram : 0..*
  CustomerProgram --> Execution : 0..*
```

Notes
- Base visibility requires an active EmployeeContract between the Employee and the Customer.
- Manager contracts grant specific action rights on top of base visibility.

## UI Roles & Template Flags

The UI exposes flags derived from active contracts. This guides which templates render and which actions are shown.

```mermaid
flowchart TB
  subgraph Contracts
    EC[EmployeeContract active?]
    EMC[EmployeeManagerContract]
    CPMC[CustomerProgramManagerContract]
    CPEMC[CustomerProgramExecutionManagerContract]
    TAMC[TimeAccountManagerContract]
  end

  subgraph Flags
    V[has_visibility]
    FE[can_manage_employees]
    FP[can_manage_programs]
    FX[can_manage_executions]
    FT[can_manage_time_accounts]
  end

  EC --> V
  EMC --> FE
  CPMC --> FP
  CPEMC --> FX
  TAMC --> FT
```

Legend
- has_visibility: set when there is an active EmployeeContract for the relevant Customer
- Other flags map 1:1 to their respective manager contracts’ booleans

See also
- Contracts & Access Control: `contracts-and-access-control.md`
- UI Roles & Rights: `ui-roles-and-rights.md`
- Admin guide: `admin.md`
