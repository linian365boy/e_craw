from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()


driver.get("http://www.python.org")
elem = driver.find_element_by_name("q")
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)

result = driver.get_screenshot_as_file("/Users/linian/xxx.png")
print(result)
driver.close()