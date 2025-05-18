def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return ''.join(f"\\{char}" if char in escape_chars else char for char in str(text))
