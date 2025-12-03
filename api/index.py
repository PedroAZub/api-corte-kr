from flask import Flask, Response
import requests
import json
import re

app = Flask(__name__)

# Rota curinga (aceita qualquer link)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    # Se na URL tiver "chall", busca Challenger. Senão, busca GM.
    tier = "challenger" if "chall" in path else "grandmaster"
    
    try:
        # Lógica OP.GG:
        # Challenger = Rank 300 (Página 3)
        # Grão-Mestre = Rank 1000 (Página 10)
        page = 3 if tier == "challenger" else 10
        url = f"https://www.op.gg/leaderboards/tier?region=kr&page={page}"
        
        # Headers para não ser bloqueado
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Timeout curto
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code != 200:
            return Response(f"Erro: OP.GG retornou {resp.status_code}", mimetype='text/plain')

        # BUSCA INTELIGENTE (SEM BEAUTIFULSOUP)
        # Procura o JSON escondido no HTML usando Regex (mais leve e rápido)
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        
        if match:
            # Carrega os dados
            data = json.loads(match.group(1))
            
            # Navega até a lista de jogadores: props -> pageProps -> data
            try:
                players = data['props']['pageProps']['data']
                
                if not players:
                    return Response("Erro: Lista vazia no OP.GG.", mimetype='text/plain')
                
                # O corte é o LP do ÚLTIMO jogador da lista
                last_player = players[-1]
                lp = last_player.get('league_points')
                
                if lp is not None:
                    return Response(f"{lp} LP", mimetype='text/plain')
                    
            except KeyError:
                return Response("Erro: O OP.GG mudou a estrutura do site.", mimetype='text/plain')
        
        return Response("Erro: Dados do OP.GG não encontrados (Bloqueio?)", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro Tecnico: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run()