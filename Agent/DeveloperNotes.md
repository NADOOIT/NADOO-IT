# NADOO-IT Developer Notes

## Project Overview
- **Purpose**: Execution Management System
- **Key Components**:
  - Provides a website interface
  - Hosts an API
  - Manages system execution

## Module Spotlight: CRM (`nadooit_crm`)
- **Purpose:** Manages customer information.
- **Key Models:**
    - `Customer`: Stores customer name.
    - `Address`: Generic address details (street, town, postal code).
    - `ShippingAdress` (Typo): Links Customer to a shipping Address.
    - `BillingAdress` (Typo): Links Customer to a billing Address.
- **Data Handled:** Contains Personally Identifiable Information (PII) like names and addresses.
- **Considerations:**
    - Security: Requires careful access control and potential encryption due to PII.
    - Data Integrity: Uses `SET_NULL` on address deletion.
    - Naming: Contains typos (`Adress` vs. `Address`) in class/field names.

## Module Spotlight: HR (`nadooit_hr`) & Permissions
- **Purpose:** Manages employee information and acts as a hub for a complex, contract-based permissions system.
- **Key Models:**
    - `Employee`: Links to a `User` account.
    - `EmployeeContract`: Defines the relationship between an `Employee` and a `Customer`.
    - **Permission Contracts** (e.g., `EmployeeManagerContract`, `CustomerProgramManagerContract`, etc.): Linked to `EmployeeContract`, these grant specific granular permissions across different application modules (Programs, Time Accounts, etc.) within the context of an employee-customer relationship.
- **Data Handled:** Contains sensitive employee and contract information.
- **Considerations:**
    - **Permissions Complexity:** The permissions model is intricate, defined by multiple contract types tied to Employee-Customer relationships. Auditing and managing these permissions requires careful attention.
    - **Security:** High importance due to sensitive data and its central role in authorization.
    - **Cascading Deletes:** Extensive use of `on_delete=CASCADE` means deleting core records (User, Employee, Customer, EmployeeContract) can trigger widespread data deletion, including permission grants.
    - Code Maintenance: Contains TODOs indicating planned refactoring.

## Module Spotlight: Program (`nadooit_program`)
- **Purpose:** Defines and manages 'programs' which appear to be core entities referenced by other system components and managed via HR permission contracts.
- **Key Models:**
    - `Program`: Contains a name, description, and a text field for `program_dependencies` (stored as a list of strings).
- **Considerations:**
    - **Dependency Management:** Storing dependencies as a string list in a `TextField` is flexible but could lead to issues with data integrity, querying, and error proneness. A relational approach (e.g., ManyToManyField) might be more robust for complex dependency graphs.
    - Central Entity: Programs likely serve as key reference points for workflows, executions, and time tracking, with access and management controlled by the granular permissions defined in `nadooit_hr`.

## Module Spotlight: API Executions System (`nadooit_api_executions_system`)
- **Purpose:** Tracks the execution of customer-specific program instances, focusing on quantifying their value/cost in terms of time saved and financial metrics.
- **Key Models:**
    - `CustomerProgramExecution`: Records details of a program execution, including `program_time_saved_in_seconds`, `price_per_second_at_the_time_of_execution`, `price_for_execution`, and `payment_status`. Links to a `CustomerProgram` from the `nadooit_program_ownership_system`.
- **Integrations & Features:**
    - **Financial Tracking:** Uses `djmoney` for robust handling of monetary values associated with executions.
    - **Time Accounting Link (via commented signals):** Commented-out Django signals suggest that program executions were intended to directly impact a `time_balance_in_seconds` on a customer's program-specific time account (likely in `nadooit_time_account`). This indicates a system for tracking consumable time credits or benefits.
    - **Ownership Context:** Executions are tied to `CustomerProgram` instances, implying programs are provisioned or customized per customer.
