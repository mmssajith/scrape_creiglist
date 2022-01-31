import math
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import get_mail


# url = 'https://auburn.craigslist.org/bop/d/auburn-cyclingdeal-tailgate-bike-pads/7433657736.html'

# url = 'https://auburn.craigslist.org/d/for-sale/search/sss'
# url = 'https://buffalo.craigslist.org/d/garage-moving-sales/search/gms'

def get_location(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_list = soup.find_all('li')

    name_list = []
    for ele in all_list:
        try:
            link = ele.a.get('href')
            name = link.split('.')[0].split('://')[1]
            if name != 'www':
                if name != 'forums':
                    name_list.append(name)
        except:
            pass
    return name_list

def get_product_url(url):
    print("Getting Product URL")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_count = int(soup.find(class_="totalcount").text)
    link_list = set(())
    if total_count <= 120:
        link_list = set(())
        results = soup.find(id="search-results").find_all('a')
        for result in results:
            if len(result.get('href')) != 1:
                link_list.add(result.get('href'))
        link_list = list(link_list)
    else:
        pages_count = math.ceil(total_count / 120)
        for i in range(pages_count):
            response = requests.get(f'{url}?s={120 * i}')
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find(id="search-results").find_all('a')
            for result in results:
                if len(result.get('href')) != 1:
                    link_list.add(result.get('href'))
    print("Product URL is set")
    return list(link_list)

def get_email(text):
    email_list = set(())
    pattern_email = "\S+@\S+"
    email = re.findall(pattern_email, text)
    if len(email) != 0:
        for mail in email:
                email_list.add(mail)
    return email_list

def get_contact(text):
    contact_numbers = set(())
    pattern = ["\d{3}-\d{8}|\d{4}-\d{7}", "\(\d{2,4}\)\d{6,7}", "\d{3}-\d{3}-\d{3}", "\d{10}"]
    for i in range(len(pattern)):
        contact = re.findall(pattern[i], text)
        if len(contact) != 0:
            for number in contact:
                contact_numbers.add(number)
    return contact_numbers

def get_page_data(url):
    # print("Getting page data")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    data = {}
    try:
        data['Heading'] = soup.find(id='titletextonly').text
    except:
        data['Heading'] = ""
    try:
        data['Price'] = soup.find(class_='price').text
    except:
        data['Price'] = ""
    try:
        data['Location in header'] = soup.find(class_='postingtitletext').find('small').text.replace('(',"").replace(" ", "").replace(")","")
    except:
        data['Location in header'] = ""
    try:
        data['Body'] = soup.find(id='postingbody').text.strip().replace('QR Code Link to This Post', '').strip()
    except:
        data['Body'] = ""
    try:
        data['Date'] = soup.find(id='display-date').find('time').text.replace('\n', '').strip()
    except:
        data['Date'] = ""
    try:
        data['Location'] = soup.find(class_="crumb area").find('a').text
    except Exception as e:
        print(e)
        data['Location'] = ""
    try:
        data['Sale type'] = soup.find(class_="crumb section").text.strip().replace("\n>", "")
    except:
        data['Sale type'] = ""
    try:
        data['Category'] = soup.find(class_="crumb category").text.strip().split('-')[0]
    except:
        data['Category'] = ""
    try:
        data['By Dealer/By Owner'] = soup.find(class_="crumb category").text.strip().split('-')[1].strip()
    except:
        data['Category'] = ""
    

    email_in_head = get_email(data['Heading'])
    email_in_body = get_email(data['Body'])
    final_email_list = set(())
    for ele in email_in_body:
        final_email_list.add(ele)
    for ele in email_in_head:
        final_email_list.add(ele)
    final_email_list = list(final_email_list)
    if len(final_email_list) < 2:
        for _ in range(3 - len(final_email_list)):
            final_email_list.append('None')
    else:
        final_email_list = final_email_list[0:2]

    contact_in_head = get_contact(data['Heading'])
    contact_in_body = get_contact(data['Body'])
    final_contact_list = set(())
    for ele in contact_in_body:
        final_contact_list.add(ele)
    for ele in contact_in_head:
        final_contact_list.add(ele)
    final_contact_list = list(final_contact_list)
    if len(final_contact_list) < 3:
        for _ in range(3 - len(final_contact_list)):
            final_contact_list.append('None')
    else:
        final_contact_list = final_contact_list[0:3]
    data['Contact Number_1'] = final_contact_list[0]
    data['Contact Number_2'] = final_contact_list[1]
    data['Contact Number_3'] = final_contact_list[2]
    data['Email_1'] = final_email_list[0]
    data['Email_2'] = final_email_list[1]
    

    try:
        data['latitude'] = soup.find('div', {"id": "map"})["data-latitude"]
        data['longitude'] = soup.find('div', {"id": "map"})["data-longitude"]
    except:
        data['latitude'] = ""
        data['longitude'] = ""

    try:
        atr = []
        at_list = set(())
        attr = soup.find_all(class_="attrgroup")
        for att in attr:
            atr.append(att.text.strip().split("\n"))
        for atrib in atr[0]:
            try:
                if ": " in atrib:
                    atrib_ = atrib.split(": ")
                    data[atrib_[0]] = atrib_[1]
                else:
                    at_list.add(atrib)
                
                
            except Exception as e:
                print(e)
    except:
        pass
    at_list = list(at_list)
    data['Other Attributes'] = ",".join(at_list)
    data['Site URL'] = url
    img_links = []
    image_url_list = soup.find_all('img')
    for image in image_url_list:
        try:
            img_links.append(image['src'].replace('50x50c', '600x450'))
        except:
            img_links.append(image['src'])
    try:
        if len(img_links) > 5:
            img_links = img_links[0:5]
        else:
            for _ in range(5 - len(img_links)):
                img_links.append('None')
        data['Image URL 1'] = img_links[0]
        data['Image URL 2'] = img_links[1]
        data['Image URL 3'] = img_links[2]
        data['Image URL 4'] = img_links[3]
        data['Image URL 5'] = img_links[4]
    except:
        pass
    try:
        if '@' in get_mail.get_email(url):
            data['Creiglist Email'] = get_mail.get_email(url)
        else:
            data['Creiglist Contact'] = get_mail.get_email(url)
    except:
        data['Creiglist Email'] = ""

    return data

def create_csv(list_of_dict,location):
    df = pd.DataFrame(list_of_dict)
    df.to_csv(f"{location}_Sale.csv")


if __name__ == '__main__':
    location_list = get_location('https://www.craigslist.org/about/sites')
    for ele in location_list:
        url = f'https://{ele}.craigslist.org/d/for-sale/search/sss'
        print(url)
        final_data = []
        try:
            for elem in get_product_url(url):
                print("processing")
                final_data.append(get_page_data(elem))
        except KeyboardInterrupt:
            pass
        create_csv(final_data, f'{ele}')
    # print(get_page_data(url))


    