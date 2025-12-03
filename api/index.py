from flask import Flask, Response
import json
import re
# Usamos a biblioteca nativa do Python em vez de requests
# Isso evita erros de instalação na Vercel
import urllib.request 

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    tier = "challenger" if "chall" in path else "grandmaster"
    
    try:
        # URL do DeepLoL (Onde tem o cabeçalho da sua imagem)
        url = "https://www.deeplol.gg/ranking/KR/all"
        
        # Headers para fingir ser Googlebot
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        }

        # Requisição NATIVA (Sem biblioteca requests)
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            # Lê o site e decodifica o texto
            html_bytes = response.read()
            html_text = html_bytes.decode('utf-8')
            
            # --- ESTRATÉGIA DE BUSCA ---
            # Procura o JSON "tierCutoff" direto no texto usando Regex.
            # O DeepLoL escreve: "tierCutoff":{"grandmaster":803,"challenger":1140}
            
            # Procura por: "tierCutoff":{...}
            match = re.search(r'"tierCutoff"\s*:\s*({[^}]+})', html_text)
            
            if match:
                # Converte o texto achado para JSON
                cutoff_data = json.loads(match.group(1))
                
                # Tenta pegar grandmaster ou GRANDMASTER
                val = cutoff_data.get(tier) or cutoff_data.get(tier.upper())
                
                if val:
                    return Response(f"{val} LP", mimetype='text/plain')
            
            # Backup: Procura texto bruto "grandmaster":803
            match_brute = re.search(rf'"{tier}"\s*:\s*(\d+)', html_text, re.IGNORECASE)
            if match_brute:
                return Response(f"{match_brute.group(1)} LP", mimetype='text/plain')

            return Response("Erro: Valor não encontrado no código do site.", mimetype='text/plain')

    except Exception as e:
        # Se der erro, mostra na tela em vez de dar Erro 500
        return Response(f"Erro Tecnico: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run()