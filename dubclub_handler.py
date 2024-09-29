import gc
from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
import re
import requests
import datetime


class DubClubBot:
    def __init__(self, sb, email, password):
        self.sb = sb
        self.email = email
        self.password = password
        self.bet_description = ""
        self.pp_links = []
        self.units = []
        self.found_prizepicks = False  # Add a flag to control the loop
        self.home_page_url = ""
        self.logged_in = False
        self.previous_published_at = None
        
    def login(self):
        self.sb.open("https://dubclub.win/r/subscriber-signin/")
        print("Opened DubClub website.")
        
        self.sb.sleep(0.5)

        # Click on the "Sign in using Twitter" button
        self.sb.click('a[title="Twitter"]')
        print("Clicked on Sign in using Twitter button.")

        self.sb.sleep(0.5)

        # Enter username
        self.sb.type('//*[@id="username_or_email"]', self.email)
        print("Entered username.")

        # Enter password
        self.sb.type('//*[@id="password"]', self.password)
        print("Entered password.")

        # Click the sign-in button
        self.sb.click('//*[@id="allow"]')
        print("Clicked on Sign in button.")

        self.sb.sleep(1)

        # Click the link on the homepage
        self.sb.click('//*[@id="product-1866"]/div[1]/a')
        print("Clicked on the link on the homepage.")


    def get_bet_description(self):
        return self.bet_description
   
    def get_pp_links(self):
        return self.pp_links.copy()
   
    def get_units(self):
        return self.units.copy()
   
    def check_and_scrape_prizepicks(self, link, message):
        try:
            print(f'dubclub link: {link}')
            self.found_prizepicks = True
            # Open the link in a new tab
            self.sb.execute_script(f"window.open('{link}');")
            self.sb.driver.switch_to.window(self.sb.driver.window_handles[-1])

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'dubclub_page_{timestamp}.png'
            self.sb.save_screenshot(filename)

            # Store links within a list
            links_xpath = '//*[@id="page-content"]/div/div[2]/div[1]/div[2]/div/p/a'
            links = self.sb.find_elements(By.XPATH, links_xpath)
            self.pp_links = [link.get_attribute('href') for link in links]
            print(f"Prizepicks/PP Links: {(self.pp_links)}\n")
            self.units = self.extract_units(message, len(self.pp_links))
            print(self.units)
        except Exception as e:
            print(f"An error occurred while checking for prizepicks: {e}")
       
    def extract_units(self, bet_description, num_links):
    # Find all unit values in the bet description
        units = re.findall(r'(\d+(\.\d+)?)\s*(U|unit|units)', bet_description, re.IGNORECASE)
       
        # Check for the presence of "each" in the bet description
        unit_values = []
        if "each" in bet_description.lower():
            for match in units:
                unit_value = float(match[0])
                unit_values.extend([unit_value] * num_links)
        else:
            # Extract the numeric part and convert to float
            unit_values = [float(unit[0]) for unit in units]


            # If we have fewer units than links, repeat the units
            if len(unit_values) == 0:
                return []
            elif len(unit_values) < num_links:
                unit_values = unit_values * (num_links // len(unit_values)) + unit_values[:num_links % len(unit_values)]
       
        # Trim the list to the number of links
        return unit_values[:num_links].copy()
   
    def monitor_page(self):
        referer = "https://dubclub.win"
        api_url = "https://dubclub.win/api/prd-ck8aj/textpicks/?page=1"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Access-Control-Allow-Origin": "localhost",
            "Cookie": "__stripe_mid=7369e841-6593-4732-83ba-682cbc790ad2480631; csrftoken=K2gkPwGC6MO9yaFVW67XmlCRaji2iVn9; sessionid=0ivugih2160a6qo1fh9j9gtgd0lhmhxg; ph_referrer=\"https://dubclub.win/t/lview/prd-ck8aj/u-4mmfe/?utm_medium=list&utm_source=web\"; ph_phc_lWlyKVnkFshWdXh95zWaBXIxB78xlZPNqjY2Guwdoj_posthog=%7B%22distinct_id%22%3A%22330026%22%2C%22%24sesid%22%3A%5B1721449890624%2C%220190ce67-010e-74e8-9dff-5e27fef1e171%22%2C1721449775374%5D%2C%22%24epp%22%3Atrue%7D",
            "Referer": "https://dubclub.win/t/prd-ck8aj/",
            "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        self.pp_links = []
        self.units = []


        while True:
            try:
                start_time = time.time()
                response = requests.get(api_url, headers=headers, timeout=5)  # Set a timeout of 10 seconds
                request_time = time.time() - start_time


                if response.status_code == 200:
                    data = response.json()


                    if data['results']:
                        first_result = data['results'][0]
                        sms_title = first_result.get('sms_title')
                        published_at = first_result.get('published_at')
                        message = first_result.get('message')
                        url = first_result.get('url')


                        if self.previous_published_at is None:
                            self.previous_published_at = published_at
                            print(f"Initial published_at: {published_at}")
                        elif self.previous_published_at != published_at:
                            print(f"{time.strftime('%H:%M:%S')} -published_at has changed from {self.previous_published_at} to {published_at}")
                            self.previous_published_at = published_at
                            if "prizepicks" in sms_title.lower() or "pp" in sms_title.lower():
                                new_url = referer + url
                                self.check_and_scrape_prizepicks(new_url, message)
                                break
                            else:
                                print(f"{time.strftime('%H:%M:%S')} - The title does not contain 'prizepicks' or 'pp'.")
                                print(f"title: {sms_title}")
                        else:
                            #print(f"{time.strftime('%H:%M:%S')} - published_at has not changed: {published_at}")
                            pass


                else:
                    print(f"{time.strftime('%H:%M:%S')} - Request failed with status code: {response.status_code}")
                    print(response.text)


                time.sleep(1.25)


            except requests.exceptions.RequestException as e:
                print(f"{time.strftime('%H:%M:%S')} - Error occurred while checking dubclub: {e}")
                time.sleep(0.75)








