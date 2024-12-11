from chatGPT import OpenAIWrapper
import os
import subprocess
import json
from flet import *
import threading

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
        
upload_process = None

def main(page: Page):
    def metadata(e):
        loading = ProgressBar()
        page.add(loading)
        button_gen_metadata.disabled = True
        try:
            if colunm_metadata:
                page.remove(colunm_metadata)
        except:
            pass
        response = VideoMetaData(video_path=textField_video_path.value, thumbnail_path=textField_thumbnail_path.value, privacity=0, prompt=desc_prompts[1], channel_video_id=example_video_of_channel[0], my_channel=my_channel[0])
        text_videoData = Text(value=JsonReader('media/response.json'))

        if response:
            page.remove(loading)
            button_gen_metadata.disabled = False
            button_upload.disabled = False
            colunm_metadata = Column([text_videoData, Divider(), button_upload], scroll="always", expand=True)
            page.add(colunm_metadata)
            page.update()

    def upload(e):
        global upload_process
        def run_upload():
            global upload_process
            page.clean()
            text_title = Text("Upload Page")
            upload_page = Column([text_title, ProgressRing(), Divider(), button_cancel_upload], scroll="always", expand=True)
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
            page.overlay.append(SnackBar(content=Text("Upload Cancelled"), open=True))
            page.update()
            page.clean()
            page.add(inputs)
            page.update()

    def on_text_change(e):
        if textField_video_path.value and textField_thumbnail_path.value:
            button_gen_metadata.disabled = False
        page.update()

    def pick_video(e):
        allower_extensions = ['mp4','avi','mpeg','webm','gif']
        file_picker_video.pick_files(allow_multiple=False, allowed_extensions=allower_extensions)

    def pick_thumbnail(e):
        allower_extensions = ['jpg','png','jpeg','webp']
        file_picker_thumbnail.pick_files(allow_multiple=False, allowed_extensions=allower_extensions)
    
    def on_video_picked(e):
        if file_picker_video.result:
            textField_video_path.value = file_picker_video.result.files[0].path
            textField_video_path.page.update()
            on_text_change(e)

    def on_thumbnail_picked(e):
        if file_picker_thumbnail.result:
            textField_thumbnail_path.value = file_picker_thumbnail.result.files[0].path
            textField_thumbnail_path.page.update()
            on_text_change(e)
           

    textField_video_path = Text(
        value=None,
    )

    textField_thumbnail_path = Text(
        value=None,
    )

    button_gen_metadata = Button(
        text="Generate Metadata",
        on_click=metadata,
        disabled=True,
        icon=Icons.AUTORENEW
    )

    button_upload = Button(
        text="Upload to Youtube",
        on_click=upload,
        icon=Icons.UPLOAD_FILE
    )

    button_cancel_upload = Button(
        text='Cancel',
        on_click=cancel_upload,
        icon=Icons.CANCEL
    )

    file_picker_video = FilePicker(on_result=on_video_picked)
    file_picker_thumbnail = FilePicker(on_result=on_thumbnail_picked)

    pick_video_button = Button(
        text="Select Video",
        icon=Icons.VIDEO_FILE,
        on_click=pick_video
    )

    pick_thumbnail_button = Button(
        text="Select Thumbnail",
        icon=Icons.IMAGE,
        on_click=pick_thumbnail
    )

    inputs = Column(
        [pick_video_button, textField_video_path, pick_thumbnail_button, textField_thumbnail_path, button_gen_metadata, Divider()],
    )

    page.overlay.append(file_picker_video)
    page.overlay.append(file_picker_thumbnail)
    page.add(inputs)

    page.update()

if __name__ == '__main__':
    app(target=main, port=8000)