- **Considerations:**
    - **Commented Logic:** The presence of commented-out signal handlers for time account adjustments is significant. Understanding why they are commented out (e.g., feature temporarily disabled, refactored elsewhere, or abandoned) is crucial.
    - **Billing/ROI Focus:** The model structure strongly suggests a mechanism for billing based on program usage or demonstrating ROI through time savings.

## Module Spotlight: Time Account (`nadooit_time_account`)
- **Purpose:** Manages time-based balances for customers and tracks employee work time.
- **Key Models:**
    - `TimeAccount`: Core model holding a `time_balance_in_seconds`.
    - `CustomerTimeAccount`: Links a `TimeAccount` to a `Customer`, likely for tracking consumable program time/credits.
    - `EmployeeTimeAccount`: Links a `TimeAccount` to an `Employee` and `Customer`, for employee-specific time tracking in a customer context.
    - `WorkTimeAccountEntry`: Records clock-in/out (`entry_trype`) entries against an `EmployeeTimeAccount`.
- **Integrations & Features:**
    - **Consumable Balances:** `CustomerTimeAccount` is the likely target for debits/credits from `CustomerProgramExecution` (as per commented signals in `nadooit_api_executions_system`).
    - **Employee Time Clock:** `WorkTimeAccountEntry` provides a standard employee time tracking mechanism.
    - **`logic.py`:** Existence of `logic.py` hints at more complex business logic for time calculations or operations.
- **Considerations:**
    - **Dual Functionality:** The module serves both as a system for consumable time credits and for traditional employee time logging.
    - **Data Integrity:** `on_delete=CASCADE` is prevalent; care needed with deletions of core entities.
    - Typo: `entry_trype` field in `WorkTimeAccountEntry`.

## Module Spotlight: Program Ownership System (`nadooit_program_ownership_system`)
- **Purpose:** Manages how `Program` entities are instantiated, configured, and priced for specific `Customer`s, and links them to `TimeAccount`s.
- **Key Models:**
    - `CustomerProgram`: Central model linking a `Program` to a `Customer`. Defines customer-specific attributes like `program_time_saved_per_execution_in_seconds`, `price_per_second`, and associates with a `TimeAccount`. This is the entity referenced by `CustomerProgramExecution`.
    - `ProgramShare`: Its exact purpose is unclear from the model alone; might relate to program templates or a different sharing mechanism. Needs further investigation.
- **Integrations & Features:**
    - **Customer-Specific Configuration:** Allows tailoring programs (time saved, pricing) per customer.
    - **Financial Calculation:** Includes logic for `price_per_execution()`.
- **Considerations & TODOs:**
    - **`CustomerProgram.time_account` Limitation (TODO):** A critical `TODO` comment in the code indicates the current `ForeignKey` from `CustomerProgram` to `TimeAccount` is a design flaw, as a customer program should ideally link to multiple time accounts. This requires refactoring (likely to a ManyToManyField).
    - **Unclear `ProgramShare` Role:** The function of `ProgramShare` needs clarification.

## Module Spotlight: Workflow (`nadooit_workflow`)
- **Purpose:** Defines and manages customer-specific processes (workflows) that can be chained together and can execute a list of `CustomerProgram` instances.
- **Key Models:**
    - `Process`: Represents a workflow. It links to a `Customer`, can trigger and be triggered by other `Process` instances, and importantly, has a ManyToManyField to `CustomerProgram` (from `nadooit_program_ownership_system`) named `list_of_nadooit_programs`.
- **Integrations & Features:**
    - **Process Chaining:** Allows creation of sequences of processes via `trigger_process` (incoming) and `tiggers_process` (outgoing, likely typo for `triggers_process`) relationships.
    - **Orchestrates Customer Programs:** A `Process` can involve multiple `CustomerProgram` instances, suggesting it orchestrates their execution in a defined sequence or context for a customer.
    - **Customer-Specific:** Workflows are explicitly tied to a `Customer`.
- **Considerations & TODOs:**
    - **Typo:** `tiggers_process` field in the `Process` model should likely be `triggers_process`.
    - **Trigger Mechanism Evolution:** Commented-out fields suggest a past or alternative trigger mechanism based on events/subscriptions.

