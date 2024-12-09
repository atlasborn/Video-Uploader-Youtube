from openai import OpenAI
import os
import json
#os.environ.get('OPENAI_KEY')
class OpenAIWrapper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def Completion(self,prompt, keys=[], language = 'inglês'):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"responda na linguagem {language}"},
                {"role": "system", "content": f"Response with Json, with keys {[k for k in keys]}"},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
        )
        return json.loads(response.choices[0].message.content.replace('```json\n','').replace('```','').strip())
    
    
    def FormatOutput(self, output):
        list_ = []
        for item in output:
            # Remove o prefixo 'json\n' e converte o JSON para objeto Python
            try:
                # Identifica e extrai o JSON, removendo qualquer parte desnecessária
                # json_part = item.replace('json\n', '').strip()
                # Converte para objeto Python
                item = item
                parsed_json = json.loads(item.strip())
                # Se for uma lista, estende; se for um dicionário, adiciona
                if isinstance(parsed_json, list):
                    list_.extend(parsed_json)
                elif isinstance(parsed_json, dict):
                    list_.append(parsed_json)
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar o JSON: {e}")

        # Converte tudo para um único JSON
        final_json = json.dumps(list_, indent=4, ensure_ascii=False)
        return json.loads(final_json)
    
    def Write(self,file_name, data, extension='json'):
        with open(f'{file_name}.{extension}', 'w') as file:
            file.write(json.dumps(data))

# def app():
#     api_key = os.environ.get('OPENAI_KEY')
#     prompt_metadata = fm.JsonReader(r"C:\codes\pythonprojects\Isis\lofi-video-poster\app\prompts\gerar-titulo.txt")
    
#     keys = ['title','description','tags','keywords']
#     openai = OpenAIWrapper(api_key=api_key)
#     metadata_json = openai.Completion(prompt_metadata, keys=keys)
#     openai.Write(file_name='response', data=metadata_json, extension='json')
#     print(metadata_json.get('title'))
#     #print(openai.FormatOutput(metadata_json))
    

# if __name__ == "__main__":
#     app()