from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
import csv
import config
class Ml_data_miner():
    def __init__(self):
        url = 'https://listado.mercadolibre.com.uy/inmuebles/maldonado/punta-del-este/dueno/'
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        #options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        try:
            self.driver = webdriver.Chrome(executable_path=".\chromedriver.exe", options=options)
        except:
            self.driver = webdriver.Chrome("./chromedriver", options=options)
        self.driver.get(url)
        self.client_name, self.client_phone, self.client_post_url = 'N/A', 'N/A', 'N/A'
    def get_data(self):
        
        time.sleep(2)
        cnt = 1
        pages = self.driver.find_elements_by_xpath('//*[@id="results-section"]/div[2]/ul/li')
        print("Pages number ----> {}".format(len(pages)))
        while cnt < len(pages):

            # Validadon si es necesario hace un cambio de pagina
            if cnt >= 2:
                # Cambios de pagina
                nextL = self.driver.find_element_by_xpath('//*[@id="results-section"]/div[2]/ul/li[' + str(cnt) + ']/a').get_attribute('href')
                self.driver.get(nextL)
            cnt += 1

            # Enumerando lista de resultado de la pagina actual
            lis = self.driver.find_elements_by_xpath('//*[@id="searchResults"]/li')
            
            
            for li in lis:
                try:
                    # Extrayendo hyperlinklnk
                    lnk = li.find_element_by_tag_name('a').get_attribute('href')
                    
                    # Abierdo link en nueva pagina
                    newTab = 'window.open("' + lnk + '", "_blank");'
                    self.driver.execute_script(newTab)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(3)
                    # Extrayendo nombre
                    self.client_name = self.driver.find_element_by_xpath('//*[@id="root-app"]/div[1]/div/div[2]/section[1]/p[3]')
                    print(self.client_name.text)

                    # Extrayendo Telefono
                    try:
                        nextL = self.driver.find_element_by_xpath('//*[@id="root-app"]/div[1]/div/div[2]/section[1]/p[5]/label').click()
                        self.client_phone = self.driver.find_element_by_xpath('//*[@id="root-app"]/div[1]/div/div[2]/section[1]/p[5]')
                    except:
                        nextL = self.driver.find_element_by_xpath('//*[@id="root-app"]/div[1]/div/div[2]/section[1]/p[7]/label').click()
                        self.client_phone = self.driver.find_element_by_xpath('//*[@id="root-app"]/div[1]/div/div[2]/section[1]/p[7]')
                    print(self.client_phone.text)
                    self.client_post_url = lnk
                    print(self.client_post_url)

                    # Escribiendo datos en documento
                    sent = self.sent_message()
                    if sent:
                        self.write()
                        self.driver.execute_script('window.close()')
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        print("##############################")
                        print("Data extraction is success.")
                        print("##############################")
                    else:
                        print("##############################")
                        print("Some error.")
                        print("##############################")
                except:
                    print("##############################")
                    print("Data can not be extrated from the url.")
                    print("##############################")

        self.driver.close()

    def sent_message(self):
        try:
            element = self.driver.find_element_by_xpath('//*[@id="question-buttonMAIN"]')
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(3)
            try:
                self.driver.find_element_by_xpath('//*[@id="modal-question-unregistered-form-contactUserFirstName"]').send_keys(config.name)
                self.driver.find_element_by_xpath('//*[@id="modal-question-unregistered-form-contactUserLastName"]').send_keys(config.lastname)
                self.driver.find_element_by_xpath('//*[@id="modal-question-unregistered-form-contactEmail"]').send_keys(config.email)
            except:
                pass
            time.sleep(3)
            self.driver.find_element_by_xpath('//*[@id="modal-question-unregistered-form-modal-unregistered-questions-btn"]').click()
            time.sleep(5)
            print('Message send')
        except:
            pass
        return True


    def write(self):
        data=[]
        data.append(str(self.client_name.text))
        data.append(str(self.client_phone.text))
        data.append(str(self.client_post_url))
        with open('data.csv', 'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(data)
            print(data)
        csvFile.close()



if __name__ == '__main__':
    col = ['NOMBRE', 'TELEFONO', 'URL']

    with open('data.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(col)

    extractor = Ml_data_miner()
    extractor.get_data()
    