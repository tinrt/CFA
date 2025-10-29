# CFA Database Documentation

This repository contains comprehensive HTML documentation for the CFA database schema, including ER diagrams, table relationships, and detailed explanations of all data structures.

---

## Using the Documentation

### What is this data?

This documentation describes a **de-normalized, read-only view** of the CFA database. Here's what that means:

- **De-normalized**: Data has been flattened and optimized for reading and analysis, rather than transactional use
- **Read-only**: This is a snapshot - we cannot modify the live CFA database

### Important Notes About the Data

**Privacy & Anonymization:**
- Personal information (names, addresses, phone numbers) has been **anonymized**
- Fake names and addresses have been superimposed to protect privacy

**Foreign Key Relationships:**
- Because this is a de-normalized read-only view, the database does **not have encoded foreign key constraints**
- However, the **comments explain how tables relate to each other**
- When you read the documentation, pay attention to the comments on columns and tables
- Comments will tell you things like "This column references the customer_id in the customers table"

### Getting the Documentation

**Step 1: Clone or Download the Repository**

```bash
# Option 1: Clone with git
git clone https://github.com/your-org/dmc-schema-documentation.git
cd dmc-schema-documentation

# Option 2: Download ZIP
# Go to https://github.com/your-org/dmc-schema-documentation
# Click "Code" → "Download ZIP"
# Extract the ZIP file
```

**Step 2: Open the Documentation**

The documentation is pre-generated HTML files. Simply open them in your web browser:

```bash
# macOS
open docs/index.html

# Linux
xdg-open docs/index.html

# Windows
start docs\index.html
```

Or navigate to the `docs` folder and double-click `index.html`.

### Exploring the Documentation

**Start Here:**
1. Open `docs/index.html` - this is the main page with database overview
2. View the **main ER diagram** to see all tables and their relationships at a glance
3. Click on any **table name** to see detailed information about that table

**On Each Table Page You'll Find:**
- **Columns**: Names, data types, and whether they can be null
- **Comments**: Explanations of what each column contains and how it's used
- **Relationships**: Visual diagrams showing how this table connects to others
- **Indexes**: Performance optimizations (advanced topic)
- **Sample Data Preview**: Examples of what the data looks like

**Following Relationships:**
- Look for comments that mention other tables (e.g., "references customer_id in customers table")
- Click on table names to navigate between related tables
- Use the ER diagrams to visualize the connections
- Remember: relationships exist in the comments and column naming, not as enforced constraints

### Learning Tips

**Understanding the Schema:**
- **Read the comments first** - they explain the "why" behind the design
- **Trace a customer journey** - start with the customers table, find their orders, then order items
- **Identify patterns** - notice how ID columns relate across tables
- **Think about queries** - how would you join tables to answer business questions?

**Key Concepts to Learn:**
- **Primary Keys**: Usually named `id` or `table_name_id` - uniquely identifies each row
- **Implied Foreign Keys**: Columns that reference IDs in other tables (check comments)
- **Denormalization**: Why some data might be repeated (performance optimization)
- **Indexes**: Columns that are optimized for fast searching

**Common Tables to Explore:**
- `customers` - who places orders
- `orders` - individual customer orders
- `order_items` - what was in each order
- `products` - menu items available
- `stores` - restaurant locations

The ER diagrams and comments will guide you in understanding which tables to join and how.

---

## 🔧 Generating Documentation

**Note: Most team members do NOT need to follow these instructions.** The documentation is already generated and committed to the repository. These instructions are for maintainers who need to regenerate documentation after database schema changes.

### What This Section Covers

This section explains how to:
- Install the required tools (Java, SchemaSpy, Graphviz)
- Configure database connection settings
- Run the generation script
- Update the documentation in the repository

### Prerequisites

To generate documentation, you need:
- **Java 11 or higher** - to run SchemaSpy
- **Graphviz** - to generate ER diagrams
- **Database access credentials** - to connect to the source database
- **Command line access** - to run the generation script

### Initial Setup

#### Step 1: Install Java

**macOS:**
```bash
brew install openjdk@11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install openjdk-11-jdk
```

