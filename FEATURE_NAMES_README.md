# First Name and Last Name Feature

This document describes the implementation of first name and last name fields for invitation codes in the VoiceAI Geography application.

## Overview

The feature adds optional first name and last name fields to invitation codes, allowing the ElevenLabs voice assistant to address users by their first name instead of the generic "Student".

## Database Changes

### Schema Updates
- Added `first_name VARCHAR(100)` column to `invitation_codes` table (nullable)
- Added `last_name VARCHAR(100)` column to `invitation_codes` table (nullable)

### Migration
For existing databases, run the migration script:
```bash
cd src/backend
python migrate_add_names.py
```

## API Changes

### Updated Endpoints

#### `/api/validate-code` (POST)
**Response now includes:**
```json
{
  "valid": true,
  "code": "TEST123",
  "first_name": "Alice",
  "last_name": "Johnson"
}
```

#### `/api/codes` (GET) - Admin only
**Response now includes name fields:**
```json
[
  {
    "code": "TEST123",
    "first_name": "Alice",
    "last_name": "Johnson",
    "created_at": "2024-01-01T12:00:00Z",
    "expires_at": "2024-01-08T12:00:00Z",
    "max_calls": 10,
    "call_count": 0,
    "is_valid": true
  }
]
```

## Frontend Changes

### ElevenLabs Integration
- The `customer_name` dynamic variable now uses the `first_name` from the invitation code
- Falls back to "Student" if `first_name` is null or empty
- Logic: `customerName = (first_name && first_name.trim()) ? first_name.trim() : "Student"`

### Admin Interface
- Added "First Name" and "Last Name" columns to the invitation codes table
- Displays "-" for null/empty name fields
- Names are sortable like other columns

## Code Creation

### Updated Test Script
The `create_test_code.py` script now supports names:

```bash
# Create a basic test code (no names)
python create_test_code.py

# Create sample codes with various name combinations
python create_test_code.py --samples
```

### Programmatic Usage
```python
from create_test_code import create_test_code

# Create code with first name only
create_test_code("ALICE001", first_name="Alice")

# Create code with both names
create_test_code("BOB002", first_name="Bob", last_name="Smith")

# Create code with no names (legacy behavior)
create_test_code("LEGACY001")
```

## Backward Compatibility

- All existing invitation codes continue to work without modification
- Codes without names will use "Student" as the customer name
- The migration script safely adds columns without affecting existing data
- All API responses remain compatible with existing clients

## Testing

### Sample Data
Run the following to create test codes with various name combinations:
```bash
cd src/backend
python create_test_code.py --samples
```

This creates:
- `TEST123` - No names (uses "Student")
- `ALICE001` - "Alice Johnson"
- `BOB002` - "Bob Smith" 
- `CHARLIE003` - "Charlie" (no last name)
- `DIANA004` - "Diana Williams"

### Verification
1. Use the admin interface to verify names appear in the table
2. Test invitation codes in the main app to verify correct customer names
3. Check browser console for "Using customer name: [name]" logs

## Files Modified

### Backend
- `src/backend/database.py` - Updated table schema
- `src/backend/setup_db.py` - Updated table schema
- `src/backend/server.py` - Updated API models and responses
- `src/backend/create_test_code.py` - Added name support
- `src/backend/migrate_add_names.py` - **NEW** Migration script

### Frontend
- `src/frontend/app.js` - Updated ElevenLabs integration
- `src/frontend/templates/admin.html` - Added name columns
- `src/frontend/admin.js` - Updated table display

## Security Notes

- Name fields are optional and can be null
- Names are stored as plain text (no sensitive data)
- Admin interface access is still protected by authentication
- No additional validation is performed on name fields (accepts any string up to 100 characters)

## Future Enhancements

Potential future improvements:
- Add name validation/sanitization
- Add a UI for creating/editing invitation codes in the admin interface
- Add bulk import functionality for invitation codes with names
- Add name field search/filtering in admin interface