## Module Spotlight: Bot Management (`bot_management`)
- **Purpose:** Manages bots for various messaging platforms (Telegram, WhatsApp, etc.), enabling AI-powered interactions with customers and linking to CRM/ERP.
- **Key Models:**
    - `Bot` & `BotPlatform`: Defines a bot for a `Customer` and configures it for specific platforms with credentials (`access_token`).
    - `User` & `Chat`: Represent platform-specific users and chats.
    - `Message`: Central model for text, voice (`Voice`, `VoiceFile`), and photo (`PhotoMessage`, `TelegramPhoto`) messages, linked to a `Customer` and `BotPlatform`.
    - `APIKey`: Allows generating API keys for `BotPlatform` instances.
    - `Advertisement`: Links an `Item` (from `nadoo_erp`) to `Message`s for promotional purposes.
- **Integrations & Features:**
    - **Multi-Platform:** Designed for Telegram, WhatsApp, with others planned.
    - **AI Integration Hinted:** File structure (`core/gpt4.py`, `core/wisper.py`) suggests use of GPT-4 and Whisper for advanced text/speech processing.
    - **Media Handling:** Supports voice and photo messages with file storage.
    - **Customer & ERP Links:** Interactions are tied to `Customer` records, and advertisements link to `nadoo_erp.Item`.
- **Considerations & TODOs:**
    - **Security of Access Tokens:** `BotPlatform.access_token` stores sensitive credentials; their protection (encryption at rest, transit, logging, rotation) is critical.
    - **Typo:** Directory `plattforms` should likely be `platforms`.

## Module Spotlight: Complaint Management (`nadoo_complaint_management`)
- **Purpose:** Allows internal employees (`customer_program_execution_manager`) to file complaints regarding specific `CustomerProgramExecution` instances, presumably directed towards the program creators/owners.
- **Key Models:**
    - `Complaint`: The central model capturing the complaint details.
        - `ComplaintStatus`: Nested choices for status (Open, In Progress, Closed, Rejected).
        - Links to `CustomerProgramExecution` (the subject) and `Employee` (the reporter).
        - Contains the `complaint` text.
- **Integrations & Features:**
    - Integrates with `nadooit_api_executions_system` and `nadooit_hr`.
    - Provides a basic workflow for tracking complaint status.
- **Considerations & TODOs:**
    - **Access Control:** The `complaint` text can be sensitive; review access controls for viewing/managing complaints.
    - **Recipient:** The implicit recipient is the program creator; the system needs logic to route/notify them.
    - **Potential Enhancements:** Assignment tracking, communication log, severity/priority fields.

## Module Spotlight: ERP (`nadoo_erp`)
- **Purpose:** Manages basic product or inventory items.
- **Key Models:**
    - `Item`: Stores details like description, price, quantity, location, and links (product page, image).
        - Has an optional `ForeignKey` to `nadooit_crm.Customer`, suggesting items can be customer-specific or listed by customers.
- **Integrations & Features:**
    - Referenced by `bot_management.Advertisement`, allowing bots to advertise ERP items.
    - The customer link could enable targeted advertising or customer-specific catalogs.
- **Considerations & TODOs:**
    - **Clarify `Item.customer` Link:** Understand the exact business logic behind associating an `Item` with a `Customer`.
    - **Content Validation:** `link` and `img_link` fields should be validated to prevent pointing to malicious external content.

## Module Spotlight: Delivery (`nadooit_delivery`)
- **Purpose:** Intended to manage customer orders and their line items.
- **Key Models (Currently Broken):**
    - `Order`: Links to a `Customer` and has standard timestamps.
    - `OrderItem`: Links to an `Order`, specifies a `quantity`, and crucially, has a **broken `ForeignKey` to an undefined `Product` model.**
