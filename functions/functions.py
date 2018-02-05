import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil import relativedelta


#Take the patent number and scrape UKIPO register for relevant patent data
def get_patent_info(patent_num):

    r = requests.get("https://www.ipo.gov.uk/p-ipsum/Case/PublicationNumber/" + patent_num.replace(" ", ""))
    soup = BeautifulSoup(r.text, "html.parser")

    headers_raw = soup.find_all("td", {"class": "CaseDataItemHeader"})
    values_raw = soup.find_all("td", {"class": "CaseDataItemValue"})

    headers = []
    values = []

    for header in headers_raw:
        headers.append(header.get_text())

    for value in values_raw:
        value = BeautifulSoup(str(value).replace("<br/>", "; "), "html.parser")
        values.append(value.get_text())

    data = dict(zip(headers, values))
    return data


#Take the patent number and scrape UKIPO register for relevant SPC data

def get_spc_info_from_patent(patent_num):
    r = requests.get("https://www.ipo.gov.uk/p-find-spc-bypatent-results.htm", params={"number": patent_num})
    soup = BeautifulSoup(r.text, "html.parser")

    if soup.find("p", {"class": "error"}):
        print("No SPC for", patent_num.upper(), "could be found.")
        return False

    else:
        headers_raw = soup.find_all("dt")
        values_raw = soup.find_all("dd")

        headers = []
        values = []

        for header in headers_raw:
            headers.append(header.get_text())

        for value in values_raw:
            v = value.get_text()
            v = re.sub("[\n]", "", v)
            v = re.sub("\r\r", "; ", v)
            v = re.sub("[\r\t]", "", v)

            values.append(v)

        data = dict(zip(headers, values))
        return data


#Determine whether the basic patent has expired.

def has_patent_expired(pat_data):
    filing_date = datetime.strptime(pat_data["Filing Date"], "%d %B %Y").date()
    exp_date = filing_date + relativedelta.relativedelta(years=20)
    date_diff = exp_date - datetime.now().date()
    if date_diff <= timedelta(0):
        print("Patent", pat_data["Publication Number"], "has expired.")
        return True
    else:
        print("The last day of protection under patent", pat_data["Publication Number"], "is", exp_date.strftime("%d %B %Y"), "(in", date_diff.days, "days).")
        return False


# Calculate the SPC term. exp_date is the last date of protection under the basic patent.

def spc_term_calc(pat_data, spc_data):
    filing_date = datetime.strptime(pat_data["Filing Date"], "%d %B %Y").date()
    exp_date = filing_date + relativedelta.relativedelta(years=20) - relativedelta.relativedelta(days=1)

    try:
        splitdate = spc_data["Dates and numbers"].split(" ")
        joineddate = splitdate[0] + " " + splitdate[1] + " " + splitdate[2]
        first_ma = datetime.strptime(joineddate, "%d %B %Y").date()
    except KeyError:
        first_ma = datetime.strptime(spc_data["Authority date"], "%d %B %Y").date()

    diff = first_ma - filing_date
    ext_date = exp_date + relativedelta.relativedelta(days=diff.days) - relativedelta.relativedelta(years=5)

    if ext_date > exp_date + relativedelta.relativedelta(years=5):
        ext_date = exp_date + relativedelta.relativedelta(years=5)
        return ext_date
    else:
        return ext_date

