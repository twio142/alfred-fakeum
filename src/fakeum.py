#!/usr/bin/env python3
import datetime
import json
import os
import random
import sys
from collections import OrderedDict

from common import (
    DEFAULT_SETTINGS,
    intvar,
)

settings = os.path.join(os.getenv("alfred_workflow_data", ""), "settings.json")
if os.path.isfile(settings):
    with open(settings, "r") as f:
        LOCALES = json.load(f).get("locales")

DELIMITER = "✕"
# Number of sentences per paragraph of Lipsum text
LIPSUMS = intvar("LIPSUM_SENTENCES", 6)
SNIPPET_MODE = os.getenv("SNIPPET_MODE") is not None


FAKERS = OrderedDict(
    [
        # People
        ("Name", ["name", ""]),
        ("First Name", ["first_name", "vorname surname"]),
        ("Last Name", ["last_name", "familienname familyname"]),
        ("Email", ["email", ""]),
        ("Email (corporate)", ["company_email", ""]),
        ("Email (free)", ["free_email", ""]),
        # ('Email (safe)', ['safe_email', '']),
        # ('Email domain (free)', ['free_email_domain', '']),
        # ('Social Security No.', ['ssn', '']),
        ("Phone No.", ["phone_number", "tel"]),
        # ('MSISDN', ['msisdn', '']),
        # Addresses
        ("Address", ["address", ""]),
        ("Street", ["street_address", ""]),
        ("Street Name", ["street_name", ""]),
        ("City", ["city", ""]),
        ("ZIP-Code", ["postcode", "plz postcode"]),
        ("State", ["state", "bundesland"]),
        ("State abbr.", ["state_abbr", "bundesland"]),
        ("Country", ["country", "land"]),
        # Internet
        # ('TLD', ['tld', '']),
        # ('Domain Name', ['domain_name', '']),
        # ('Domain Word', ['domain_word', '']),
        ("IP Address (IPv4)", ["ipv4", ""]),
        ("IP Address (IPv6)", ["ipv6", ""]),
        ("URI", ["uri", ""]),
        # ('URI path', ['uri_path', '']),
        ("URL", ["url", ""]),
        ("User-Agent", ["user_agent", ""]),
        # Corporate bullshit
        # ('Corporate BS', ['bs', '']),
        # ('Corporate catchphrase', ['catch_phrase', '']),
        ("Company", ["company", "unternehmen"]),
        # ('Company suffix', ['company_suffix', '']),
        # Lorem
        ("Paragraph", ["paragraph", "abschnitt"]),
        ("Sentence", ["sentence", "satz"]),
        ("Word", ["word", "wort"]),
        # Dates and times
        ("Date", ["date", "datum"]),
        ("Datetime", ["date_time", ""]),
        # ('ISO 8601 Datetime', ['iso8601', '']),
        ("Time", ["time", "zeit"]),
        ("Timezone", ["timezone", "zeitzone"]),
        ("UNIX Timestamp", ["unix_time", ""]),
        # Banking
        # ('Credit Card Provider', ['credit_card_provider', 'kredit']),
        ("Credit Card No.", ["credit_card_number", "kredit"]),
        ("Credit Card Expiry Date", ["credit_card_expire", "kredit"]),
        # ('Credit Card Full', ['credit_card_full', '']),
        ("Credit Card Security No.", ["credit_card_security_code", "kredit"]),
        ("IBAN", ["iban", ""]),
        # ('BBAN', ['bban', '']),
        # ('Bank Country Code', ['bank_country', '']),
        # ('Currency', ['currency_name', '']),
        # ('Currency Code', ['currency_code', '']),
        # ('Cryptocurrency', ['cryptocurrency_name', '']),
        # ('Cryptocurrency Code', ['cryptocurrency_code', '']),
        # Barcodes
        # ('EAN', ['ean', '']),
        # ('EAN 8', ['ean8', '']),
        # ('EAN 13', ['ean13', '']),
        # ('ISBN 10', ['isbn10', '']),
        # ('ISBN 13', ['isbn13', '']),
        # Colours
        # ('Colour Name', ['color_name', '']),
        # ('Colour Name (Safe)', ['safe_color_name', '']),
        # ('Hex Colour', ['hex_color', '']),
        # ('Hex Colour (Safe)', ['safe_hex_color', '']),
        # ('RGB Colour', ['rgb_color', '']),
        # ('RGB CSS Colour', ['rgb_css_color', '']),
        # Miscellaneous
        ("Job", ["job", "beruf occupation"]),
        # ('Licence Plate', ['license_plate', '']),
        # ('MD5 Hash', ['md5', '']),
        # ('SHA1 Hash', ['sha1', '']),
        # ('SHA256 Hash', ['sha256', '']),
        # ('Locale', ['locale', '']),
        # ('Language Code', ['language_code', '']),
        # ('UUID4', ['uuid4', '']),
        # ('Password (not secure!!)', ['password', '']),
    ]
)


fakers = []


def all_fakers():
    """Return all fakers."""
    from faker import Factory

    global fakers
    if not fakers:
        for loc in LOCALES or DEFAULT_SETTINGS["locales"]:
            fakers.append(Factory.create(loc))
    return fakers


def get_faker(name=None):
    """Return random faker instance."""
    fakers = all_fakers()
    if name is None:
        return random.choice(fakers)
    random.shuffle(fakers)
    methname = FAKERS[name][0]
    for faker in fakers:
        if hasattr(faker, methname):
            return faker


def get_fake_datum(name):
    """Return one fake datum for name."""
    faker = get_faker(name)
    if not faker:
        return None
    methname = FAKERS[name][0]
    if name == "Paragraph":  # Pass no. of sentences to generator
        datum = getattr(faker, methname)(LIPSUMS, False)
    else:
        datum = getattr(faker, methname)()
    if isinstance(datum, int):
        datum = str(datum)
    elif isinstance(datum, datetime.datetime):
        datum = datum.strftime("%Y-%m-%d %H:%M:%S")
    elif not isinstance(datum, str):
        sys.stderr.write(f"{name} : ({datum.__class__}) {datum}")
    return datum


def supported_type(name):
    """Return ``True`` if at least one Faker supports this type."""
    methname = FAKERS[name][0]
    for faker in all_fakers():
        if hasattr(faker, methname):
            return True
    sys.stderr.write(f'data type "{name}" is not supported by active locales')
    return False


def get_fake_data(names=None, count=1):
    """Return list of fake data."""
    fake_data = []
    if not names:
        names = sorted(FAKERS.keys())
    names = [n for n in names if supported_type(n)]
    for name in names:
        data = []
        for _ in range(count):
            data.append(get_fake_datum(name))
        if name in ("Paragraph", "Address"):
            data = "\n\n".join(data)
        else:
            data = "\n".join(data)
        fake_data.append((name, data))
    return fake_data


def main(fake_data):
    items = []
    for name, data in fake_data:
        items.append(
            dict(
                {
                    "title": name,
                    "subtitle": data,
                    "arg": data,
                    "uid": name,
                    "match": name + " " + FAKERS[name][1],
                    "text": {"largetype": data, "copy": data},
                    "mods": {"cmd": {"subtitle": "Regenerate fakers", "arg": "refake"}},
                }
            )
        )
    sys.stdout.write(json.dumps({"items": items}))


if __name__ == "__main__":
    sys.path.append(os.path.abspath("./lib"))
    main(get_fake_data())
