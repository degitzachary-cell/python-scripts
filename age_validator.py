"""
Age Validator CLI Tool
----------------------
Asks the user for their age, validates the input,
and returns a custom message based on the result.

A clean, beginner-friendly example of:
- Input validation with try/except
- Functions and control flow
- Command-line user interaction

Author: Your Name
"""


def get_age_from_user() -> int:
    """Prompt the user for their age, retrying on invalid input."""
    while True:
        raw = input("Please enter your age: ").strip()
        try:
            age = int(raw)
            if age < 0 or age > 130:
                print("  Please enter a realistic age between 0 and 130.")
                continue
            return age
        except ValueError:
            print(f"  '{raw}' is not a valid number. Please try again.")


def classify_age(age: int) -> str:
    """Return a category label based on the given age."""
    if age < 13:
        return "Child"
    elif age < 18:
        return "Teenager"
    elif age < 65:
        return "Adult"
    else:
        return "Senior"


def main():
    print("=" * 40)
    print("       Age Validator Tool")
    print("=" * 40)
    print()
    age = get_age_from_user()
    category = classify_age(age)
    print()
    print(f"  Age entered   : {age}")
    print(f"  Category      : {category}")
    if age >= 18:
        print("  Voting status : Eligible to vote")
    else:
        years_left = 18 - age
        print(f"  Voting status : Not yet eligible ({years_left} year(s) to go)")
    print()
    print("=" * 40)


if __name__ == "__main__":
    main()
