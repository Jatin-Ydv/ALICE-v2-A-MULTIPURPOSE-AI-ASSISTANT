from groq import Groq
from PIL import ImageGrab, Image
import cv2
from faster_whisper import WhisperModel
from openai import OpenAI
import speech_recognition as sr
import pyperclip
import google.generativeai as genai
import pyaudio
import os
import time
import re
import requests
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import os
import json
import pyttsx3
from datetime import datetime
from dotenv import load_dotenv
from utils.utils import get_news , get_weather
from utils.calls import extract_news_param, function_call


#load variables from .env
load_dotenv()


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


wake_word='Alice'


web_cam=cv2.VideoCapture(0)

groq_client=Groq(api_key=os.getenv('GROQ_API_KEY'))
genai.configure(api_key=os.getenv('GENAI_API_KEY'))
openai_client=OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
weather_api=os.getenv('WEATHER_API_KEY')
news_api=os.getenv('NEWS_API_KEY')


num_cores=os.cpu_count()
whisper_size='base'
whisper_model=WhisperModel(
    whisper_size,
    device='cpu',
    compute_type='int8',
    cpu_threads=num_cores//2,
    num_workers=num_cores//2
)

r=sr.Recognizer()
source=sr.Microphone()

sys_msg=("""
         You are a multi-modal AI voice assistant. Your user may or may not have attached a photo for context
         (either a screeshot or webcam capture). Any photo has already been processed into a highly detailed
         text prompt that will be attached to their transcribed voice prompt. Generate the most useful and
         factual response possible, carefully considering all previous generated text in your response before
         adding new tokens to the response. Do not expect or request images, just use the context if added.
         Use all of the context of this conversation so your response is relevant to the conversation. Make
         your response clear and concise, avoiding any verbosity.
         """)

convo=[{'role':'system','content':sys_msg}]

generation_config={
    'temperature':0.7,
    'top_p':1,
    'top_k':1,
    'max_output_tokens':2048
}

safety_settings=[
    {
        'category':'HARM_CATEGORY_HARASSMENT',
        'threshold':'BLOCK_NONE'
    },
    {
        'category':'HARM_CATEGORY_HATE_SPEECH',
        'threshold':'BLOCK_NONE'
    },
    {
        'category':'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold':'BLOCK_NONE'
    },
    {
        'category':'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold':'BLOCK_NONE'
    },
]

model=genai.GenerativeModel('gemini-1.5-flash-latest',
                            generation_config=generation_config,
                            safety_settings=safety_settings)

def groq_prompt(prompt,img_context):
    
    
    if img_context:
        prompt=f'USER PROMPT:{prompt}\n\n   IMAGE_CONTEXT: {img_context}'
    convo.append({'role':'user','content':prompt})
    chat_completion=groq_client.chat.completions.create(messages=convo,model='llama3-70b-8192')
    response=chat_completion.choices[0].message
    
    convo.append(response)
    return response.content




def fetch_news_params(prompt):
    return extract_news_param(prompt=prompt,groq_client=groq_client)




def take_screenshot():
    path='screenshot.jpg'
    screenshot=ImageGrab.grab()
    
    rgb_screenshot=screenshot.convert('RGB')
    rgb_screenshot.save(path,quality=15)




def web_cam_capture():
    if not web_cam.isOpened():
        print('ERROR : Camera did not open successfully')
        exit()
    
    path='webcam.jpg'
    ret,frame=web_cam.read()
    
    cv2.imwrite(path,frame)
    
def get_clipboard_text():
    clipboard_content=pyperclip.paste()
    if isinstance(clipboard_content,str):
        return clipboard_content
    
    else:
        print('No clipboard text to copy')
        return None




def fetch_weather(result,api_key=weather_api):
     
     return get_weather(result,api_key)




def fetch_news(params,api_key=news_api):
    return get_news(params,news_api)



        
def vision_prompt(prompt,photo_path):
    
    
    img =Image.open(photo_path)
    prompt=(
        """"
        You are the vision analysis AI that provides semantic meaning from images to provide context to send
        to another AI that will create a response to the user. Do not respond as the AI assistant to the user.
        Instead take the user prompt input and try to extract all meaning from the photo relevant to the user
        prompt. Then generate as much objectives data about the image for the AI
        """
    )
    response=model.generate_content([prompt,img])
    
    return response.text




