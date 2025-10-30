Develop the architecture for a complete CRM for restaurants with the following specifications:

**Functional Requirements:**

1. **Client Form Register:**
   - Implement a corporate customer registration form.
   - Consider that the customer is a restaurant company, with CNPJ or other company ID.

2. **Login and Authentication:**
   - Implement a user login/authentication system with role based control.
   - Consider username as User ID as CPF (for administrator, manager, shopper, and employee), CNPJ or another company ID for customer.
   - Profiles with different access levels (administrator, manager, employee, shopper, customer).
   
3. **Restaurant Shopping List:**
   - Implement a Restaurant Shopping List registration organized by Categories ( (proteins, fruits and vegetables, dairy products, cleaning products, groceries, packaging).
   - Provide categories registration form.
   - Provide a supermarket registration form.
   - Provide an interface to the shopper, where they can access the shopping lists by customer.
   - Restaurant Shopping Lists must be split in categories sections on the shopper interface.
   - For each list, shoppers can record prices quoted at registered supermarkets, and check off items as they are purchased.

4. **Subscription Management:**
   - Integrate with Stripe for customer subscription management.
   - Features to manage subscription plans, payments, and notifications.
   
5. **Inventory Control**:
   - Implement complete inventory control.
   - Integrate with the shopping list by category (proteins, produce, dairy, cleaning products, packaging, etc.).

6. **Point of Sale (POS)**:
   - Develop complete POS functionalities.
   - Management of orders in the dining room, delivery, and kitchen.
   - Issuance of tax receipts.
   
7. **Dashboard:**
   - Create a dashboard with the restaurant's key performance indicators (KPIs).
   - KPIs include daily, weekly, monthly sales, inventory, etc.

8. **Reports**:
   - Reports section with information on billing, taxes, sales by category, etc.
   
9. **Multi-location**:
    - The system can be used in multiple restaurants within the same chain, requiring support for multiple locations.

10. **Predictive analysis**:
    - The scope should include predictive analysis or artificial intelligence features, such as sales forecasts or identification of consumption trends, among others.

**Technological Requirements:**

1. **Backend:**
   - Use uv to python libraries management.
   - Develop the project in Python using FastAPI.
   - Use Postgres as a database with asynchronous calls.

2. **Frontend:**
   - Use JinjaTemplates for templating.
   - Integrate HTMX to streamline the frontend.
   - Choose a CSS framework (optional) for styling.
   - The look should be clean, sober, and elegant.

**Architecture and Development Plan:**

1. **Folder Structure:**
   - Define an organized folder structure for the project.

2. **Development Stages:**
   - Stage 1: Initial project setup (environment, dependencies, folder structure).
   - Stage 2: Implementation of Client Form Register.
   - Stage 3: Implementation of the login/authentication system and profile control.
   - Stage 4: Implementation of Restaurant Shopping List.
   - Stage 5: Integration with Stripe for subscription management.
   - Stage 6: Implementation of inventory control and integration with shopping list.
   - Stage 7: Development of POS and tax receipt issuance features.
   - Stage 6: Development of dashboard with KPIs.
   - Stage 7: Creation of the reports section.
   - Stage 8: Testing and final adjustments.

3. **Additional Technologies:**
   - Use additional Python libraries if necessary (e.g., for integration with Stripe, security, etc.).
   - Testing tools (e.g., Pytest).

**Deliverables:**

1. Detailed project architecture document.
2. Kilo memory bank updated.

**Success Criteria:**

1. Features implemented as specified.
2. Adequate performance and responsiveness.
3. Clean, sober, and elegant interface.
4. Adequate documentation of code and architecture.
5. Preference for an iterative development approach (partial deliveries).