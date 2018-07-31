import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()


driver.get("https://www.baidu.com")
elem = driver.find_element_by_id("kw")
elem.send_keys("mysql")

time.sleep(5)

driver.find_element_by_xpath('//*[@id="su"]').click()
elem.send_keys(Keys.RETURN)

time.sleep(5)

for i in range(18):
    js = "window.scrollTo(0,{})".format(i * 500)
    driver.execute_script(js)
    time.sleep(0.3)
result = driver.get_screenshot_as_file("/Users/niange/xxx.png")
print(result)
driver.close()