- **Integrations & Features (Intended):**
    - Links to `nadooit_crm.Customer`.
    - Expected to link to a product model (likely `nadoo_erp.models.Item`).
- **Critical Issues & TODOs:**
    - **Undefined `Product` Model:** `OrderItem.product` FK is broken. This prevents migrations and use of the module. It likely needs to point to `nadoo_erp.models.Item`.
    - **Missing Migrations:** No `0001_initial.py` likely due to the model error.
- **Considerations:**
    - **PII:** Customer order history is sensitive.

## Module Spotlight: Funnel (`nadooit_funnel`)
- **Purpose:** Intended for sales/conversion funnel management (inferred from name).
- **Key Models:** None defined. The `models.py` file is empty.
- **Integrations & Features:** None implemented.
- **Critical Issues & TODOs:**
    - **Placeholder Module:** This module is currently a placeholder with no defined models or functionality.
    - **Future Development:** If funnel tracking is required, this module needs to be designed and implemented.

## Module Spotlight: Key Management Permissions (`nadooit_key`)
- **Purpose:** Defines a `KeyManager` role for employees, granting them specific permissions to manage "keys" (e.g., API keys from `nadooit_api_key`) and other `KeyManager` instances.
- **Key Models:**
    - `KeyManager`: Links one-to-one with `nadooit_hr.Employee`. Contains boolean fields for permissions like `can_create_keys`, `can_delete_keys`, and `can_create_key_managers`.
- **Integrations & Features:**
    - Integrates with `nadooit_hr.Employee`.
    - Provides a permissions layer for managing "keys" defined in other modules (e.g., `nadooit_api_key`).
    - Allows for delegation of key management responsibilities and even `KeyManager` creation rights.
- **Considerations & TODOs:**
    - **Security Critical:** This module is central to controlling who can manage potentially powerful keys.
        - Initial bootstrapping of `KeyManager` roles needs review.
        - Audit trails for `KeyManager` permission changes are recommended.
        - Enforcement of these permissions in the actual key management logic (elsewhere) is crucial.
    - **Typo:** `key_managers_assigened_by_this_key_manager` field name.
    - **Scope of "Keys":** Clarify exactly which types of "keys" these permissions apply to.

## Module Spotlight: Network, Social & Economy Features (`nadooit_network`)
- **Purpose:** Implements features for social networking (friends, groups, guilds) and a basic in-app economy (money, program shares).
- **Key Models:**
    - `NadooitInventory`: Holds "money" and `ProgramShare` objects.
    - `NadooitNetworkMember`: Links a `User` to an `NadooitInventory`.
    - `NadooitNetworkFriendslist`: Manages friend connections between `NadooitNetworkMember`s.
    - `NadooitNetworkGroup`: Small, user-created groups (commented limit of 10 members, not enforced).
    - `NadooitGuild`: Larger, formal groups (guilds/clans) with members, roles, and a logo.
    - `NadooitNetworkGuildMember`: Defines a member's role within a `NadooitGuild`.
    - `NadooitGuildBank`: Links a `NadooitGuild` to a `NadooitInventory` (its collective bank).
- **Integrations & Features:**
    - Links to `nadooit_auth.User` and `nadooit_program_ownership_system.ProgramShare`.
    - Provides infrastructure for friends, groups, and guilds.
    - Introduces an economic layer with "money" and program shares.
- **Considerations & TODOs:**
    - **Bugs in `__str__` methods:** Several models have `__str__` methods that will raise `AttributeError`s (`NadooitNetworkFriendslist`, `NadooitNetworkGuildMember`).
    - **Unenforced Group Member Limit:** The 10-member limit for `NadooitNetworkGroup` needs model-level validation if strict.
    - **`NadooitGuildBank` Design:** Clarify if it's just a collective guild inventory or if per-user contributions are intended (requiring redesign).
    - **Complexity & Security:** This module adds significant complexity. The economic system (`NadooitInventory`) requires careful implementation to ensure transactional integrity and prevent abuse. Privacy of social connections needs consideration.

