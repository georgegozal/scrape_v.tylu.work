import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv
import re


headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}


base_url = "https://v-tylu.work"


# This generator gives us every job advertisement url for every page
def start_requests():
    page_num = 1
    while True:
        url = f"https://v-tylu.work/en?transaction_type=offering-with-online-payment&page={page_num}"  
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.find_all('h2', class_="home-list-title")
        if len(items) > 0:
            for item in items:
                yield urljoin(base_url, item.select('a')[0]['href'])
        else:
            break
        page_num += 1


# This function goes to each jobs and collects and writes details in csv file
def parse_details(gen=start_requests()):

    columns = ['Title', 'Payment', 'Job type', 'Experience / Level', 'Description']

    for url in gen:
        time.sleep(0.5)

        mylist = {}

        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')

        try:
            # job title
            title = soup.find("span", {"id": "listing-title"}).getText().strip()
        except AttributeError:
            title = None
        mylist['Title'] = title
        details = soup.find_all('div', class_="col-12")

        for detail in details:
            # find all details which presented for each property
            s = detail.find_all('div', class_="selected")
            if s:
                # detail name
                detail_title = detail.b.text.replace(":", "")
                # if s
                if len(s) > 1:
                    # if each property has more than one value
                    detail_item =  [item.find_all("span")[1].text.replace("\n", "") for item in s]
                    if mylist.get(detail_title):
                        mylist[detail_title] += detail_item
                    else:
                        if len(detail_item) > 1:
                            mylist[detail_title] = detail_item
                        else:
                            mylist[detail_title] = [detail_item]
                else:
                    # if each property has only one value
                    detail_item = s[0].find_all("span")[1].text.replace("\n", "")
                    if mylist.get(detail_title):
                        mylist[detail_title].append(detail_item)
                    else:
                        mylist[detail_title] = [detail_item]
        try:
            # find description each job
            description = soup.find(class_="listing-description-content").text.replace("\n", "").strip() or None
        except AttributeError:
            description = None
        mylist["Description"] = description

        # sort and filter dictionary to have correct number of key values
        for name in columns:
            if name not in mylist.keys():
                mylist[name] = None
        mylist = dict(list(sorted(mylist.items()))[::-1])

        # write data to csv
        try:
            with open("result.csv", "r") as csv_file:
                header = csv_file.readline().replace("\n", "").split(',')
                print(len(list(csv_file.readlines())) +1, "Row has been writen.")
                with open("result.csv", "a") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=columns)
                    if header != columns:
                        writer.writeheader()
                    writer.writerow(mylist)

        except FileNotFoundError:
            with open("result.csv", "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=columns)
                writer.writeheader()
                writer.writerow(mylist)


if __name__ == "__main__":
    print(parse_details())
