from chatGPT import OpenAIWrapper
import os
import subprocess
import json
from flet import *
import threading
from fastapi import FastAPI, WebSocket
import asyncio

## Gerando  o vídeo
suno_prompts = ["lofi chill beats"]
video_urls= ["https://static.videezy.com/system/resources/previews/000/012/466/original/LA_01_-_4K_res.mp4", "https://atlasborn.github.io/lofi-media-manager/videos/Lofi-Preview.mp4"]
duration = int(2)
instrumental = [True, False]
n_musics = 2
sfx_url = ["https://atlasborn.github.io/lofi-media-manager/audios/rain-base.MP3"]
thumbnail_url = ["https://atlasborn.github.io/lofi-media-manager/thumbnails/lofi-thumbnail01.jpg"]

paths = {
            'prompt_metadata':r"C:\codes\pythonprojects\Isis\lofi-video-poster\app\prompts\gerar-titulo.txt",
            
            }

##Publicando no Youtube
my_channel = ["Rainy"]
folder_id = {my_channel[0]: "1pXpi2W1obahQFANj62Rn-7-YmHMPEDlS"}
desc_prompts = [
    "Crie um título para vídeo do youtube com SEO otimizado para o nicho de pessoas que ouvem músicas relaxantes para estudar, trabalhar ou dormir. Lofi Music.",
    r"C:\codes\pythonprojects\Isis\lofi-video-poster\app\prompts\gerar-titulo.txt"]
platforms = ["youtube", "spotify", "deezer"]
example_video_of_channel = ["cYPJaHT5f3E"]

def JsonReader(path):
    with open(path, 'r') as file:
        return file.read()

def getMetaData(prompt = desc_prompts[1], channel_video_id = example_video_of_channel[0], my_channel = my_channel[0]):
    api_key = os.environ.get('OPENAI_KEY')
    prompt_metadata = JsonReader(prompt)
    keys = ['title','description','tags','keywords']
    
    openai = OpenAIWrapper(api_key=api_key)
    metadata_json = openai.Completion(prompt_metadata, keys=keys)
    openai.Write(file_name='response', data=metadata_json, extension='json')
    
    title = metadata_json.get('title')
    description = metadata_json.get('description')
    tags = metadata_json.get('tags')
    return title, description, tags

def VideoMetaData(video_path, thumbnail_path, path = 'media', privacity=0, category=10, prompt = desc_prompts[0], channel_video_id = example_video_of_channel[0], my_channel = my_channel[0]):
        title, description, tags = getMetaData(prompt = prompt, channel_video_id = channel_video_id, my_channel = my_channel)
        privacy = ['unlisted', 'private', 'public']
        try:
            privacy_status = privacy[privacity]
        except:
            privacy_status = privacy[0]
        json_ = {
            'video_path': video_path,
            'thumbnail_path': thumbnail_path,
            'title': title,
            'description': description,
            'tags':tags,
            'category': category,
            'privacity': privacy_status
        }
        
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, 'response.json'), 'w') as js:
            json.dump(json_, js, indent=4)
            print(js.name)
            return js.name

fastapi = FastAPI()

@fastapi.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    def consent_url(value):
        text_consent_url.value = f"URL: {value}"
        text_consent_url.page.update()
    
    def progress_bar(value):
        bar_upload_progress.value = round(float(value),2)
        bar_upload_progress.page.update()
    
    actions = {"url": consent_url, "progress": progress_bar}
    while True:
        try:
            message = await websocket.receive_text()
            data = json.loads(message)
            actions[data["type"]](data['data'])
        
        except Exception as e:
            print(f"Error in websocket:\n\n{e}")
    
upload_process = None
bar_upload_progress = ProgressBar(value = 0)
text_consent_url = Text(" ")

def flet_main(page: Page):

        
    def metadata(e):
        #video_path = "/workspaces/lofi-video-poster/video/output_final.mp4" # Teste para caso tudo dê errado
        try:
            if colunm_metadata:
                page.remove(colunm_metadata)
        except:
            pass
        response = VideoMetaData(video_path=textField_video_path.value,thumbnail_path=textField_thumbnail_path.value, privacity=0,prompt = desc_prompts[1], channel_video_id = example_video_of_channel[0], my_channel = my_channel[0])
        text_videoData = Text(
        value= JsonReader('media/response.json')
        )
        
        if response:
            button_upload.disabled = False
            colunm_metadata = Column([text_videoData, Divider(), button_upload], scroll="always", expand=True)
            page.add(colunm_metadata)
            page.update()
    
    def upload(e):
        global upload_process
        def run_upload():
            global upload_process
            page.clean() #Limpa tela
            text_title = Text("Upload Page")
            upload_page = Column([text_title, bar_upload_progress , Divider(), button_cancel_upload], scroll="always", expand=True)
            page.add(upload_page)
            page.update()            
            upload_process = subprocess.Popen(["node", "upload.js"])
            upload_process.wait()
            page.clean()
            page.update()
            page.overlay.append(SnackBar(content=Text("Upload Complete"), open=True))
            page.update()
            page.add(inputs)
            page.update()
        
        upload_thread = threading.Thread(target=run_upload)
        upload_thread.start()
            
    def cancel_upload(e):
        global upload_process
        
        if upload_process:
            upload_process.terminate()
            page.overlay.append(SnackBar(content=Text("Upload Complete"), open=True))
            page.update()
            page.clean()
            page.add(inputs)
            page.update()
                    

    def on_text_change(e):
        if textField_video_path.value and textField_thumbnail_path.value:
            button_gen_metadata.disabled = False
        page.update()
    
    textField_video_path = TextField(
        label="Video Path",
        multiline=False,
        on_change= on_text_change
    )
    
    textField_thumbnail_path = TextField(
        label="Thumb Path",
        multiline=False,
        on_change= on_text_change
    )
    
    button_gen_metadata = Button(
        text= "Generate Metadata",
        on_click= metadata,
        disabled= True,
    )
    
    button_upload = Button(
        text= "Upload to Youtube",
        on_click= upload,
    )
    
    button_cancel_upload = Button(
        text='Cancel', 
        on_click=cancel_upload
        )
    
    
    inputs = Column(
        [textField_video_path, textField_thumbnail_path, button_gen_metadata, Divider()],
    )
    
    page.add(inputs)
    
    page.update()
    
if __name__ =='__main__':
    from multiprocessing import Process
    import uvicorn
    
    flet_process = Process(target=app, args=(flet_main,))
    flet_process.start()
    uvicorn.run(fastapi, host='0.0.0.0',port=8000)
