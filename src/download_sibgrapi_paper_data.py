from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


sibgrapi_raw_html_page = simple_get("http://www.mat.puc-rio.br/sibgrapi2019/PreliminaryProgramSibgrapi2019.htm")
sibgrapi_html_page = BeautifulSoup(sibgrapi_raw_html_page, 'html.parser')
# for p in sibgrapi_html_page.select("p"):
#     for span in p.select("span"):
#         if span["class"] == "c12":
#         print(span)

sibgrapi_data = {}

last_presentation = ""
presentation_id = 0
last_session = ""
session_id = 0

for tr in sibgrapi_html_page.select("tr"):
    for td in tr.findAll("td", {"class": ["c130", "c127", "c43", "c327", "c36"]}):
        for span in td.findAll("span", {"class": "c78"}):
            if span.text != "@" and span.text != "\xa0":
                last_session = "session_" + str(session_id)
                sibgrapi_data[last_session] = {
                    "session_name": span.text,
                    "presentations": {}
                }
                print("Session: " + span.text)
                session_id += 1
                presentation_id = 0
                last_presentation = ""

    for td in tr.findAll("td", {"class": ["c129", "c126", "c90", "c19", "c73", "c15"]}):
        for p in td.findAll("p", {"class": "c23"}):
            for span in p.findAll("span", {"class": ["c12", "c78", "c173"]}):
                if span.text != "" and span.text != "(":
                    last_presentation = "presentation_" + str(presentation_id)
                    sibgrapi_data[last_session]["presentations"][last_presentation] = {
                        "title": span.text,
                        "authors": []
                    }
                    print("Title: " + span.text)
                    presentation_id += 1

    if last_presentation != "":
        for td in tr.findAll("p", {"class": ["c30", "c5"]}):
            for span in td.findAll("span", {"class": "c12"}):
                print(" " + span.text)
                sibgrapi_data[last_session]["presentations"][last_presentation]["authors"].append(span.text)

with open("sibgrapi_papers.json", 'w') as f:
    json.dump(sibgrapi_data, f)
