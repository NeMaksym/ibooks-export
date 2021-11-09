import urls
import utils
from selenium import webdriver
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_token(email, password):
    try:
        # Initialize browser
        driver = webdriver.Chrome(ChromeDriverManager().install())
        wait = WebDriverWait(driver, 10)

        # Go to login page
        driver.get(urls.AUTH)
        wait.until(EC.url_contains(urls.LOGIN))

        # Manipulate login page
        switcher = driver.find_element_by_class_name('js-phone-form-to-username-password')
        switcher.click()

        login_input = driver.find_element_by_class_name('js-username-password-form-input')
        login_input.send_keys(email)

        pass_input = driver.find_element_by_class_name('js-username-password-form-password-input')
        pass_input.send_keys(password)

        submit_btn = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[3]/div[1]/div/form/div[4]/button')
        submit_btn.click()

        # Manipulate confirmation page
        wait.until(EC.url_contains(urls.CONFIRMATION))
        approve_btn = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div/form/div[1]/div/button')
        approve_btn.click()

        # Get token from url
        wait.until(EC.url_contains(urls.TOKEN))
        parsed_url = urlparse(driver.current_url)
        parsed_fragment = parse_qs(parsed_url.fragment)
        access_token = parsed_fragment.get('access_token')[0]

        # Quite
        driver.quit()

        return access_token

    except Exception as e:
        utils.save_to_log(f"Failed to get the access token: {e}")
        return None
