import os
import nextcord as discord
import requests
import json
import speech_recognition as sr
from dotenv import load_dotenv
from translate import Translator
import pyttsx3
from gtts import gTTS
import asyncio
from nextcord.ext import commands

load_dotenv()
APIkey = os.getenv("CARTER_API_KEY")
DiscordAPI = os.getenv("DISCORD_API_KEY")

RawUIName = "Holo"
r = sr.Recognizer()

print(f"{RawUIName} is Online...")
engine = pyttsx3.init()

vc = None

intents = discord.Intents.all()
client = discord.Client(intents=intents)
intents.guild_messages = True
bot = commands.Bot(command_prefix='!')


@client.event
async def on_message(message):


    global vc

    if message.author == client.user:
        return

    User = message.author
    sentence = message.content
    sentence = sentence.lower()
    UIName = RawUIName.lower()



    if message.content.startswith('!holo'):
        await message.channel.send(
            "Natürlich, aber bitte bedenke, dass ich den Chat aufnehme und dafür lerne, euch zu erkennen und dass das ganze hier Beta ist.")

        if message.author.voice is None:
            await message.channel.send("Du bist in keinem Voice-Channel.")
            return

        vc = await message.author.voice.channel.connect()

        await message.channel.send("Ich höre zu...")
        while True:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)

            try:
                text = r.recognize_google(audio, language="de-DE")
                print(f"Recognized text: {text}")

                SendToCarter(text, User, APIkey)
                with open("CarterResponse.txt") as f:
                    ResponseOutput = f.read()

                translator = Translator(to_lang="de", from_lang="en")
                ResponseOutput = translator.translate(ResponseOutput)



                tts = gTTS(text=ResponseOutput, lang='de')
                tts.save('response.mp3')
                print(ResponseOutput)

                # Check if the voice client is already playing audio
                while vc.is_playing():
                    await asyncio.sleep(0.1)

                # Play the audio and wait for it to finish
                vc.play(discord.FFmpegPCMAudio('response.mp3'))
                while vc.is_playing():
                    await asyncio.sleep(0.1)

            except sr.UnknownValueError:
                print("Could not recognize speech")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

            if 'holo leave' in sentence.lower():
                await vc.disconnect

        await vc.disconnect()

    elif '!holo' in sentence:
        SendToCarter(sentence, User, APIkey)
        with open('CarterResponse.txt') as f:
            ResponseOutput = f.read()
            translator = Translator(to_lang="de", from_lang="en")
            ResponseOutput = translator.translate(ResponseOutput)

            print(f"Carter's response: {ResponseOutput}")

            tts = gTTS(text=ResponseOutput, lang='de')
            tts.save('response.mp3')


            while vc.is_playing():
                await asyncio.sleep(0.1)


            vc.play(discord.FFmpegPCMAudio('response.mp3'))
            while vc.is_playing():
                await asyncio.sleep(0.1)

    elif UIName in sentence:
     SendToCarter(sentence, User, APIkey)
    with open('CarterResponse.txt') as f:
        ResponseOutput = f.read()

    print(message.content)
    translator = Translator(to_lang="de", from_lang="en")
    ResponseOutput = translator.translate(ResponseOutput)
    await message.channel.send(f"{ResponseOutput}")
    print(ResponseOutput)





def SendToCarter(sentence, User, APIkey):
    response = requests.post("https://api.carterlabs.ai/chat", headers={
        "Content-Type": "application/json"
    }, data=json.dumps({
        "text": f"{sentence}",
        "key": f"{APIkey}",
        "playerId": f"{User}"
    }))


    RawResponse = response.json()
    Response = RawResponse["output"]
    FullResponse = Response["text"]
    ResponseOutput = FullResponse
    with open("CarterResponse.txt", "w+") as f:
        f.write(f"{ResponseOutput}")

client.run(DiscordAPI)