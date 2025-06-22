import os

SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "subscribers.txt")


def get_all_subscribed_users():
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip().isdigit()]
    except FileNotFoundError:
        return []


def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    except FileNotFoundError:
        return set()


def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        for user_id in subscribers:
            f.write(f"{user_id}\n")
