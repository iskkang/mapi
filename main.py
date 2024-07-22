from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import logging
from bs4 import BeautifulSoup

app = FastAPI()
# CORS 설정
origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://mtlab.netlify.app/",
    "https://mtlab.netlify.app/scfi" # 여기에 실제 배포 URL을 추가하세요
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)

@app.get("/scfi")
async def fetch_and_plot_scfi():
    url = "https://www.econdb.com/widgets/shanghai-containerized-index/data/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        series_data = data['plots'][0]['data']
        df = pd.DataFrame(series_data)
        df['Date'] = pd.to_datetime(df['Date'])
        fig = go.Figure()
        for column in df.columns:
            if column != 'Date':
                fig.add_trace(go.Scatter(x=df['Date'], y=df[column], mode='lines+markers', name=column))
        return fig.to_dict()
    else:
        return {"error": "Failed to retrieve SCFI data"}

@app.get("/ports")
async def fetch_and_plot_ports():
    url = "https://www.econdb.com/widgets/top-port-comparison/data/"
    response = requests.get(url)
    if response.status_code == 200 {
        data = response.json()
        series_data = data['plots'][0]['data']
        df = pd.DataFrame(series_data)
        fig = px.bar(df, x='name', y='value', title="Top Port Comparison (June 24 vs June 23)")
        return fig.to_dict()
    } else {
        return {"error": "Failed to retrieve port comparison data"}
    }

@app.get("/global_trade")
async def fetch_and_plot_global_trade():
    url = "https://www.econdb.com/widgets/global-trade/data/?type=export&net=0&transform=0"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        series_data = data['plots'][0]['data']
        df = pd.DataFrame(series_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        fig = px.bar(df, x=df.index, y=df.columns, title="Global exports (TEU by week)", labels={'x': 'Year', 'value': 'TEU'}, barmode='stack')
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=52))
        return fig.to_dict()
    } else {
        return {"error": "Failed to retrieve global trade data"}
    }

@app.get("/news")
async def fetch_news(category: str):
    url = f"https://news.google.com/search?q={category}&hl=ko&gl=KR&ceid=KR:ko"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')

    news = []
    for article in articles:
        source = article.find('div', class_='vr1PYe').text if article.find('div', class_='vr1PYe') else 'No Source'
        title_tag = article.find('a', class_='JtKRv')
        title = title_tag.text if title_tag else 'No Title'
        link = 'https://news.google.com' + title_tag['href'][1:] if title_tag else 'No Link'
        thumbnail_tag = article.find('img', class_='Quavad')
        if thumbnail_tag:
            thumbnail = thumbnail_tag['src']
            if thumbnail.startswith('/'):
                thumbnail = 'https://news.google.com' + thumbnail
        else:
            thumbnail = None
        date_tag = article.find('time', class_='hvbAAd')
        date = date_tag['datetime'] if date_tag else None
        news.append({
            'source': source,
            'title': title,
            'link': link,
            'thumbnail': thumbnail,
            'date': date
        })

    return news
