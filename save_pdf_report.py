from selenium import webdriver
import time
import os

print_button = driver.find_element_by_tag_name("button")
print_button.click()
time.sleep(2)

driver.switch_to_window(driver.window_handles[-1])

save_button = driver.find_element_by_xpath("//*[@id='print-header']/div/button[1]")
save_button.click()


rep_path = "d:/tmp2/aaa.pdf"
os.system('chrome_saveas.exe %s' rep_path)

driver.switch_to_window(driver.window_handles[0])




# screenshot
