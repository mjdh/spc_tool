"""
Michael's UKIPO query tool
Author: Michael Henley
Email: michael@henley.co
Copyright: 2018
All rights under the Copyright, Designs and Patents Act 1988 are asserted including the author's moral rights.

This tool is designed to allow basic access to UK IPO register information relating to EP(UK) patents and their associated SPCs.
The SPC term calculation logic implements article 13(1) - 13(3) of Regulation (EC) No 469/2009.

This program provides information only and does not provide legal advice.
"""


from functions.functions import get_patent_info, get_spc_info_from_patent, has_patent_expired, spc_term_calc
from dateutil import relativedelta
from classes.classes import bcolours

actions = ["EP search", "SPC search by EP number", "SPC term calculator"]
running = True

while running:
    i = 1
    print("==========================")
    print("Michael's UKIPO query tool")
    print("==========================\n")
    for action in actions:
        print(str(i) + ".", action)
        i += 1
    print("\n")
    choice = input("Choose mode:")
    index = int(choice) - 1

    search = input("EP number:")

    print("\n")

    if index == 0:
        pat_data = get_patent_info(search)

        for header, value in pat_data.items():
            if len(header) < 27:
                while len(header) < 27:
                    header += " "
            print(header, "|     ", value)
        print("\n")
        continue

    if index == 1:
        spc_data = get_spc_info_from_patent(search)

        for header, value in spc_data.items():
            if len(header) < 25:
                while len(header) < 25:
                    header += " "
            print(header, "|     ", value)
        print("\n")
        continue

    if index == 2:
        pat_data = get_patent_info(search)
        spc_data = get_spc_info_from_patent(search)

        has_patent_expired(pat_data)
        if spc_data == False:
            print(bcolours.FAIL + "No SPC identified." +bcolours.ENDC)
            continue
        else:
            spc_expiry = spc_term_calc(pat_data, spc_data)
            print("SPC", spc_data["SPC number"], "will expire on", spc_expiry.strftime("%d %B %Y") + ".")

            pe_expiry = spc_expiry + relativedelta.relativedelta(months=6)
            print("If there is a paediatric extension, it will expire on", pe_expiry.strftime("%d %B %Y") + ".\n")
            continue

    else:
        print(bcolours.FAIL + "You have not made a valid selection.\n" + bcolours.ENDC)
        continue