#!/bin/bash

#######################################
# PostgreSQL Database Documentation Generator
# Uses SchemaSpy to create HTML documentation with ER diagrams
#######################################

set -e  # Exit on error

#######################################
# CONFIGURATION
# Update these values for your database
#######################################

DB_HOST="dbaas-db-7530007-do-user-2009138-0.k.db.ondigitalocean.com"
DB_PORT="25060"
DB_NAME="defaultdb"
DB_USER="cfa_dev"
DB_PASSWORD="mPn4WX7FszhY"
DB_SCHEMA="public"          # Your database schema
        # Schema to document (usually 'public')

# SSL Configuration
# Set to "true" if your database requires SSL
SSL_ENABLED="False"

# SSL Mode options: disable, allow, prefer, require, verify-ca, verify-full
# - disable: No SSL
# - require: SSL required but don't verify certificate (common for cloud databases)
# - verify-ca: SSL required and verify certificate authority
# - verify-full: SSL required and verify certificate and hostname
SSL_MODE="require"

# Optional: Path to SSL certificates (uncomment if needed)
# SSL_ROOT_CERT="/path/to/root.crt"
# SSL_CERT="/path/to/client.crt"
# SSL_KEY="/path/to/client.key"

#######################################
# PATHS
# Adjust if you installed tools elsewhere
#######################################

OUTPUT_DIR="./docs"
SCHEMASPY_JAR="$HOME/schemaspy-tools/schemaspy.jar"
POSTGRES_JAR="$HOME/schemaspy-tools/postgresql.jar"

#######################################
# SCRIPT START
#######################################

echo "================================================"
echo "  PostgreSQL Database Documentation Generator"
echo "================================================"
echo ""

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Error: Java is not installed or not in PATH"
    echo "   Please install Java 11 or higher"
    echo "   macOS: brew install openjdk@11"
    echo "   Ubuntu: sudo apt install openjdk-11-jdk"
    exit 1
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | awk -F '.' '{print $1}')
if [ "$JAVA_VERSION" -lt 11 ]; then
    echo "❌ Error: Java 11 or higher is required"
    echo "   Current version: $(java -version 2>&1 | head -n 1)"
    exit 1
fi

# Check if SchemaSpy JAR exists
if [ ! -f "$SCHEMASPY_JAR" ]; then
    echo "❌ Error: SchemaSpy JAR not found at $SCHEMASPY_JAR"
    echo "   Please run the setup commands from README.md"
    exit 1
fi

# Check if PostgreSQL driver exists
if [ ! -f "$POSTGRES_JAR" ]; then
    echo "❌ Error: PostgreSQL driver not found at $POSTGRES_JAR"
    echo "   Please run the setup commands from README.md"
    exit 1
fi

# Clean and create output directory
echo "🧹 Cleaning output directory..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "📊 Connecting to database: $DB_NAME@$DB_HOST:$DB_PORT"
echo "🔍 Analyzing schema: $DB_SCHEMA"
echo "🔒 SSL: $SSL_ENABLED"
echo ""

# Build connection properties for SSL
CONN_PROPS_FILE=""
if [ "$SSL_ENABLED" = "true" ]; then
    # Create temporary properties file for SSL settings
    CONN_PROPS_FILE=$(mktemp)
    echo "ssl=true" > "$CONN_PROPS_FILE"
    echo "sslmode=$SSL_MODE" >> "$CONN_PROPS_FILE"

    # Add certificate paths if provided
    if [ ! -z "$SSL_ROOT_CERT" ]; then
        echo "sslrootcert=$SSL_ROOT_CERT" >> "$CONN_PROPS_FILE"
    fi
    if [ ! -z "$SSL_CERT" ]; then
        echo "sslcert=$SSL_CERT" >> "$CONN_PROPS_FILE"
    fi
    if [ ! -z "$SSL_KEY" ]; then
        echo "sslkey=$SSL_KEY" >> "$CONN_PROPS_FILE"
    fi
fi

# Generate documentation
echo "⚙️  Generating documentation..."

# Build the java command
JAVA_CMD="java -jar $SCHEMASPY_JAR \
    -t pgsql \
    -dp $POSTGRES_JAR \
    -host $DB_HOST \
    -port $DB_PORT \
    -db $DB_NAME \
    -u $DB_USER \
    -p $DB_PASSWORD \
    -s $DB_SCHEMA \
    -o $OUTPUT_DIR \
    -desc \"Database Documentation - Generated on $(date '+%Y-%m-%d %H:%M:%S')\" \
    -norows"

# Add connection properties if SSL is enabled
if [ ! -z "$CONN_PROPS_FILE" ]; then
    JAVA_CMD="$JAVA_CMD -connprops \"$CONN_PROPS_FILE\""
fi

# Execute the command
eval "$JAVA_CMD"

# Clean up temporary properties file
if [ ! -z "$CONN_PROPS_FILE" ] && [ -f "$CONN_PROPS_FILE" ]; then
    rm -f "$CONN_PROPS_FILE"
fi

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✅ Documentation generated successfully!"
    echo "================================================"
    echo ""
    echo "📁 Output directory: $OUTPUT_DIR/"
    echo "📖 Main page: $OUTPUT_DIR/index.html"
    echo "📊 Diagrams: $OUTPUT_DIR/diagrams/"
    echo ""
    echo "To view documentation:"
    echo "  macOS:   open $OUTPUT_DIR/index.html"
    echo "  Linux:   xdg-open $OUTPUT_DIR/index.html"
    echo "  Windows: start $OUTPUT_DIR/index.html"
    echo ""
else
    echo ""
    echo "================================================"
    echo "❌ Error generating documentation"
    echo "================================================"
    echo ""
    echo "Common issues:"
    echo "  - Cannot connect to database (check host, port, credentials)"
    echo "  - Schema does not exist (check DB_SCHEMA setting)"
    echo "  - Insufficient permissions (user needs read access)"
    echo ""
    exit 1
fi
