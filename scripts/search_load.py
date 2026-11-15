# 25 librarians search the catalog at the same time. Ctrl+C stops it.
# Run: python3 search_load.py

import os
import random
import threading
import time

import requests

SITE = "https://mylibrary.bom.frappe.cloud"
AUTHORS = ["Lars Walker", "Beatrice Cohen", "Zara Zhang", "Kenji Tanaka", "Grace Achebe"]

session = requests.Session()
session.post(f"{SITE}/api/method/login", data={"usr": "librarian1@mylibrary.test", "pwd": "Library@2026"})


def librarian():
	for _ in range(2):
		author = random.choice(AUTHORS)
		start = time.time()
		response = session.get(f"{SITE}/api/method/mylibrary.api.search_books", params={"query": author}, timeout=180)
		print(response.status_code, f"{time.time() - start:.0f}s", author)


threads = [threading.Thread(target=librarian, daemon=True) for _ in range(25)]
for thread in threads:
	thread.start()

try:
	for thread in threads:
		thread.join()
except KeyboardInterrupt:
	print("stopped")
	os._exit(0)
