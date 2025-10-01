import re

is_email = lambda x: bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", x))
