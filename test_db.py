from src.database import get_user_stats, update_user_activity

# Test data
user_id = 12345
username = "test_user"
first_name = "Test"
last_name = "User"

# Update activity
update_user_activity(user_id, username, first_name, last_name)

# Get stats
stats = get_user_stats(user_id)
print(f"User stats: {stats}")