from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
import smtplib, ssl
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
from PIL import Image 

logging.basicConfig(level=logging.INFO)

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
    msg_text = MIMEText('<b>%s</b>' % (message), 'html')
    msg.attach(msg_text)

    img_name = 'reservas.png'
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
        tarjeta_profesor = driver.find_element_by_xpath('//a[@href="'+url_profesor+'"]')
        tabla_profesor = tarjeta_profesor.find_element_by_xpath("./../..")
        filas = tabla_profesor.find_elements_by_tag_name('tr') # get all of the rows in the table
        for index, fila in enumerate(filas):             
            col = fila.find_elements_by_tag_name('td')
            hora = col[0].text
            reserva_disponible = col[1].text
            boton_reserva = col[1]
            if(hora in horarios_preferidos and reserva_disponible == 'Reservar'):
                if(reservas_max_dia > 1):
                    next_col = filas[index+1].find_elements_by_tag_name('td')
                    hora_siguiente = next_col[0].text
                    reserva_siguiente_disponible = next_col[1].text
                    if(hora_siguiente not in horarios_preferidos or reserva_siguiente_disponible != 'Reservar'):
                        continue
                logging.info(tarjeta_profesor.text + "-> " +  hora + ': ' + reserva_disponible)
                boton_reserva.click()
                sleep(1)
                driver.find_element_by_name("confirmar").click()
                logging.info("******* Clase Reservada ******* ")
                reservas_max_dia -= 1
                return True , reservas_max_dia
    except:
        logging.info("El profesor " + url_profesor + " no está disponible ese día")

    return res, reservas_max_dia

def filtro_hora(driver):
    hora_inicio = driver.find_element_by_name('start_hour')
    horas = hora_inicio.find_elements_by_tag_name('option')
    for hora in horas:
        if(hora.get_attribute("value") == '20'):
            hora.click()
            break

    min_inicio = driver.find_element_by_name('start_minute')
    mins = min_inicio.find_elements_by_tag_name('option')
    for min in mins:
        if(min.get_attribute("value") == '00'):
            min.click()
            break
    
    driver.find_element_by_name('search').click()
    sleep(1)

    return driver

def filtro_dias_clase(driver, dias_preferidos, dias_reservados):
    dias_reserva_links = list()
    for dia in dias_preferidos:
        dias_reserva_links += driver.find_elements_by_partial_link_text(dia)
    dias_reserva_text = [dia.text for dia in dias_reserva_links if dia.text not in dias_reservados]

    return driver, dias_reserva_text

def check_availability(driver, horarios_preferidos, dias_preferidos, profes_preferidos, reservas_max_dia, dias_reservados=None, contador_reservas=0):
    sleep(1)
    driver.get('https://www.fitslanguage.com/lessons/search')

    if(dias_reservados is None):
        dias_reservados = list()
    driver = filtro_hora(driver)
    driver, dias_reserva = filtro_dias_clase(driver, dias_preferidos, dias_reservados)

    logging.info(dias_reserva)
    for dia in dias_reserva:
        link_dia = driver.find_element_by_partial_link_text(dia)
        logging.info("Reserva para el dia "+ link_dia.text)
        link_dia.click()
        sleep(1)
        for profe in profes_preferidos:
            if(reservas_max_dia):
                nueva_busqueda, reservas_max_dia = reserva(driver, profe, horarios_preferidos, reservas_max_dia)
            if(nueva_busqueda):
                contador_reservas += 1
                check_availability(driver, horarios_preferidos, dias_preferidos, profes_preferidos, reservas_max_dia, dias_reservados, contador_reservas)
        dias_reservados.append(dia)

    return contador_reservas
    
def make_screenshot(driver):
    driver.get('https://www.fitslanguage.com/')
    sleep(1) 
    tabla_reservas = driver.find_element_by_class_name('ui.icon.warning.message') 
    location = tabla_reservas.location 
    size = tabla_reservas.size 
    driver.save_screenshot('fullPageScreenshot.png') 
    x = location['x'] 
    y = location['y'] 
    w = x + size['width'] 
    h = y + size['height'] 
    full_img = Image.open('fullPageScreenshot.png') 
    crop_img = full_img.crop((x, y, w, h)) 
    crop_img.save('reservas.png') 
    driver.quit() 


def main():
    horarios_preferidos = ('20:00', '20:30', '21:00', '21:30', '22:00', '22:30')
    dias_preferidos = ('Tue', 'Thu')
    reservas_max_dia = 2
    url_hannah = "https://www.fitslanguage.com/teacher/view/2874"
    url_cassie = "https://www.fitslanguage.com/teacher/view/1323"
    profes_preferidos = (url_hannah, url_cassie)

    driver = webdriver.Chrome(executable_path=r'D:\chromedriver_win32\chromedriver.exe')
    driver = login(driver)
    numero_reservas = check_availability(driver, horarios_preferidos, dias_preferidos, profes_preferidos, reservas_max_dia)

    mensaje_correo = "Se han reservado "+ str(numero_reservas) + " clases"
    logging.info(mensaje_correo)

    if(numero_reservas):
        make_screenshot(driver)
        send_mail(mensaje_correo)
    
if __name__ == "__main__":
    main()