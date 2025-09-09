# Testing Checklist - First Name & Last Name Feature

## Pre-Testing Setup

### 1. Database Migration (if you have existing data)
```bash
cd voiceai-geography/src/backend
python migrate_add_names.py
```

### 2. Create Test Data
```bash
cd voiceai-geography/src/backend
python create_test_code.py --samples
```
This creates:
- `TEST123` - No names (should use "Student")
- `ALICE001` - "Alice Johnson" (should use "Alice")
- `BOB002` - "Bob Smith" (should use "Bob")
- `CHARLIE003` - "Charlie" only (should use "Charlie")
- `DIANA004` - "Diana Williams" (should use "Diana")

## Testing Steps

### ✅ Admin Interface Testing
1. **Start the application** and go to admin login
2. **Login** with admin credentials
3. **Check the invitation codes table** - should show:
   - New columns: "First Name" and "Last Name"
   - Sample codes with their respective names
   - "-" displayed for empty name fields
4. **Test sorting** by clicking on "First Name" and "Last Name" headers

### ✅ ElevenLabs Integration Testing
1. **Go to main app** (not admin)
2. **Test code without name** (`TEST123`):
   - Enter code and submit
   - Start conversation
   - Check browser console for: `"Using customer name: Student"`
   - Verify ElevenLabs uses "Student" in conversation

3. **Test code with first name** (`ALICE001`):
   - Enter code and submit  
   - Start conversation
   - Check browser console for: `"Using customer name: Alice"`
   - Verify ElevenLabs uses "Alice" in conversation

4. **Test code with only first name** (`CHARLIE003`):
   - Enter code and submit
   - Start conversation
   - Check browser console for: `"Using customer name: Charlie"`
   - Verify ElevenLabs uses "Charlie" in conversation

### ✅ API Testing (Optional - for developers)
Test the API endpoints directly:

```bash
# Test validate-code endpoint
curl -X POST http://localhost:8000/api/validate-code \
  -H "Content-Type: application/json" \
  -d '{"code": "ALICE001"}'

# Expected response:
# {
#   "valid": true,
#   "code": "ALICE001", 
#   "first_name": "Alice",
#   "last_name": "Johnson"
# }
```

## Expected Behavior

### ✅ Customer Name Logic
- **Has first_name**: Uses first_name (trimmed)
- **No first_name or empty**: Uses "Student"
- **Whitespace only**: Uses "Student"

### ✅ Admin Interface
- **Name columns**: Visible and sortable
- **Empty names**: Show as "-"
- **Existing codes**: Continue to work (show "-" for names)

### ✅ Backward Compatibility
- **Existing invitation codes**: Still work exactly as before
- **No database errors**: Migration handles existing data safely
- **API compatibility**: All existing API calls continue to work

## Troubleshooting

### Database Issues
If you get database errors:
```bash
# Check if migration is needed
cd voiceai-geography/src/backend
python migrate_add_names.py
```

### Console Errors
Check browser developer console for:
- `"Using customer name: [name]"` - Should appear when starting conversations
- Any JavaScript errors related to `currentInvitationData`

### API Issues
Verify the `/api/validate-code` endpoint returns name fields:
- Should include `first_name` and `last_name` in response
- Values can be `null` for codes without names

## Success Criteria

- ✅ Admin interface shows name columns
- ✅ Codes with names use first_name as customer_name in ElevenLabs
- ✅ Codes without names use "Student" as customer_name
- ✅ No existing functionality is broken
- ✅ Migration script runs without errors
- ✅ Sample codes are created successfully
