import os
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import textwrap
import random
import json
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont

# --- CONFIGURAZIONE ---
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN")

# ✅ 1. BOT TELEGRAM
TELEGRAM_TOKEN = "8500964546:AAF_N69eNLxRNLn023At20cLrKspG378u2I"

# ✅ 2. ID CHAT TELEGRAM
# ⚠️ SOSTITUISCI "123456789" CON IL TUO ID VERO!
TELEGRAM_CHAT_ID = "1723292483"

PAGE_ID = "1479209002311050"

# ✅ 3. NUOVO LINK MAKE.COM (Aggiornato)
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/3eomacplemm46t3lila470oo1sykddx2"

CSV_FILE = "Frasichiesa.csv"
LOGO_PATH = "logo.png"
FONT_NAME = "arial.ttf" 

# --- 1. GESTIONE DATI ---
def get_random_verse():
    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty: return None
        return df.sample(1).iloc[0]
    except Exception as e:
        print(f"⚠️ Errore lettura CSV: {e}")
        return None

# --- 2. GENERATORE PROMPT ---
def get_image_prompt(categoria):
    cat = str(categoria).lower().strip()
    base_style = "bright, divine light, photorealistic, 8k, sun rays, cinematic"
    
    prompts_consolazione = [
        f"peaceful sunset over calm lake, warm golden light, {base_style}",
        f"gentle morning light through trees, forest path, {base_style}",
        f"hands holding light, soft warm background, {base_style}"
    ]
    prompts_esortazione = [
        f"majestic mountain peak, sunrise rays, dramatic sky, {base_style}",
        f"eagle flying in blue sky, sun flare, freedom, {base_style}",
        f"running water stream, clear river, energy, {base_style}"
    ]
    prompts_altro = [
        f"beautiful blue sky with white clouds, heaven light, {base_style}",
        f"field of flowers, spring, colorful, creation beauty, {base_style}"
    ]

    if "consolazione" in cat: return random.choice(prompts_consolazione)
    elif "esortazione" in cat: return random.choice(prompts_esortazione)
    else: return random.choice(prompts_altro)

# --- 3. AI & IMMAGINI ---
def get_ai_image(prompt_text):
    print(f"🎨 Generazione immagine: {prompt_text}")
    try:
        clean_prompt = prompt_text.replace(" ", "%20")
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1080&nologo=true"
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print(f"⚠️ Errore AI: {e}")
    return Image.new('RGBA', (1080, 1080), (50, 50, 70))

# --- 4. FUNZIONE CARICAMENTO FONT ---
def load_font(size):
    fonts_to_try = [FONT_NAME, "DejaVuSans-Bold.ttf", "arial.ttf"]
    for font_path in fonts_to_try:
        try:
            return ImageFont.truetype(font_path, size)
        except: continue
    return ImageFont.load_default()

# --- 5. CREAZIONE IMMAGINE ---
def create_verse_image(row):
    prompt = get_image_prompt(row['Categoria'])
    base_img = get_ai_image(prompt).resize((1080, 1080))
    
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    W, H = base_img.size
    
    font_txt = load_font(100)  
    font_ref = load_font(60)   

    text = f"“{row['Frase']}”"
    lines = textwrap.wrap(text, width=16) 
    
    line_height = 110
    text_block_height = len(lines) * line_height
    ref_height = 80
    total_content_height = text_block_height + ref_height
    
    start_y = ((H - total_content_height) / 2) - 150
    
    padding = 50
    box_left = 40
    box_top = start_y - padding
    box_right = W - 40
    box_bottom = start_y + total_content_height + padding
    
    draw.rectangle(
        [(box_left, box_top), (box_right, box_bottom)], 
        fill=(0, 0, 0, 140), 
        outline=None
    )
    
    final_img = Image.alpha_composite(base_img, overlay)
    draw_final = ImageDraw.Draw(final_img)
    
    current_y = start_y
    for line in lines:
        bbox = draw_final.textbbox((0, 0), line, font=font_txt)
        w = bbox[2] - bbox[0]
        draw_final.text(((W - w)/2, current_y), line, font=font_txt, fill="white")
        current_y += line_height
        
    ref = str(row['Riferimento'])
    bbox_ref = draw_final.textbbox((0, 0), ref, font=font_ref)
    w_ref = bbox_ref[2] - bbox_ref[0]
    draw_final.text(((W - w_ref)/2, current_y + 25), ref, font=font_ref, fill="#FFD700")

    return final_img

