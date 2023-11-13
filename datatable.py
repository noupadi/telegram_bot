import datatable as dt
import bs4, requests, json, datetime
from bs4 import BeautifulSoup


def fetch_fuel_prices(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Here, adapt the selection based on the actual HTML structure
            prices = soup.find_all('h6')
            return [price.get_text() for price in prices]
    except Exception as e:
        print(f"An error occurred: {e}")

def fuelprices():

    url = "https://www.tankille.fi/suomi/"
    prices = fetch_fuel_prices(url)
    
    if prices:
        message = f"95 {prices[0]} \n98 {prices[1]} \nDiesel {prices[2]} \n(prices are for last 24 hours, source: https://www.tankille.fi/suomi/)"
        keraa_tiedot_tietokantaan('fuel_data.json', prices)
        # with open('hintatietoja.txt', 'r'):
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = "Failed to retrieve fuel prices."
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


        def keraa_tiedot_tietokantaan(file_name, data):
            data_dict = {
                str(datetime.date.today()): {
                    "E95": data[0],
                    "E98": data[1],
                    "Diesel": data[2]
                }
            }
            #writing to jsonfile
            with open(file_name, 'a', encoding='utf-8') as file:
                json.dump(data_dict, file, ensure_ascii=False, indent=4)

fuelprices()