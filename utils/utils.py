import requests



def get_news(params,api_key):
   
    base_url="https://newsapi.org/v2/top-headlines"
    
    params['apiKey']=api_key
    response=requests.get(base_url,params=params)
    
    if response.status_code==200:
        
        data=response.json()
        
        articles=data['articles']
        news_report=[]
        
        for article in articles:
            title=article['title']
            
            description=article.get('description','No description found')
            
            news_report.append(f"Title:{title}. Description: {description}")
            
        return news_report
    else:
        
        return ["Sorry, I couldn't retrieve the new information."]


def get_weather(result,api_key):
    
    location=result['parameters'].get('location','')
    
    time=result['parameters'].get('time','')
    
    
    base_url="http://api.weatherapi.com/v1/current.json"
    params={
        'key':api_key,
        'q':location,
        'lang':'en'
    }
    response=requests.get(base_url,params=params)
    
    if response.status_code==200:
        data=response.json()
        
        return format_weather_response(data)
    else:
        
        return "sorry, I couldn't retrieve the weather information."
    


def format_weather_response(weather_data):
    
    location = weather_data['location']
    current = weather_data['current']
    
    location_name = location['name']
    current_temp = current['temp_c']
    current_condition = current['condition']['text']
    feels_like = current['feelslike_c']
    wind_speed = current['wind_kph']
    humidity = current['humidity']
    time_str=location['localtime']
    
    # Parse time string into hour and minute
    hour = int(time_str.split()[1].split(':')[0])
    
    # Determine the greeting based on the hour
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    response = (f"""{greeting}! In {location_name}, it's currently {current_temp} degrees Celsius with {current_condition}. "
                Feels like {feels_like} degreesThe wind is showing off at 
                {wind_speed} kilometers per hour, and the humidity is a sticky {humidity} percent.
                Enjoy your {greeting.split()[1]}""")
    
    return response