## Module Spotlight: Central Operations & Admin Hub (`nadooit_os`)
- **Purpose:** Acts as a centralized, role-based administrative and operational interface for many other modules within the NADOO-IT system. It does not define its own database models but orchestrates data and actions from other apps.
- **Key Features & Functionality (via `views.py` and `services.py`):
    - **Role-Based Access Control (RBAC):** Extensive use of functions to check user roles based on `nadooit_hr` contracts and other specific manager roles (e.g., `TimeAccountManager`, `ApiKeyManager`, `CustomerProgramExecutionManager`).
    - **Main Dashboard (`index_nadooit_os`):** Likely the central landing page.
    - **Management Interfaces for Other Modules:** Provides views for managing/overseeing:
        - Time Accounts (`nadooit_time_account`)
        - API Keys (creation/revocation, potentially linking to `nadooit_key` or `nadooit_api_key`)
        - Customer Program Executions (`nadooit_api_executions_system`), including complaints and data export.
        - Customer Programs (`nadooit_program_ownership_system`)
        - HR/Employee data (`nadooit_hr`), including contract activation/deactivation.
    - **Role Granting Capabilities:** Views dedicated to granting various manager roles to users.
    - **Service Layer:** Heavily relies on `nadooit_os.services.py` for business logic.
    - **UI Components:** Includes Django templates and custom template tags for presentation.
- **Integrations:**
    - `nadooit_hr` (Employee, various Contract models)
    - `nadooit_api_executions_system` (CustomerProgramExecution)
    - `nadooit_auth` (User)
    - Likely `nadooit_key` or `nadooit_api_key` (for API key management logic).
- **Considerations & TODOs:**
    - **Security Critical:** Due to its central role and permission-granting capabilities, this module requires rigorous security auditing of its RBAC checks, views, and especially the underlying service functions.
    - **Complexity in `services.py`:** The `services.py` file is expected to be large and contain critical business logic; it warrants a detailed review.
    - **API Key Management Link:** The `user_is_Api_Key_Manager` check suggests a link (e.g., `OneToOneField` reverse relation) from `Employee` to a model like `nadooit_key.KeyManager` (named `nadooitapikeymanager` in the code).

## Module Spotlight: Q&A Management (`nadooit_questions_and_answers`)
- **Purpose:** Stores question-answer pairs and provides an API for users (linked to `nadooit_website` sessions) to submit questions.
- **Models:**
    - `Question_Answer`: Stores `question_answer_id` (UUID PK), `question_answer_date`, `question_answer_question` (TextField, blank=True), `question_answer_answer` (TextField, blank=True).
- **Admin Interface:**
    - `Question_Answer` model is registered with the default Django admin.
- **API & Views (`views.py`, `urls.py`):
    - `submit_question(request, session_id)` view mapped to `your_question_we_answer/question/<str:session_id>/`.
        - Accepts POST requests (JSON body with "question") to submit a new question.
        - Uses `@csrf_exempt` (security concern).
        - Validates `session_id` using `nadooit_website.services.check__session_id__is_valid`.
        - If valid, creates a `Question_Answer` entry (answer is blank) and increments `session_score` on the `nadooit_website.Session` model by 100.
- **Integrations:**
    - `nadooit_website`: For session validation (`Session` model, `check__session_id__is_valid` service) and session scoring.
- **Considerations & TODOs:**
    - **Security (`@csrf_exempt`):** The `submit_question` view uses `@csrf_exempt`. This needs review; standard CSRF protection or token-based auth for APIs is generally preferred.
    - **Model Enhancements:**
        - **Required Fields:** Consider if question/answer should be non-blank.
        - **Categorization/Tagging:** No current way to categorize Q&As.
        - **User Association:** No link to user who asked/answered.
        - **Context:** No field for the source/context of the Q&A.
        - **`__str__` method:** Could be improved for very long questions/answers.
    - **API Enhancements:**
        - **Error Handling:** Improve error handling for malformed requests in `submit_question`.
        - **Atomic Updates:** Use `F()` expressions for `session_score` update to prevent race conditions.
    - **Admin Enhancements:** Custom `ModelAdmin` for better usability (list_display, search_fields, etc.).
    - **No Public Display:** No views currently to display Q&As to end-users; implies this is handled elsewhere or only via admin.

