from flask import Flask, Response
import requests
import json
import re

app = Flask(__name__)

# Rota curinga (Pega tanto /gm quanto /chall ou a raiz /)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    # LÓGICA:
    # Se na URL tiver "chall", buscamos Challenger.
    # Caso contrário (ou se for vazio), buscamos Grão-Mestre.
    target_tier = "challenger" if "chall" in path else "grandmaster"
    
    try:
        # --- LÓGICA OP.GG ---
        # Challenger = Top 300 (Página 3)
        # Grão-Mestre = Top 1000 (Página 10)
        page = 3 if target_tier == "challenger" else 10
        url = f"https://www.op.gg/leaderboards/tier?region=kr&page={page}"
        
        # Headers para fingir ser um navegador comum e não ser bloqueado
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        # Timeout de 5s
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code != 200:
            return Response(f"Erro: OP.GG retornou código {resp.status_code}", mimetype='text/plain')

        # --- ESTRATÉGIA DE EXTRAÇÃO (SEM BEAUTIFULSOUP) ---
        # Vamos usar Regex para achar o JSON "__NEXT_DATA__" dentro do HTML.
        # Isso economiza memória e evita erros de instalação do bs4.
        
        # Procura por: <script id="__NEXT_DATA__" type="application/json"> ...dados... </script>
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            
            # Navega no JSON do OP.GG:
            # props -> pageProps -> data (que é a lista de jogadores)
            try:
                players_list = data['props']['pageProps']['data']
                
                if not players_list:
                    return Response("Erro: Lista de jogadores vazia no OP.GG.", mimetype='text/plain')
                
                # O corte é o LP do ÚLTIMO jogador da página (Rank 300 ou 1000)
                last_player = players_list[-1]
                lp = last_player.get('league_points')
                
                if lp is not None:
                    return Response(f"{lp} LP", mimetype='text/plain')
                else:
                    return Response("Erro: Campo LP não encontrado no jogador.", mimetype='text/plain')

            except KeyError:
                return Response("Erro: Estrutura do JSON do OP.GG mudou.", mimetype='text/plain')
        
        else:
            return Response("Erro: JSON oculto não encontrado (Bloqueio de Bot?)", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro Tecnico: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run()