**Windows:**
Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [Adoptium](https://adoptium.net/)

**Verify installation:**
```bash
java -version
```

You should see version 11 or higher.

#### Step 2: Download SchemaSpy and PostgreSQL Driver

```bash
# Create a directory for the tools (one-time setup)
mkdir -p ~/schemaspy-tools
cd ~/schemaspy-tools

# Download SchemaSpy JAR (one-time download)
curl -L https://github.com/schemaspy/schemaspy/releases/download/v6.2.4/schemaspy-6.2.4.jar -o schemaspy.jar

# Download PostgreSQL JDBC driver (one-time download)
curl -L https://jdbc.postgresql.org/download/postgresql-42.7.1.jar -o postgresql.jar

# Return to your project
cd -
```

These files stay in `~/schemaspy-tools` and are reused for all documentation generation.

#### Step 3: Install Graphviz

Graphviz is required for generating ER diagrams and visualizations.

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install graphviz
```

**Windows:**
Download and install from [graphviz.org](https://graphviz.org/download/)

**Verify installation:**
```bash
dot -V
```

You should see the Graphviz version number.

#### Step 4: Configure Database Connection

Edit the `generate-docs.sh` script in this repository and update the database connection settings:

```bash
DB_HOST="localhost"          # Your database host
DB_PORT="5432"               # Your database port
DB_NAME="myapp_db"           # Your database name
DB_USER="postgres"           # Your database username
DB_PASSWORD="your_password"  # Your database password
DB_SCHEMA="public"           # Schema to document (usually 'public')
```

**Security Note:** Never commit database credentials to GitHub! Consider using environment variables or a `.env` file (see Security Considerations section below).

#### Step 5: Make Script Executable

```bash
chmod +x generate-docs.sh
```

### Generating Documentation

Once setup is complete, generating documentation is simple:

```bash
./generate-docs.sh
```

This will:
1. Connect to your PostgreSQL database
2. Read the schema and all comments
3. Generate ER diagrams using Graphviz
4. Create HTML documentation in the `./docs/` directory

**View the documentation:**
```bash
# macOS
open docs/index.html

# Linux
xdg-open docs/index.html

# Windows
start docs/index.html
```

### Maintenance Workflow

#### 1. Database Schema is Updated
When the database schema changes (new tables, columns, or comments are added), the documentation needs to be regenerated.

#### 2. Regenerate Documentation
```bash
./generate-docs.sh
```

#### 3. Review Changes
```bash
# View what files changed
git status

# Review specific changes
git diff docs/
```

#### 4. Commit and Push to GitHub
```bash
git add docs/
git commit -m "Update database documentation - added customer_preferences table"
git push
```

Students will see the updated documentation the next time they pull from the repository.

### Repository Structure

```
dmc-schema-documentation/
├── README.md              # This file
├── generate-docs.sh       # Documentation generation script
├── docs/                  # Generated HTML documentation (commit this!)
│   ├── index.html        # Main documentation page
│   ├── diagrams/         # ER diagrams
│   ├── tables/           # Individual table pages
│   └── ...
└── .gitignore            # Exclude sensitive files
```

## 📝 Adding Documentation Comments

**Note: Most team members do NOT need to read this section.** This is for database administrators and developers who are adding or updating the documentation comments that appear in the generated documentation.

### What Are PostgreSQL Comments?

PostgreSQL allows you to attach descriptive comments to database objects using the `COMMENT` statement. These comments:
- Are stored in the database itself (not in external files)
- Appear in the generated HTML documentation
- Help others understand the purpose and usage of database structures
- Are part of the schema definition and survive database backups


### Comment Syntax

PostgreSQL uses this basic syntax:
```sql
COMMENT ON [object_type] [object_name] IS 'Your comment text here';
```

### Commenting Tables

Tables should explain what data they store and their purpose in the system.

**Basic Example:**
```sql
COMMENT ON TABLE customers IS
'Stores customer information including contact details and account status.';
```

**Detailed Example with Context:**
```sql
COMMENT ON TABLE customers IS
'Customer master table containing profile and contact information.

This table stores all registered customers, whether they have placed orders or not.
New customers are created when they first sign up or place an order.

Privacy Note: In the production database, this contains real customer data.
In the student database, all personal information has been anonymized.

Related Tables:
- orders: Links to this table via customer_id
- customer_addresses: Stores multiple addresses per customer
- customer_preferences: Stores dietary preferences and favorites';
```

### Commenting Columns

Columns should explain what data they contain, any constraints, and how they're used.

**Basic Examples:**
```sql
COMMENT ON COLUMN customers.email IS
'Customer email address. Used for login and order notifications. Must be unique.';

COMMENT ON COLUMN customers.phone IS
'Primary phone number in format (555) 555-5555. Optional. Used for SMS notifications if customer opts in.';

COMMENT ON COLUMN customers.created_at IS
'Timestamp when customer account was created. Set automatically, never updated.';
```

**Explaining Relationships (Implied Foreign Keys):**
```sql
COMMENT ON COLUMN orders.customer_id IS
'References customers.id - the customer who placed this order.

Since this is a denormalized read-only database, there is no formal foreign key constraint,
but in the source system this is a required foreign key relationship.
Every order must belong to a valid customer.';
```

**Documenting Enums and Status Fields:**
```sql
COMMENT ON COLUMN orders.status IS
'Current status of the order. Possible values:
- pending: Order received, not yet confirmed
- confirmed: Order accepted by store, being prepared
- ready: Order complete and ready for pickup
- completed: Customer has picked up the order
- cancelled: Order was cancelled (by customer or store)

Orders typically progress: pending → confirmed → ready → completed
Status changes are logged in order_status_history table.';
```

**Documenting Calculated/Derived Fields:**
```sql
COMMENT ON COLUMN orders.total_amount IS
'Total order amount in USD including tax and fees.

Calculated as: sum(order_items.subtotal) + tax + delivery_fee
Stored redundantly for performance and historical accuracy.
This value is frozen at time of order completion and does not change
if product prices are later updated.';
```

### Commenting Views

Views should explain what data they show and why they exist.

```sql
COMMENT ON VIEW active_customers IS
'Lists customers who have placed at least one order in the last 90 days.

Used for marketing campaigns and active user analysis.
Excludes customers with status = ''cancelled''.

Columns are same as customers table but filtered for recency.
Materialized nightly at 2 AM EST.';
```

### Commenting Indexes

Indexes should explain what queries they optimize.

```sql
COMMENT ON INDEX idx_customers_email IS
'Enables fast customer lookup by email during login.
Used by: customer authentication, password reset, order confirmation emails.';

COMMENT ON INDEX idx_orders_customer_created IS
'Composite index for customer order history queries.
Optimizes: SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC
Critical for customer portal "My Orders" page.';
```

### Commenting Constraints

Explain the business rule behind the constraint.

```sql
COMMENT ON CONSTRAINT fk_orders_customer ON orders IS
'Ensures every order belongs to a valid customer.
Prevents deletion of customers who have orders (ON DELETE RESTRICT).

Business Rule: Customer records must be maintained for historical order tracking,
even if the customer closes their account. Use customers.status = ''closed'' instead
of deleting the customer record.';

COMMENT ON CONSTRAINT chk_order_total_positive ON orders IS
'Ensures order total is always greater than 0.
Business Rule: Zero-dollar orders are not allowed. Promotional orders must show
original price with separate discount/promo line items.';
```

### Commenting Sequences

```sql
COMMENT ON SEQUENCE customers_id_seq IS
'Generates unique customer IDs starting from 1000.
Starts at 1000 to distinguish from test data (IDs 1-999).';
```


#### Multi-line Comments

For complex explanations, use PostgreSQL's multi-line string syntax:

```sql
COMMENT ON TABLE customers IS
'Customer master table containing all registered customer information.

=== Purpose ===
This table is the central hub for customer data, linking to orders, addresses,
preferences, and payment methods.

=== Data Privacy ===
In production: Contains real customer PII (Personally Identifiable Information)
In student database: All PII has been anonymized with fake data

=== Common Queries ===
1. Find customer by email (for login):
   SELECT * FROM customers WHERE email = ''user@example.com'';

2. Get customer order history:
   SELECT c.*, o.* FROM customers c
   JOIN orders o ON c.id = o.customer_id
   WHERE c.id = 123 ORDER BY o.created_at DESC;

3. Find active customers (ordered in last 90 days):
   SELECT DISTINCT c.* FROM customers c
   JOIN orders o ON c.id = o.customer_id
   WHERE o.created_at > NOW() - INTERVAL ''90 days'';

=== Related Tables ===
- orders: Customer purchase history
- customer_addresses: Shipping/billing addresses
- customer_preferences: Dietary restrictions and favorites
- loyalty_points: Rewards program balance';
```

### Updating Comments

Comments can be updated by running the COMMENT statement again:

```sql
-- Add initial comment
COMMENT ON TABLE customers IS 'Customer information';

-- Update the comment (replaces the old one)
COMMENT ON TABLE customers IS
'Customer master table with contact information and account status.
Updated on 2024-01-15 to clarify anonymization policy.';
```

### Removing Comments

To remove a comment:
```sql
COMMENT ON TABLE customers IS NULL;
```

### Viewing Existing Comments

To see what comments exist:

```sql
-- View all table comments
SELECT
    schemaname,
    tablename,
    obj_description((schemaname||'.'||tablename)::regclass)
FROM pg_tables
WHERE schemaname = 'public';

-- View comments for columns in a specific table
SELECT
    cols.column_name,
    pg_catalog.col_description((schemaname||'.'||tablename)::regclass::oid, cols.ordinal_position)
FROM information_schema.columns cols
JOIN pg_tables t ON cols.table_name = t.tablename
WHERE cols.table_name = 'customers'
  AND t.schemaname = 'public';
```

### After Adding Comments

Once you've added or updated comments in the database:

1. **Regenerate Documentation**
   ```bash
   ./generate-docs.sh
   ```

2. **Review the Generated HTML**
   - Open `docs/index.html`
   - Navigate to the tables you commented
   - Verify your comments appear and are formatted correctly

3. **Commit and Push**
   ```bash
   git add docs/
   git commit -m "Add documentation comments for customers and orders tables"
   git push
   ```