## Module Spotlight: Core Website & Personalization Engine (`nadooit_website`)
- **Purpose:** Manages the main website's content, structure, user session tracking, video delivery (including HLS), and implements A/B testing and personalization features. It also seems to collect data for potential ML applications.
- **Key Model Groups:**
    - **Content Management:**
        - `Section`: Core content unit (HTML, optional video/file, categories).
        - `Plugin`: Reusable HTML components.
        - `File`: Manages downloadable files.
        - `Category`: For classifying sections (e.g., based on engagement metrics).
    - **Video Management:**
        - `Video`: Handles original video uploads, preview images. Custom save logic renames/deletes files directly on the filesystem.
        - `VideoResolution`: Stores different resolutions for videos, including HLS playlist files. Custom save logic also directly manipulates filesystem for cleanup.
        - `RenameFileStorage`: Custom storage to rename uploaded files with UUIDs.
    - **User Tracking & Session Management:**
        - `Visit`: Logs simple site visits.
        - `Session`: Detailed user session tracking (ID, start time, duration, shown sections, interaction time, bot detection, score, A/B testing variant/category). *This model's `session_score` is used by `nadooit_questions_and_answers`.*
        - `Signals_Option` (typo): Defines types of user interaction signals.
        - `Session_Signal`: Records specific signals within a session related to a section.
    - **A/B Testing, Personalization & Ordering:**
        - `Section_Order`: Defines the sequence of sections presented to users, can include plugins.
        - `Section_Order_Sections_Through_Model`: Ordered M2M through model for `Section_Order` and `Section`.
        - `ExperimentGroup`: Manages A/B test groups, tracks success ratios.
        - `SectionScore`: Associates a score and experiment group (control/experimental) with sections.
        - `Section_Transition`: Models transitions between sections (e.g., section A to B) with a percentage. **Critical Issue:** Uses raw UUIDFields for section IDs instead of ForeignKeys.
        - `Section_Transition_Test`: Records tests for section transitions. Has typo `section_was_pased`.
        - `Section_Competition`: Groups transition tests for comparison.
- **Integrations:**
    - `nadooit_questions_and_answers`: Updates `Session.session_score`.
    - Likely `ordered_model` library for `Section_Order_Sections_Through_Model`.
- **Considerations & TODOs:**
    - **CRITICAL - Filesystem Manipulation:** `Video.save()` and `VideoResolution.save()` use direct `os.remove/rename/makedirs` and `shutil.rmtree`. This is risky and bypasses Django's storage API. **Refactor** to use Django storage API and signals for cleanup.
    - **CRITICAL - Referential Integrity:** `Section_Transition.section_1_id` and `Section_Transition.section_2_id` **must be `ForeignKey` fields** to `Section`, not raw `UUIDField`s.
    - **Typos:** Correct `Section.greeting_sction`, `Signals_Option` class name, `Section_Transition_Test.section_was_pased`.
    - **Security - File Uploads:** Ensure robust validation for all file uploads (`Video`, `VideoResolution`, `File`).
    - **Security - HTML Content:** If `Section.html` or `Plugin.html` can be user-influenced, ensure XSS protection/sanitization.
    - **Transaction Safety:** Consider wrapping `Video.save()` in `@transaction.atomic` due to its file operations.
    - **TrainingData Directory:** Presence of `TrainingData/` (`embeddings.npy`, `session_data.txt`) implies ML/data processing features, which would need separate review if in scope.
    - **`admin.py` Structure:** Has an `admin/` subdirectory, suggesting more complex admin configurations.
    - **`tasks/` Directory:** May contain Celery tasks for background processing (e.g., video reprocessing, data aggregation).

