import logging, datetime
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, InlineQueryHandler
from datetime import date
from openai import OpenAI
import os

import requests, json
from bs4 import BeautifulSoup

# Logger for troubleshooting
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# (Deactivated) this function overloaded GPT requests. Do i have enough credits???? right subscription plan??? 
'''async def chat_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    client = OpenAI()

    try:
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "you are chat gpt and receiving a test message from me using my api token. The message received is sent using a few lines of python code."},
            {"role": "user", "content": "this is my first api message im trying to trouble shoot, you are interacting with a request made with python. This code was provided on the openai website on the quick start tutorial. I edited this message to trouble shoot why im getting an error about insufficient funds"}
        ]
        )
        message = completion.choices[0].message
    except:
        message = 'too many requests. Let it cool down for a few hours! (dont know how many hours tho)'
    

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)'''
# Reults in:   httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 429 Too Many Requests"     

# (deactivated) Function not working and always causes exception (needs to be debugged)
'''async def electricity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://www.fortum.fi/kotiasiakkaille/sahkoa-kotiin/opas/spot-hinta?utm_term=&utm_campaign=Search+-+Dynamic+-+tCPA+-+05/20&utm_source=adwords&utm_medium=ppc&hsa_acc=3752639039&hsa_cam=10116276415&hsa_grp=103164997842&hsa_ad=519234340308&hsa_src=g&hsa_tgt=aud-2079771752762:dsa-465869455172&hsa_kw=&hsa_mt=&hsa_net=adwords&hsa_ver=3&gad_source=1&gclid=Cj0KCQiAmNeqBhD4ARIsADsYfTdQVqbJVWcc9ODzk0P9WlUSvOM8bhejCqx5EDJBz4gZAn0t-ukb8TYaAlE4EALw_wcB'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Here, adapt the selection based on the actual HTML structure
            eprice = soup.find('p', _class='Boxweb__StyledBox-phd6kb-0 eLEKHk').get_text()
            message = f"date: {date.today}\nCurrent electricity price: {eprice}"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    except:
        message = 'error occured, data not found or other error.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)'''


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="I'm a bot, please talk to me!"
        )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


# inline_query function to learn about inline query
async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


# Handling of unknown requests / commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. type /help to get all available commands")


# Help message updated mechanicaly
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = """
    /help - Show this help message
    /prices - Fetch and display avg/24h fuel prices. 
    @poltt0aine_bot (input text) to use the bot to send msg.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)


# Command function to fetch and display fuel prices
async def fuelprices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def check_todays_data(file):
        for item in prices['prices']:
            try:
                if item[f'{date.today()}']:
                    return item
            except:
                continue
        return None

    def read_jsonfile_into_variable():
            try:
                # Read the data from the file
                with open('fuel_data.json', 'r') as file:
                    data = json.load(file)
                    file.close
            except json.JSONDecodeError:
                # If the file is empty or contains invalid JSON, initialize it.
                data = {"prices": []}
            return data
    
    def save_fuel_data(prices):

        # read datafile into a variable
        

        # save (old + new data) --> json file
        def save_json_data_to_file(new_json_data):
            with open('fuel_data.json', 'w') as file:
                json.dump(new_json_data, file, indent=4)
                file.close
            return

        # read datafile into a variable
        json_data = read_jsonfile_into_variable()
        
        new_data = {
            f"{date.today()}": {
                "E95": str(prices[0]),
                "E98": str(prices[1]),
                "Diesel": str(prices[2])
            }
        }

        # updated data string --> append to old data
        json_data['prices'].append(new_data)

        # save (old + new data) --> json file
        save_json_data_to_file(json_data)
        return
            
    def fetch_fuel_prices(url):
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                prices = BeautifulSoup(response.text, 'html.parser').find_all('h6')
            
                return [str(price.get_text()).replace(" ", "") for price in prices]
        except Exception as e:
            print(f"An error occurred: {e}")

    
    # check if todays data has been aquired already and return
    # Iterating the data collected
    prices = read_jsonfile_into_variable()
    
    todays_data = check_todays_data(prices)
    
    if todays_data == None:
        url = "https://www.tankille.fi/suomi/" 
        prices = fetch_fuel_prices(url)
           
        save_fuel_data(prices)
        
        if prices:
            message = f"date: {date.today()}\n\n95 {prices[0]} \n\n98 {prices[1]} \n\nDiesel {prices[2]} \n\n(prices are for last 24 hours, prices fetched from: https://www.tankille.fi/suomi/)"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            message = "Failed to retrieve fuel prices."
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f"date: {date.today()}\n\n95 {todays_data[str(date.today())]["E95"]} \n\n98 {todays_data[str(date.today())]["E98"]} \n\nDiesel {todays_data[str(date.today())]["Diesel"]} \n\n(prices are for last 24 hours, source: https://www.tankille.fi/suomi/) \n\n (todays fuel price was found from database)"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    

if __name__ == '__main__':
    # load bot-token to start your bot
    def load_bot_token():
        while True:
            try:
                file_url = str(input("insert path for token:\n"))
            
                with open(file_url, 'r') as file:
                    token = file.read()
                    file.close
                break

            except:
                print('file not found, try again.\n')
        
        return token
    
    application = ApplicationBuilder().token(load_bot_token()).build()
    
    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    fuel_prices = CommandHandler('fprice', fuelprices)
    get_help = CommandHandler('help', help)

    # Deactivated handlestokens
    '''gpt_chat = CommandHandler('gpt', chat_gpt)'''
    '''electricity_price = CommandHandler('eprice', electricity)'''

    # All of the handlestoken

    # deactivated functions
    '''application.add_handler(electricity_price)'''
    '''application.add_handler(gpt_chat)'''

    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(fuel_prices)
    application.add_handler(get_help)
    
    

    inline_caps_handler = InlineQueryHandler(inline_caps)
    application.add_handler(inline_caps_handler)

    # this one has to be last to work
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()