# --- 6. LOGO ---
def add_logo(img):
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            w = int(img.width * 0.20)
            h = int(w * (logo.height / logo.width))
            logo = logo.resize((w, h))
            img.paste(logo, ((img.width - w)//2, img.height - h - 30), logo)
        except: pass
    return img

# --- 7. MEDITAZIONE (STILE EVANGELICO PENTECOSTALE) ---
def genera_meditazione(row):
    cat = str(row['Categoria']).lower()
    
    # Intros più carismatiche
    intro = random.choice([
        "🔥 𝗣𝗮𝗿𝗼𝗹𝗮 𝗱𝗶 𝗩𝗶𝘁𝗮:", 
        "🕊️ 𝗚𝘂𝗶𝗱𝗮 𝗱𝗲𝗹𝗹𝗼 𝗦𝗽𝗶𝗿𝗶𝘁𝗼:", 
        "🙏 𝗣𝗲𝗿 𝗶𝗹 𝘁𝘂𝗼 𝗖𝘂𝗼𝗿𝗲:", 
        "🙌 𝗚𝗹𝗼𝗿𝗶𝗮 𝗮 𝗗𝗶𝗼:"
    ])
    
    msgs = []
    
    if "consolazione" in cat:
        msgs = [
            "Fratello, sorella, non temere! Lo Spirito Santo è il Consolatore e oggi asciuga ogni tua lacrima.",
            "Affida ogni peso a Gesù. Lui ha già portato le tue sofferenze sulla croce per darti pace.",
            "Anche se attraversi la valle oscura, non sei solo. Il Buon Pastore è con te e ti rialzerà.",
            "Dio non è mai in ritardo. Confida nei Suoi tempi perfetti e vedrai la Sua mano muoversi.",
            "La pace di Dio, che supera ogni intelligenza, custodisca oggi il tuo cuore in Cristo Gesù."
        ]
    elif "esortazione" in cat:
        msgs = [
            "Alzati nel nome di Gesù! Dichiara vittoria sulla tua situazione, il nemico è già sconfitto.",
            "Non mollare proprio ora. La tua benedizione è vicina. Prega con potenza e vedrai le mura crollare!",
            "Spezza ogni catena di paura. Hai l'autorità di Cristo in te per camminare sopra le acque.",
            "Sii forte e coraggioso. Non guardare alle circostanze, ma guarda alla grandezza del tuo Dio!",
            "La fede sposta le montagne. Oggi, ordina alla tua montagna di spostarsi nel nome di Gesù."
        ]
    elif "edificazione" in cat or "fede" in cat:
        msgs = [
            "Resta saldo sulla Roccia che è Cristo. Nessuna tempesta potrà smuovere chi confida in Lui.",
            "Nutri il tuo spirito con la Parola oggi. La fede viene dall'udire la Parola di Dio. Alleluia!",
            "Sii luce in mezzo alle tenebre. Che gli altri vedano Gesù brillare attraverso la tua vita.",
            "Non vivere per visione, ma cammina per fede. Dio sta preparando cose grandiosi per te.",
            "Cresci nella grazia e nella conoscenza del Signore. Lui ha un piano meraviglioso per la tua vita."
        ]
    else: # Generico / Altro
        msgs = [
            "Metti Dio al primo posto e Lui si prenderà cura di tutto il resto. Amen!",
            "Prega senza stancarti. La preghiera del giusto ha una grande efficacia nel mondo spirituale.",
            "Oggi, scegli di benedire e non di mormorare. Dio onora chi ha un cuore grato.",
            "Lascia che lo Spirito Santo ti guidi in ogni decisione. Lui sa cosa è meglio per te.",
            "Ricorda: se Dio è per noi, chi sarà contro di noi? Vai avanti con fiducia!"
        ]

    msg_scelto = random.choice(msgs)
    return f"{intro}\n{msg_scelto}"

# --- 8. SOCIAL & WEBHOOK ---
def send_telegram(img_bytes, caption):
    if not TELEGRAM_TOKEN: 
        print("❌ Telegram Token Mancante")
        return
    
    if TELEGRAM_CHAT_ID == "123456789":
        print("⚠️ ATTENZIONE: ID Telegram non configurato correttamente!")

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        files = {'photo': ('img.png', img_bytes, 'image/png')}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
        response = requests.post(url, files=files, data=data)
        print(f"✅ Telegram Risposta: {response.status_code}")
    except Exception as e: print(f"❌ Telegram Error: {e}")

def post_facebook(img_bytes, message):
    if not FACEBOOK_TOKEN: return
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos?access_token={FACEBOOK_TOKEN}"
    files = {'file': ('img.png', img_bytes, 'image/png')}
    data = {'message': message, 'published': 'true'}
    try:
        requests.post(url, files=files, data=data)
        print("✅ Facebook OK")
    except Exception as e: print(f"❌ Facebook Error: {e}")

def trigger_make_webhook(row, img_bytes, meditazione_text):
    """Invia dati E immagine a Make.com"""
    print(f"📡 Inviando a Make.com: {MAKE_WEBHOOK_URL}")
    
    data_payload = {
        "categoria": row.get('Categoria', 'N/A'),
        "riferimento": row.get('Riferimento', 'N/A'),
        "frase": row.get('Frase', 'N/A'),
        "meditazione": meditazione_text,
        "evento": "Post Chiesa Pubblicato",
        "origine": "Script Python - Chiesa"
    }

    files_payload = {
        'upload_file': ('post_chiesa.png', img_bytes, 'image/png')
    }

    try:
        response = requests.post(
            MAKE_WEBHOOK_URL, 
            data=data_payload,
            files=files_payload
        )
        if response.status_code == 200:
            print("✅ Webhook Make attivato con immagine!")
        else:
            print(f"❌ Errore Webhook Make: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Errore connessione Make: {e}")

# --- MAIN ---
if __name__ == "__main__":
    row = get_random_verse()
    if row is not None:
        print(f"📖 Versetto: {row['Riferimento']}")
        img = add_logo(create_verse_image(row))
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        img_data = buf.getvalue()
        
        meditazione = genera_meditazione(row)
        caption = (
            f"✨ {str(row['Categoria']).upper()} ✨\n\n"
            f"“{row['Frase']}”\n"
            f"📖 {row['Riferimento']}\n\n"
            f"────────────────\n"
            f"{meditazione}\n"
            f"────────────────\n\n"
            f"📍 Chiesa L'Eterno Nostra Giustizia\n\n"
            f"#fede #vangelodelgiorno #chiesa #gesù #preghiera #bibbia #paroladidio #pentecostale"
        )
        
        # 1. Telegram
        send_telegram(img_data, caption)
        
        # 2. Facebook
        post_facebook(img_data, caption)
        
        # 3. Make.com
        trigger_make_webhook(row, img_data, meditazione)
        
    else:
        print("❌ Nessun contenuto nel CSV.")
        