def speak(text):

    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # List available voices
    
    voices = engine.getProperty('voices')
    
    # Set properties (optional)
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 150)    # Speed percent (can go over 100)
    engine.setProperty('volume', 1)    # Volume 0-1

    # Speak the text
    engine.say(text)
    engine.runAndWait()



# def speak2(text):
#     print('inside speak \n')
    
#     # Convert text to speech using gTTS
#     tts = gTTS(text=text, lang='en', slow=False)
    
#     # Save the audio to a bytes buffer
#     with io.BytesIO() as audio_buffer:
#         tts.write_to_fp(audio_buffer)
#         audio_buffer.seek(0)
        
#         # Load the audio with pydub
#         audio_segment = AudioSegment.from_file(audio_buffer, format="mp3")
        
#         # Play the audio
#         play(audio_segment)



# def speak(text):
    
#     print('inside speak \n')
    
#     player_stream=pyaudio.PyAudio().open(format=pyaudio.paInt16,channels=1,rate=24000,output=True)
#     stream_start=False
    
#     with openai_client.audio.speech.with_streaming_response.create(
#         model='tts-1',
#         voice='nova',
#         response_format='pcm',
#         input=text
#     ) as response:
#         silence_threshold=0.01
#         for chunk in response.iter_bytes(chunk_size=1024):
#             if stream_start:
#                 player_stream.write(chunk)
                
#             else:
#                 if max(chunk)>silence_threshold:
#                     player_stream.write(chunk)
#                     stream_start=True



def wav_to_text(audio_path):
    
    segments,_=whisper_model.transcribe(audio_path)
    text=''.join(segment.text for segment in segments)
    return text


def callback(recognizer,audio):
    
    
    prompt_audio_path='prompt.wav'
    with open(prompt_audio_path,'wb') as f:
        f.write(audio.get_wav_data())
        
    prompt_text=wav_to_text(prompt_audio_path)
    clean_prompt=extract_prompt(prompt_text,wake_word)
    
    if clean_prompt:
        print(f'USER : {clean_prompt}')
        call=function_call(clean_prompt,groq_client)
        call2=call
        call=call['function']
        if 'take screenshot' in call:
            print('Taking screenshot ...')
            take_screenshot()
            visual_context=vision_prompt(prompt=clean_prompt,photo_path='screenshot.jpg')
            prompt=clean_prompt
            
        elif 'capture webcam' in call:
            print('Capturing webcam ...')
            web_cam_capture()
            visual_context=vision_prompt(prompt=clean_prompt,photo_path='webcam.jpg')
            prompt=clean_prompt
            
        elif 'extract clipboard' in call:
            print('Copying clipboard text ...')
            paste=get_clipboard_text()
            prompt=f'{clean_prompt}\n\n CLIPBOARD CONTENT :{paste}'
            visual_context=None
            
        elif 'check weather' in call:
            print('Analysing Weather ...')
            weather=fetch_weather(result=call2)
           
            prompt=f'{clean_prompt} \n\n WEATHER STATUS: {weather}'
            visual_context=None
        
        elif 'check news' in call:
            print('Checking news ...')
            para=fetch_news_params(prompt=clean_prompt)
            
            news=fetch_news(para['parameters'])
            prompt=f'{clean_prompt} \n\n LATEST NEWS : {news}'
            visual_context=None
        else:
            prompt=clean_prompt
            visual_context=None
        
        
        response=groq_prompt(prompt=prompt,img_context=visual_context)
        print(f'{wake_word.upper()} : {response}')
        speak(response)

def start_listening():
    
    print('Starting the bot ... \n')
    
    with source as s:
        r.adjust_for_ambient_noise(s,duration=2)
        
    print('\n Say', wake_word, 'followed with your prompt. \n')
    r.listen_in_background(source,callback)
    
    
    while True:
        time.sleep(0.5)


def extract_prompt(transcribed_text,wake_word):
    
    pattern=rf'\b{re.escape(wake_word)}[\s,.?!]*([A-Za-z0-9].*)'
    match=re.search(pattern,transcribed_text,re.IGNORECASE)
    
    if match:
        prompt=match.group(1).strip()
        return prompt
    
    else:
        print('none extracted\n')
        return None
                   


start_listening()