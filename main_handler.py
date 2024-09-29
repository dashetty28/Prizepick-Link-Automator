import signal
import sys
from seleniumbase import SB
from dubclub_handler import DubClubBot
from prize_picks_handler import PrizePicksHandler
import time
import gc
from multiprocessing import Process, current_process
import logging
import datetime
import os


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def handle_account(dc_username, dc_password, pp_email, pp_password, one_unit, lat, lon, see):
    headless = False
    if see == 'n':
        headless = True  # Use headless mode if 'see' is 'n'

    process_name = current_process().name
    with SB(uc=True, headless=headless) as sb:  # Use the headless variable correctly here
        print(f"{process_name} - Starting selenium for {pp_email}")
        time.sleep(5)

        dub_club_bot = DubClubBot(sb, dc_username, dc_password)
        prizepicks_handler = PrizePicksHandler(sb, pp_email, pp_password, one_unit, lat, lon)
        
        logging.info(f"{process_name} - Starting dubclub login process")
        dub_club_bot.login()
        logging.info(f"{process_name} - Starting prizepicks login process")
        prizepicks_handler.login()
        logging.info(f"{process_name} - Completed login process")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'login_attempt_{timestamp}.png'
        sb.save_screenshot(filename)
        
        # Close extra tabs opened during the login process
        while len(sb.driver.window_handles) > 1:
            sb.switch_to_window(sb.driver.window_handles[-2])
            sb.driver.close()

        sb.switch_to_window(sb.driver.window_handles[0])

        while True:
            dub_club_bot.monitor_page()

            # PrizePicksHandler usage
            for link, unit in zip(dub_club_bot.pp_links, dub_club_bot.units):
                logging.info(f"{process_name} - Handling PrizePicks for link: {link}")
                prizepicks_handler.handle_prizepicks(link, unit)
                logging.info(f"{process_name} - Completed handling PrizePicks for link: {link}")

            time.sleep(5)
            logging.info(f"{process_name} - TABS OPEN: {len(sb.driver.window_handles)}")

            window_handles = sb.driver.window_handles
            for i in range(len(window_handles) - 1, 0, -1):
                sb.switch_to_window(window_handles[i])
                sb.driver.close()
                logging.info(f"{process_name} - Closed tab {i}")

            # Switch back to the first tab
            sb.switch_to_window(window_handles[0])
            logging.info(f"{process_name} - Switched back to the first tab.")

            prizepicks_handler.clear_browser_data()
            gc.collect()


def main():

    # List of PrizePicks account credentials and one_unit values
    prizepicks_accounts = [
    ]

    processes = []

    for pp_email, pp_password, one_unit, lat, lon, see in prizepicks_accounts:
        process = Process(target=handle_account, args=(dc_username, dc_password, pp_email, pp_password, one_unit, lat, lon, see))
        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Optionally, wait for all processes to complete
    for process in processes:
        process.join()


if __name__ == "__main__":
    # Protect multiprocessing entry point
    main()