## Module Spotlight: Custom Authentication (`nadooit_auth`)
- **Purpose:** Implements a custom authentication system where users are identified by a `user_code`, followed by mandatory FIDO2-based multi-factor authentication.
- **Key Components:**
    - **`User` Model (`models.py`):**
        - Extends `AbstractUser` and `PermissionsMixin`.
        - `id`: UUIDField (PK).
        - `user_code`: CharField (max_length=32, unique). Serves as a primary identifier for FIDO2 flows. Default generated by `get__new_user_code`. Intended to be on a "security key". TODO: Rename to `code`.
        - `display_name`: CharField.
    - **`UserCodeBackend` (`custom_user_code_auth_backend.py`):**
        - Custom backend that *identifies* the user based on `user_code`. It does not perform full authentication itself; this is a prelude to FIDO2.
    - **Code Generation/Validation (`user_code.py`):**
        - `get__new_user_code()`: Generates a 6-character alphanumeric code. While `user_code` is an identifier, this is short and could be made more robust (longer, using full model field length) to improve uniqueness and reduce guessability/enumeration.
        - `check__valid_user_code()`: Attempts to validate user codes. **CRITICAL FLAW: Buggy and unreliable logic.**
    - **Views (`views.py`):**
        - `login_user`: Handles the login process. First, identifies the user via `user_code` using `UserCodeBackend`. Then, crucially, it calls an `mfa` app (likely `django-mfa2`) to perform FIDO2 authentication. Login proceeds only if FIDO2 is successful.
        - `register_user`: Restricted to "KeyManagers". Creates users with a `user_code`, a generated `username`, and password "none" (**RISKY**). Redirects to FIDO2 setup (`start_fido2`) after registration, enforcing MFA enrollment.
        - `logout_user`: Standard logout.
        - `log_user_in`: Helper to complete the Django login session *after* successful FIDO2 authentication.
    - **Username Generation (`username.py`):** Contains `get__new_username()`.
