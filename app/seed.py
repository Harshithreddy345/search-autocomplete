"""
Seed data: preloads the Trie with popular search terms and frequencies.
Simulates a real search engine's historical query data.
"""

SEED_WORDS = [
    # Tech
    ("python", 9500), ("python tutorial", 8200), ("python list comprehension", 4100),
    ("python dictionary", 3900), ("python functions", 3700), ("python classes", 3500),
    ("postgresql", 7200), ("postgresql tutorial", 5100), ("postgresql vs mysql", 3200),
    ("programming", 8800), ("programming languages", 6200), ("programming for beginners", 4500),
    ("javascript", 9100), ("javascript tutorial", 7800), ("javascript async await", 5200),
    ("java", 8700), ("java tutorial", 7100), ("java spring boot", 5500),
    ("docker", 7600), ("docker tutorial", 6100), ("docker compose", 5300),
    ("deep learning", 7400), ("deep learning tutorial", 5100), ("deep learning python", 4200),
    ("data structures", 8100), ("data structures and algorithms", 7200), ("data structures in python", 5100),
    ("database design", 6300), ("database normalization", 4800), ("database indexing", 4100),
    ("redis", 5900), ("redis tutorial", 4200), ("redis cache", 3800),
    ("react", 8900), ("react tutorial", 7400), ("react hooks", 5600),
    ("fastapi", 4200), ("fastapi tutorial", 3100), ("fastapi vs flask", 2400),
    ("machine learning", 9200), ("machine learning python", 7100), ("machine learning tutorial", 6300),
    # General
    ("apple", 9800), ("apple iphone", 8700), ("apple macbook", 6200),
    ("amazon", 9700), ("amazon prime", 8100), ("amazon web services", 7200),
    ("google", 9900), ("google maps", 8800), ("google cloud", 6500),
    ("netflix", 8600), ("netflix movies", 7200), ("netflix series", 6800),
    ("facebook", 8200), ("facebook login", 7100), ("facebook marketplace", 5900),
    ("twitter", 7800), ("twitter login", 6200),
    ("weather", 9100), ("weather today", 8400), ("weather forecast", 7600),
    ("news", 8900), ("news today", 7800), ("news headlines", 6500),
    ("youtube", 9600), ("youtube music", 8100), ("youtube premium", 5400),
]


def seed_trie(trie):
    """Load seed words into the Trie with their frequencies."""
    for word, frequency in SEED_WORDS:
        trie.insert(word, frequency)
    print(f"✓ Seeded Trie with {len(SEED_WORDS)} words")
