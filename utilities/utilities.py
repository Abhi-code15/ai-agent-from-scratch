import os

# ANSI escape codes for coloring terminal output
# \033 (or \x1b) signals the terminal that a formatting command follows
# [90m sets the text color to dark gray (ideal for background debug logs)
# [0m resets text styling back to normal so standard conversation stays untouched
START_COLOR = "\033[90m"
END_COLOR = "\033[0m"


def log(text: str):
    """Prints indented debug messages in gray when DEBUG is enabled in environment."""
    if os.getenv("DEBUG", "").strip().lower() == "true":
        print(f"  {START_COLOR}{text}{END_COLOR}")
