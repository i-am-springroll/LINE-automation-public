import requests
from bs4 import BeautifulSoup
import urllib
import json
import datetime


class App:
    def __init__(self, city):
        self.URL_YAHOO = "https://www.yahoo.co.jp/"
        self.TOKEN_LINE = "yxjyBxMI2lgndYQTKq9r5ySuRuWEN5nNvjGJJdgFJWX"
        self.API_LINE = "https://notify-api.line.me/api/notify"
        self.TOKEN_WEATHER = "9d5eb5e621c6eaa6ca8507e8e7fd6a24"
        self.API_WEATHER = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&lang=ja&units=metric".format(city, self.TOKEN_WEATHER)
        self.TOKEN_NOTION = "secret_mYrAOtoPWbdMdPuk0RTQJHqlHdSWpFVWA4AjfpkWV8N"
        self.NOTION_DATABASE_ID_WEEKLY = "f83e4481abf043b4a7f466ac20098c3b"
        self.NOTION_DATABASE_ID_ONEDAY = "f4275d3ca92a48409c4fa7fab0510c2e"
        self.NOTION_DATABASE_URL_WEEKLY = f'https://api.notion.com/v1/databases/{self.NOTION_DATABASE_ID_WEEKLY}/query'
        self.NOTION_DATABASE_URL_ONEDAY = f"https://api.notion.com/v1/databases/{self.NOTION_DATABASE_ID_ONEDAY}/query"
        self.list_title = []
        self.list_url = []
        self.item_name = []
        self.item_tag = []
        self.message_yahoo = ""
        self.message_weather = ""
        self.message_notion = ""
        self.dt = datetime.datetime.now()
        self.dt_adjust = self.dt + datetime.timedelta(hours=9)
        self.today_year = self.dt_adjust.year
        self.today_date = self.dt_adjust.date()
        self.today_hour = self.dt_adjust.hour
        self.today_day = self.today_date.weekday()

    def index_app(self):
        self.get_notion_data()
        self.get_weather()
        self.scraping_yahoo()
        self.send_to_line("\n{}({})\n\nToday's Schedules&Tasks:{}\n\nWeather{}\n\nRecentry NEWS{}".format(self.today_date, self.today_date.strftime("%a"), self.message_notion, self.message_weather, self.message_yahoo))


    def scraping_yahoo(self):
        self.html = requests.get(self.URL_YAHOO)
        self.soup = BeautifulSoup(self.html.content, "html.parser")

        self.topic = self.soup.find(id="tabpanelTopics1")
        for i in self.topic.find_all("a"):
            self.list_title.append(i.text)
            self.get_news_url = i.get("href")
            self.show_news_url = urllib.parse.urljoin(self.URL_YAHOO, self.get_news_url)
            self.list_url.append(self.show_news_url)
            self.message_yahoo += "\n{}\n{}".format(i.text, self.show_news_url)
        
    def get_weather(self):
        self.jsondata = requests.get(self.API_WEATHER).json()
        self.message_weather += "\ncity:{}".format(self.jsondata["name"])
        self.message_weather += "\ntemp:{}".format(self.jsondata["main"]["temp"])
        self.message_weather += "\nweather:{}".format(self.jsondata["weather"][0]["description"])

    def get_notion_data(self):
        self.headers_notion = {'Authorization': f'Bearer {self.TOKEN_NOTION}',
          'Notion-Version': '2021-08-16',
          'Content-Type': 'application/json'}

        self.payload_notion = {'page_size': 20}

        self.response = requests.post(self.NOTION_DATABASE_URL_WEEKLY, data=json.dumps(self.payload_notion), headers=self.headers_notion).json()
        self.result = self.response["results"]

        for i in range(len(self.result)):
            if self.result[i]["properties"]["day"]["number"] == self.today_day or self.result[i]["properties"]["day"]["number"] == 7:
                self.message_notion += "\n{}".format(self.result[i]['properties']['Name']['title'][0]['plain_text'])

        self.response = requests.post(self.NOTION_DATABASE_URL_ONEDAY, data=json.dumps(self.payload_notion), headers=self.headers_notion).json()
        self.result = self.response["results"]
        
        for i in range(len(self.result)):
            if self.result[i]["properties"]["Date"]["date"]["start"] == str(self.today_date):
                self.message_notion += "\n{}".format(self.result[i]["properties"]["Name"]["title"][0]["plain_text"])

        if self.message_notion == "":
            self.message_notion += "\nNothing."

    def send_to_line(self, msg):
        self.headers_line = {"Authorization": f"Bearer {self.TOKEN_LINE}"}
        self.payload_line = {"message": f"message: {msg}"}
        requests.post(self.API_LINE, headers=self.headers_line, data=self.payload_line)


if __name__ == "__main__":
    app = App("Hanamaki, JP")
    app.index_app()