import logging, datetime
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, InlineQueryHandler
from datetime import date

import requests, json
from bs4 import BeautifulSoup

# Logger for troubleshooting
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="I'm a bot, please talk to me!"
        )


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

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


# Function to fetch and parse fuel prices from the webpage
async def fetch_fuel_prices(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Here, adapt the selection based on the actual HTML structure
            prices = soup.find_all('h6')
            return [price.get_text() for price in prices]
    except Exception as e:
        print(f"An error occurred: {e}")



# Command function to fetch and display fuel prices
async def fuelprices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    async def read_jsonfile_into_variable():
        try:
            # Read the data from the file
            with open('fuel_data.json', 'r') as file:
                data = json.load(file)
                file.close
        except json.JSONDecodeError:
            # If the file is empty or contains invalid JSON, initialize it.
            data = {"prices": []}
        return data


    async def save_json_data_to_file(new_json_data):
        with open('fuel_data.json', 'w') as file:
            json.dump(new_json_data, file, indent=4)
            file.close
        return


    async def save_fuel_data(prices):
        json_data = read_jsonfile_into_variable()
        '''Add statement to check if file already contains the data for date.today()'''
        if date.today in json_data['prices']:
            return
        # def add_new_data_to_json_file()
        
        new_data = {
            f"{date.today()}": {
                "E95": str(prices[0]),
                "E98": str(prices[1]),
                "Diesel": str(prices[2])
            }
        }
        
        # updated data string -->
        json_data['prices'].append(new_data)
        save_json_data_to_file(json_data)
            
    url = "https://www.tankille.fi/suomi/"
    prices = fetch_fuel_prices(url)
    
    save_fuel_data(prices)
    
    if prices:
        message = f"95 {prices[0]} \n98 {prices[1]} \nDiesel {prices[2]} \n(prices are for last 24 hours, source: https://www.tankille.fi/suomi/)"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = "Failed to retrieve fuel prices."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)






if __name__ == '__main__':
    file_url = str(input("insert file path: "))
    token = ''
    if token == '':
        with open(file_url, 'r') as file:
            token = file.read()

    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)
    fuel_prices = CommandHandler('prices', fuelprices)
    get_help = CommandHandler('help', help)
    # tori_sangyt = CommandHandler('sänky', tori_sanky)

    # All of the handlestoken

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



'''
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def fetch_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")
    # await update.message.reply_text(f'Polttoaineen keskihinta suomessa tänään {update.effective_user.first_name}')


def extract_data(html_content):
    osat = html_content.rstrip().split('table')
    haluttu_osa = osat[1].split('<td>')[2]
    hinnat = []
    i = 0
    hinta = ''
    for char in haluttu_osa:
    # print(str(char) + '\n')
        if char.isdigit():
            hinta += str(char)
            i += 1
            if i == 1:
                hinta += ','
        if i < 4:
            continue
        else:
            hinnat.append(hinta)
            hinta = ''
            i = 0
    return hinnat



    
def hinta(update: Update, Context: CallbackContext) -> None:
    url='https://www.polttoaine.net/index.php'
    html_content = fetch_webpage(url)
    if html_content:
        hinnat = extract_data(html_content)
        update.message.reply_text(f"Eilisen keskihinta; 95: {hinnat[0]}, 98: {hinnat[1]}, diesel:  {hinnat[2]} ")
    else:
        update.message.reply_text("Failed to retrieve data.")




app = ApplicationBuilder().token("6379170697:AAH38nT_w93ufverF8ki6xClntoMKwpnRU8").build()

#handler for the '/start' command
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("hinta", hinta))

#start the bot
app.run_polling()'''