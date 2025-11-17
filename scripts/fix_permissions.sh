#!/bin/bash
# Script to fix file permissions for security

echo "Fixing file permissions..."

# Fix database file permissions (owner read/write only)
chmod 600 app/db/*.db 2>/dev/null
echo "✓ Database files set to 600"

# Fix secret key file permissions (if exists)
chmod 600 app/.secret_key 2>/dev/null
echo "✓ Secret key file set to 600 (if exists)"

# Ensure log directory is writable
chmod 700 app/log/ 2>/dev/null
echo "✓ Log directory set to 700"

# Ensure db directory is secure
chmod 700 app/db/ 2>/dev/null
echo "✓ DB directory set to 700"

echo "✓ All permissions fixed!"
