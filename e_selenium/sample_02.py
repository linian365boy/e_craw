from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# define headless
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(chrome_options=chrome_options)

# do something
driver.get("http://www.szyoy.com")
#driver.find_element_by_id("menu-item-2").click()
#driver.find_element_by_id("menu-item-3").click()

# get html code source
#html = driver.page_source
result = driver.get_screenshot_as_file("/Users/linian/foo.png")
print(result)
driver.close()