- **Authentication Flow Outline:**
    1. KeyManager registers a new user with a `user_code` (identifier).
    2. User account created (username auto-generated, password="none").
    3. New user is immediately logged in (this initial login might need review if FIDO2 isn't setup yet) and redirected to FIDO2 setup.
    4. Subsequent login: User provides `user_code` (identifier) -> System identifies user -> User is challenged for FIDO2 credential -> If FIDO2 auth successful, user is logged in.
- **Key Considerations & TODOs:**
    - **User Code as Identifier:**
        - **Length/Strength:** While not a password, the 6-character `user_code` is short for a unique identifier. **Recommendation:** Increase length (e.g., to 16-32 chars using `secrets.token_urlsafe()`) and utilize the full `max_length=32` of the model field to enhance uniqueness and reduce guessability.
        - **Generation:** `get__new_user_code` should generate codes of the new recommended length.
    - **CRITICAL - Flawed Code Validation:** `check__valid_user_code` logic is buggy. **Action:** Rewrite to correctly validate length and alphanumeric content according to the chosen code format.
    - **CRITICAL - Default Password "none":** Creating users with `password="none"` is risky if `ModelBackend` is active and `username` is known. **Action:** Use `user.set_unusable_password()` for these accounts to prevent username/password bypasses of the FIDO2 flow.
    - **FIDO2 Enforcement:** The security of the system hinges on the robust and non-bypassable enforcement of FIDO2 authentication after user identification via `user_code`. Ensure no paths exist to complete login without FIDO2.
    - **`user_code` in Model:** Address `TODO #114` to rename `user_code` field to `code` for conciseness.
    - **Misleading Login Error Message:** The error message in `login_user` ("Username or Password is incorrect") should be updated to "Invalid user code or FIDO2 authentication failed." or similar, depending on the stage of failure.
    - **Redundant `user_code` Slashes:** `register_user` view replaces `/` from `user_code` input; investigate why this is necessary if codes are intended to be alphanumeric.

## Development Environment Setup

### Prerequisites
- GitHub Desktop
- Docker (with PATH configuration for Mac users)
- Docker Compose
- Python (latest version)
- pip (upgraded)

### Mac-Specific Setup Steps
1. Configure Docker PATH:
   ```bash
   echo 'export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Project Initialization
- Use Docker Compose for development environment
- Specific Docker Compose file for Mac with SQLite: `docker-compose-dev-MAC_SQLite.yml`

### Initialization Commands
```bash
# Build and prepare the environment
docker compose -f docker-compose-dev-MAC_SQLite.yml build

# Database migrations
docker compose -f docker-compose-dev-MAC_SQLite.yml run --rm app python manage.py makemigrations
docker compose -f docker-compose-dev-MAC_SQLite.yml run --rm app python manage.py migrate

# Static files and templates
docker compose -f docker-compose-dev-MAC_SQLite.yml run --rm app python manage.py collectstatic --no-input
docker compose -f docker-compose-dev-MAC_SQLite.yml run --rm app python manage.py import_templates

# Create superuser
docker compose -f docker-compose-dev-MAC_SQLite.yml run --rm app python manage.py createsuperuser

# Start the development server
docker compose -f docker-compose-dev-MAC_SQLite.yml up
```

## Deployment
- Use `docker-compose-deploy.yml` for production deployment
- Command: `docker compose -f docker-compose-deploy.yml up -d`

## Testing
- Activate virtual environment before running tests
- Specific test command not fully specified in README

## Contributing Workflow
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create pull request

## Potential Improvements
- Complete testing instructions
- Add more detailed API documentation
- Clarify deployment process
- Provide more context about the system's purpose and architecture

## Notes for Future Development
- Ensure cross-platform compatibility
- Maintain clear and up-to-date documentation
- Regularly update dependencies

## Security Considerations

### Authentication and Authorization
- Multiple authentication modules detected (`nadooit_auth`, `nadooit_api_key`)
- Potential security risks:
  - Ensure robust API key management
  - Implement strong password policies
  - Use multi-factor authentication
  - Regularly rotate API keys and credentials

### Infrastructure Security
- Docker-based deployment
- Multiple environment configurations (dev, deploy)
- Security recommendations:
  - Use least-privilege principle in container configurations
  - Implement network isolation
  - Regularly update base images
  - Use secrets management for sensitive configurations

### Code Security
- Django-based project
- Potential security focus areas:
  - CSRF protection
  - XSS prevention
  - SQL injection protection
  - Input validation
  - Rate limiting for API endpoints

### Vulnerability Management
- Implement regular security scans
- Use tools like:
  - Bandit for Python security checks
  - Safety for dependency vulnerability scanning
  - OWASP Dependency-Check
- Set up automated security testing in CI/CD pipeline

### Data Protection
- Multiple modules handling sensitive data (CRM, HR, Workflow)
- Security best practices:
  - Encrypt sensitive data at rest and in transit
  - Implement data access logging
  - Use secure database connections
  - Anonymize or pseudonymize personal data where possible

### Monitoring and Incident Response
- Implement comprehensive logging
- Set up security event monitoring
- Create an incident response plan
- Regularly conduct security audits and penetration testing

### Compliance Considerations
- Identify applicable data protection regulations (GDPR, CCPA, etc.)
- Ensure data handling meets legal requirements
- Provide mechanisms for data subject rights (access, deletion)

### Recommended Security Tools
- Django-axes for login attempt tracking
- Django-defender for IP blocking
- Django-rest-framework-simplejwt for secure token-based authentication
- python-jose for JWT handling

### Potential Vulnerabilities to Monitor
- Ensure no hardcoded credentials in source code
- Validate and sanitize all user inputs
- Implement proper error handling without exposing system details
- Use environment variables for sensitive configurations

### Continuous Improvement
- Stay informed about security updates in:
  - Django framework
  - Python ecosystem
  - Docker and container technologies
  - Third-party dependencies
