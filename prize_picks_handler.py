from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
import datetime
import re




FINAL_LINK = "https://app.prizepicks.com/board"
LOGIN = "https://app.prizepicks.com/login?utm_source=landing&utm_medium=website"
class PrizePicksHandler:




    def __init__(self, sb, email, password, one_unit, lat, lon):
        self.one_unit = one_unit
        self.sb = sb
        self.email = email
        self.password = password
        self.logged_in = False
        self.lat = lat
        self.lon = lon




    def set_geolocation(self, lat, lon, origin):
        # Reset and grant geolocation permissions
        self.sb.execute_cdp_cmd("Browser.resetPermissions", {})
        self.sb.execute_cdp_cmd("Browser.grantPermissions", {
            "origin": origin,
            "permissions": ["geolocation"]
        })




        # Set geolocation coordinates
        self.sb.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": lat,
            "longitude": lon,
            "accuracy": 100
        })






    def login(self):
        self.set_geolocation(self.lat, self.lon, "https://www.prizepicks.com/")
        self.sb.execute_script(f"window.open('https://www.prizepicks.com/');")
        self.sb.switch_to_window(self.sb.driver.window_handles[-1])
        print("opened prizepicks.com")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'login_attempt_{timestamp}.png'
        self.sb.save_screenshot(filename)
        
        time.sleep(1)
        '''
        self.set_geolocation(self.lat, self.lon, LOGIN)
        self.sb.click('//*[@id="navbar-login-button"]')
        print("opened first log in")
        self.set_geolocation(self.lat, self.lon, LOGIN)
        self.sb.switch_to_window(self.sb.driver.window_handles[-1])
        # self.sb.driver.close()
        self.sb.switch_to_window(self.sb.driver.window_handles[1])
        
        
        time.sleep(2)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'login_attempt_{timestamp}.png'
        self.sb.save_screenshot(filename)
        
        self.set_geolocation(self.lat, self.lon, LOGIN)
        self.sb.click('//*[@id="navbar-login-button"]')
        print("opened second log in")
        self.sb.switch_to_window(self.sb.driver.window_handles[-1])
        # self.sb.driver.close()
        self.sb.switch_to_window(self.sb.driver.window_handles[1])
        time.sleep(1)
        '''
        
        self.set_geolocation(self.lat, self.lon, LOGIN)
        self.sb.execute_script(f"window.open('https://app.prizepicks.com/login?utm_source=landing&utm_medium=website');")
        self.sb.switch_to_window(self.sb.driver.window_handles[-1])
        print("opened third login")
        
        
        time.sleep(2)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'login_attempt_{timestamp}.png'
        self.sb.save_screenshot(filename)
        # Set geolocation again before login


        

        #time.sleep(5)


        # Wait for the login page to load and enter the credentials
        try:
            self.sb.wait_for_element_visible('//*[@id="email-input"]', timeout=10)
            self.sb.type('//*[@id="email-input"]', self.email)
            self.sb.type('//*[@id="sign-up-container"]/div[1]/div[2]/form/div[2]/input', self.password)
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - Entered login credentials.")




            # Click the "Log In" button
            self.sb.click('button:contains("Sign in")')
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - Clicked on Log In button.")
            self.logged_in = True


            welcome_text = "WELCOME TO PRIZEPICKS"
            self.sb.wait_for_text(welcome_text, timeout=30)
            print(f"{self.email} - Successfully logged in and the welcome message appeared.")
        except Exception as e:
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - An error occurred while trying to enter login credentials: {e}")




    def handle_prizepicks(self, initial_link, unit):
        try:
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - START")
            start_time = time.time()




            # Open the initial PrizePicks link
            self.set_geolocation(self.lat, self.lon, FINAL_LINK)
            self.sb.execute_script(f"window.open('{initial_link}');")
            self.sb.switch_to_window(self.sb.driver.window_handles[-1])
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - Link opened.")
            try:
                # Wait for the button to be visible for up to 2 seconds
                 if self.sb.is_element_present("//button[contains(text(), 'Edit Lineup')]", timeout = 2):
                    self.sb.click("//button[contains(text(), 'Edit Lineup')]")
                    print(f"{time.strftime('%H:%M:%S')} - Edit Lineup button found")
            except:
                # If the element is not found within 2 seconds, this block is executed
                print(f"{time.strftime('%H:%M:%S')} - Edit Lineup button not found")



            self.sb.click('//*[@id="lineup_copied"]/div[1]/div[2]/div')


            # Try to click the submit lineup button again
            self.submit_lineup(unit)




            end_time = time.time()
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - Total time taken: {end_time - start_time:.2f} seconds")
       
        except Exception as e:
            print(f"{self.email} - error occured: {e}")




        finally:
            print(f"{time.strftime('%H:%M:%S')} - {self.email} - Script finished.")


    def submit_lineup(self, unit):
            self.set_geolocation(self.lat, self.lon, FINAL_LINK)




            # Try to click the submit lineup button again
            try:
                amount = int(unit * self.one_unit)
                if amount < 5:
                    amount = 5
                self.edit_amount_and_submit(amount)
               
                try:
                    popup_xpath = '//*[@id="1"]/div[1]/div[2]/div'
                    #self.sb.wait_for_element_visible(popup_xpath, by=By.XPATH, timeout=4)
                    message_text = self.sb.get_text(popup_xpath, by=By.XPATH)
                    self.sb.click(popup_xpath)
                    print(f"{self.email} - Message appeared: {message_text}")
                    if "successfully submitted" in message_text.lower():
                        pass
                    elif "no longer available" in message_text.lower() or "removed" in message_text.lower():
                        pass
                    elif "Maximum lineup amount" in message_text or "discounted" in message_text or "Maximum lineups" in message_text:
                        limit = self.extract_limit(message_text)
                        self.edit_amount_and_submit(limit)
                        #popup_xpath = '//*[@id="successfully-submitted-lineup!"]'
                        #self.sb.wait_for_element_visible(popup_xpath, by=By.XPATH, timeout=4)
                        #message_text = self.sb.get_text(popup_xpath, by=By.XPATH)
                        #self.sb.click(popup_xpath)
                        #print(f"Message appeared: {message_text}")
                    else:
                        self.edit_amount_and_submit("5")
                        '''
                        popup_xpath = '//*[@id="successfully-submitted-lineup!"]'
                        #self.sb.wait_for_element_visible(popup_xpath, by=By.XPATH, timeout=4)
                        message_text = self.sb.get_text(popup_xpath, by=By.XPATH)
                        self.sb.click(popup_xpath)
                        print(f"{self.email} - Message appeared: {message_text}")
                        '''
                       
                       
                except:
                    print(f"{self.email} - Popup message not found")
               


            except:
                print(f"{self.email} - Cannot submit lineup")
           
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'submit_attempt_{timestamp}.png'
            self.sb.save_screenshot(filename)


    def edit_amount_and_submit(self,amount):
        self.enter_bet_amount(int(amount))
        button_xpath = '//*[@id="lineup-menu-footer"]/div/form/div[2]/button'
        self.sb.wait_for_element_visible(button_xpath, timeout=10)
        self.sb.click(button_xpath)
        print(f"{time.strftime('%H:%M:%S')} - {self.email} - Clicked the submit lineup button.")




    def extract_limit(self, message):
        # Use regex to find the whole number after the dollar sign
        match = re.search(r'\$(\d+)', message)
        if match:
            return int(match.group(1))
        return None
       
    def enter_bet_amount(self, amount):
        # Define the XPath for the input box
        input_box_xpath = '//*[@id="entry-input subheading-md"]'
       
        try:
            # Clear the input box before entering the new amount
            self.sb.clear(input_box_xpath, by=By.XPATH)
            # Enter the specified amount into the input box
            self.sb.type(input_box_xpath, str(amount), by=By.XPATH)
            print(f"{self.email} - Entered bet amount: ${amount}")
        except Exception as e:
            print(f"{self.email} - An error occurred while entering the bet amount: {e}")


    def clear_browser_data(self):
        self.sb.delete_all_cookies()
        self.sb.clear_local_storage()
        self.sb.clear_session_storage()
        print("{self.email} - Cleared cookies, local storage, and session storage.")  





