import csv
import hashlib
import random
import string
import os

OUTPUT_FILE = "static/csv/identifiers.csv"

def generate_identifier(netid):
    """
    Generate a pseudo-anonymous identifier based on the NetID.
    """
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    unique_identifier = hashlib.sha256(f"{netid}{salt}".encode()).hexdigest()[:10]
    return unique_identifier

def generate_class_identifiers(roster_file):
    """
    Generate identifiers for all students in the class.
    """
    identifiers = []

    with open(roster_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            netid = row[0].strip()  # Assume NetID is the first column
            identifier = generate_identifier(netid)
            identifiers.append((netid, identifier))

    # Save the identifiers to a central file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["NetID", "Identifier"])
        writer.writerows(identifiers)

    print(f"Identifiers saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    roster_file = input("Enter the path to the class roster (CSV): ").strip()
    generate_class_identifiers(roster_file)