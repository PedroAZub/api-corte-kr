from flask import Flask, Response
import requests
import re
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    # Define o alvo
    tier = "challenger" if "chall" in path else "grandmaster"

    try:
        # URL do DeepLoL
        url = "https://www.deeplol.gg/ranking/KR/all"
        
        # User-Agent do Googlebot (Obrigatório)
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Referer": "https://www.google.com/"
        }

        # Timeout curto
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code != 200:
            return Response(f"Erro: DeepLoL off ({resp.status_code})", mimetype='text/plain')

        # ESTRATÉGIA LEVE (SEM BEAUTIFULSOUP)
        # Vamos procurar o JSON "tierCutoff" usando Regex direto no texto.
        
        # Procura por: "tierCutoff": { ... }
        match = re.search(r'"tierCutoff"\s*:\s*({.*?})', resp.text)
        
        if match:
            # Transforma o texto achado em JSON
            json_str = match.group(1)
            data = json.loads(json_str)
            
            # Pega o valor
            val = data.get(tier) or data.get(tier.upper())
            
            if val:
                return Response(f"{val} LP", mimetype='text/plain')
        
        return Response("Erro: Corte nao encontrado no site.", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro Tecnico: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run()