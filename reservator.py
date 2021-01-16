from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
import smtplib, ssl
import time 
from Screenshot import Screenshot_Clipping 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_mail(message):
    port = 465  # For SSL
    password = 'GoogleLeganes01@'

    sender_email = "shursilver@gmail.com"
    receiver_email = "jorgedominguezpoblete@gmail.com"

    subject = "Dias disponibles Fitslanguage"   

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msgText = MIMEText('<b>%s</b>' % (message), 'html')
    msg.attach(msgText)

    img_name = 'screenshoot.png'
    with open(img_name, 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-Disposition', 'attachment', filename=img_name)
        msg.attach(img)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

def login(driver):
    driver.maximize_window()
    driver.get('https://www.fitslanguage.com/login')
    driver.find_element_by_name("email").send_keys("jorgedominguezpoblete@gmail.com")
    driver.find_element_by_name("pass").send_keys("FitsLeganes01@")
    driver.find_element_by_name("entrar").click()
    return driver

def reserva(driver, url_profesor, horarios_preferidos, reservas_max_dia):
    res = False
    try:
        profesor_col = driver.find_element_by_xpath('//a[@href="'+url_profesor+'"]')
        profesor_tarjeta = profesor_col.find_element_by_xpath("./../..")
        rows = profesor_tarjeta.find_elements_by_tag_name('tr') # get all of the rows in the table
        for index, row in enumerate(rows):             
            col = row.find_elements_by_tag_name('td')
            if(col[0].text in horarios_preferidos and col[1].text == 'Reservar'):
                if(reservas_max_dia > 1):
                    next_col = rows[index+1].find_elements_by_tag_name('td')
                    if(next_col[0].text not in horarios_preferidos or next_col[1].text != 'Reservar'):
                        continue
                print(profesor_col.text + "-> " +  col[0].text + ': ' + col[1].text)
                col[1].click()
                time.sleep(2)
                driver.find_element_by_name("confirmar").click()
                print("******* Clase Reservada ******* ")
                reservas_max_dia -= 1
                return True , reservas_max_dia
    except:
        print("El profesor " + url_profesor + " no está disponible ese día")

    return res, reservas_max_dia

def check_availability(driver, horarios_preferidos, dias_preferidos, profes_preferidos, reservas_max_dia, dias_reservados=list()):
    time.sleep(2)
    driver.get('https://www.fitslanguage.com/lessons/search')

    hora_inicio = driver.find_element_by_name('start_hour')
    horas = hora_inicio.find_elements_by_tag_name('option')
    for hora in horas:
        if(hora.get_attribute("value") == '19'):
            hora.click()
            break

    min_inicio = driver.find_element_by_name('start_minute')
    mins = min_inicio.find_elements_by_tag_name('option')
    for min in mins:
        if(min.get_attribute("value") == '30'):
            min.click()
            break

    driver.find_element_by_name('search').click()

    time.sleep(2)

    dias_reserva_links = list()
    for dia in dias_preferidos:
        dias_reserva_links += driver.find_elements_by_partial_link_text(dia)
        
    dias_reserva_text = [dia.text for dia in dias_reserva_links if dia.text not in dias_reservados]

    print(dias_reserva_text)
    for dia in dias_reserva_text:
        link_dia = driver.find_element_by_partial_link_text(dia)
        print("Reserva para el dia "+ link_dia.text)
        link_dia.click()
        time.sleep(2)
        for profe in profes_preferidos:
            nueva_busqueda, reservas_max_dia = reserva(driver, profe, horarios_preferidos, reservas_max_dia)
            if(nueva_busqueda):
                check_availability(driver, horarios_preferidos, dias_preferidos, profes_preferidos, reservas_max_dia, dias_reservados)
        dias_reservados.append(dia)
    
def make_screenshot(driver):
    ob=Screenshot_Clipping.Screenshot()
    ob.full_Screenshot(driver, save_path=r'.', image_name='screenshoot.png') 

def main():
    horarios_preferidos = ('19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30')
    dias_preferidos = ('Tue', 'Thu')
    reservas_max_dia = 2
    url_hannah = "https://www.fitslanguage.com/teacher/view/2874"
    url_cassie = "https://www.fitslanguage.com/teacher/view/1323"
    profes_preferidos = (url_hannah, url_cassie)

    driver = webdriver.Chrome(executable_path=r'D:\chromedriver_win32\chromedriver.exe')
    driver = login(driver)
    check_availability(driver, horarios_preferidos, dias_preferidos, profes_preferidos, reservas_max_dia)

    #make_screenshot(driver)
    
if __name__ == "__main__":
    main()