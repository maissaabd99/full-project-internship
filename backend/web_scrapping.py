#import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import os

if not os.path.exists("backend/composants-info"):
    # Create a new directory if not exists
    os.makedirs("backend/composants-info")

driver1 = webdriver.Chrome()
driver2 = webdriver.Chrome()


i=0

try:
  for num_page in range(1,19): 
    search_results = None
    driver1 = webdriver.Chrome()
    driver1.get("https://www.tunisianet.com.tn/406-composant-informatique?page="+str(num_page)+"&order=product.price.asc")
    #results_page1 = driver.page_source
    print("Page title:", driver1.title)
    # Get search results
    search_results =  driver1.find_elements(By.XPATH,"//div[contains(@class,'item-product')]")
    print("Combien de div scrappés dans la page "+str(num_page)+" : ", len(search_results))
    for div in search_results:
        src =[]
        i = i + 1
        print("--------Nous sommes dans la div", i,"-----------")
        # Initialize variables for each iteration on a div element
        imgs = []
        a = None
        href_value = ""
        # Find the anchor element within the current div
        try:
            a = div.find_element(By.XPATH, ".//a[contains(@class, 'thumbnail product-thumbnail')]")
            href_value = a.get_attribute("href")
            print("href value :", href_value)

            # Open a new tab and navigate to the href value of each product
            driver2.execute_script("window.open('" + href_value + "', '_blank');")
            
            # Switch to the new tab of each product
            driver2.switch_to.window(driver2.window_handles[1])

            # Wait for the images to be present in the DOM
            wait = WebDriverWait(driver2, 100)
            imgs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//img[contains(@class, 'thumb js-thumb ')]")))
            
            #scrapp the reference name of each product 
            ref = div.find_element(By.XPATH, ".//span[contains(@class,'product-reference')]").text
            print("ref product is :",ref)
           
            # Create a new product directory if not exist
            path = "backend/composants-info/"+str(ref)
            if not os.path.exists(path):
                  os.makedirs("backend/composants-info/"+str(ref))

            #save product images to iys specific folder     
            for img in imgs:
               src.append(img.get_attribute("src"))
               #print("src of img",src)
            for j in range(len(src)):
               urllib.request.urlretrieve(str(src[j]),"backend/composants-info/"+str(ref)+"/img{}.jpg".format(j))
            print("Number of imgs found for this product url : ", len(imgs))

        except NoSuchElementException as e:
            print("An error occurred:", e)
        finally:
            # Close the product tab if it is open
            try:
                driver2.close()
            except:
                pass
            # Switch back to the original tab (initial products tab) if it still open
            try:
                driver2.switch_to.window(driver2.window_handles[0])
            except:
                pass
    print("--------------------------------------------------------------------")
  driver1.quit()
except TimeoutException as e:
    print("Timeout occurred:", e)

# Quit the drivers

driver2.quit()