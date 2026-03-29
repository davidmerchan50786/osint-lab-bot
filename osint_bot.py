#!/usr/bin/env python3
"""
OSINT Lab Bot - Red Team Training
Author: David Merchán
Email: david.merchan.50786@ikasle.egibide.org
GitHub: github.com/davidmerchanaltsasu

⚠️ DISCLAIMER: Solo para uso educativo con consentimiento explícito
"""

import sqlite3
import json
import hashlib
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
import re
from collections import Counter
import time

# ⚠️ CONFIGURACIÓN
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("La variable de entorno BOT_TOKEN no está definida. Configúrala antes de iniciar el bot.")
_admin_env = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_env.split(",") if x.strip()]

# Base de datos
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'osint_lab.db')

class OSINTBot:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos"""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabla de usuarios participantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT,
                consent_given BOOLEAN DEFAULT 0,
                points INTEGER DEFAULT 0,
                osint_scans INTEGER DEFAULT 0,
                phishing_caught INTEGER DEFAULT 0,
                phishing_failed INTEGER DEFAULT 0,
                ctf_flags_found INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de actividad/logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TEXT,
                message_text TEXT,
                message_type TEXT,
                chat_id INTEGER
            )
        ''')
        
        # Tabla de OSINT scans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS osint_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanner_id INTEGER,
                target_id INTEGER,
                scan_type TEXT,
                findings TEXT,
                timestamp TEXT
            )
        ''')
        
        # Tabla de phishing tests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phishing_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE,
                creator_id INTEGER,
                active BOOLEAN DEFAULT 1,
                clicks INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # Tabla de CTF flags
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ctf_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag_id TEXT UNIQUE,
                flag_value TEXT,
                points INTEGER,
                description TEXT,
                found_by INTEGER,
                found_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[+] Base de datos inicializada")
    
    def log_activity(self, user_id, message_text, message_type, chat_id):
        """Registrar actividad de usuario"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_log (user_id, timestamp, message_text, message_type, chat_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, datetime.now().isoformat(), message_text, message_type, chat_id))
        
        conn.commit()
        conn.close()
    
    def add_participant(self, user_id, username, full_name):
        """Añadir participante"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO participants (user_id, username, full_name, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, full_name, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def add_points(self, user_id, points):
        """Añadir puntos a usuario"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE participants SET points = points + ? WHERE user_id = ?
        ''', (points, user_id))
        
        conn.commit()
        conn.close()

bot_instance = OSINTBot()

# ==================== COMANDOS BÁSICOS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    
    bot_instance.add_participant(user.id, user.username, user.full_name)
    
    welcome_text = f"""
🔒 **OSINT LAB - Red Team Training Bot**

Bienvenido {user.mention_html()},

⚠️ **DISCLAIMER LEGAL:**
Este bot es para entrenamiento educativo en ciberseguridad.
Al usar este bot confirmas que:
- Participas voluntariamente
- Das consentimiento para análisis OSINT
- Entiendes que es un ejercicio educativo
- No usarás estas técnicas de forma maliciosa

📚 **Comandos disponibles:**

**OSINT Pasivo:**
/osint_scan - Escanear perfil de usuario
/reverse_image - Búsqueda inversa de imagen
/metadata - Extraer metadatos de imagen
/timeline @usuario - Ver actividad temporal
/correlate @user1 @user2 - Comparar usuarios

**Análisis:**
/patterns @usuario - Analizar patrones de escritura
/activity @usuario - Análisis de actividad
/common_groups @usuario - Grupos en común

**Phishing Tests:**
/phish_create - Crear test de phishing
/phish_stats - Ver estadísticas

**CTF (Capture The Flag):**
/ctf_status - Ver retos activos
/submit_flag <flag> - Enviar flag encontrada

**Estadísticas:**
/leaderboard - Ranking de puntos
/mystats - Tus estadísticas
/report @usuario - Generar reporte OSINT

**Admin:**
/give_consent @usuario - Dar consentimiento (admin)
/reset_points - Reiniciar puntos (admin)

Usa /help [comando] para más info
    """
    
    await update.message.reply_html(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    await update.message.reply_text(
        "📖 Usa /start para ver todos los comandos disponibles\n"
        "Para ayuda específica: /help [comando]"
    )

# ==================== OSINT PASIVO ====================

async def osint_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Escaneo OSINT de usuario"""
    if not context.args:
        await update.message.reply_text("Uso: /osint_scan @usuario")
        return
    
    username = context.args[0].replace('@', '')
    scanner_id = update.effective_user.id
    
    # Simular búsqueda (en producción usarías APIs reales)
    await update.message.reply_text(f"🔍 Escaneando información pública de @{username}...")
    
    findings = {
        'username': username,
        'scan_date': datetime.now().isoformat(),
        'found_in_groups': ['Este grupo'],  # Grupos en común
        'account_age': 'Desconocido',  # Telegram no expone esto directamente
        'profile_photos': 'Disponible',
        'bio': 'Accesible si es público',
        'last_seen': 'Disponible si no está oculto'
    }
    
    # Guardar scan
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO osint_scans (scanner_id, target_id, scan_type, findings, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (scanner_id, 0, 'profile_scan', json.dumps(findings), datetime.now().isoformat()))
    cursor.execute('UPDATE participants SET osint_scans = osint_scans + 1 WHERE user_id = ?', (scanner_id,))
    conn.commit()
    conn.close()
    
    # Dar puntos
    bot_instance.add_points(scanner_id, 10)
    
    report = f"""
📊 **Reporte OSINT - @{username}**

**Información Pública Encontrada:**
• Username: @{username}
• Grupos en común: {len(findings['found_in_groups'])}
• Fotos de perfil: Accesibles
• Última vez visto: Depende de configuración

**Metadatos:**
• Fecha del scan: {datetime.now().strftime('%Y-%m-%d %H:%M')}
• Escaneado por: {update.effective_user.mention_html()}

✅ +10 puntos por completar scan OSINT
    """
    
    await update.message.reply_html(report)

async def timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver timeline de actividad de usuario"""
    if not context.args:
        await update.message.reply_text("Uso: /timeline @usuario")
        return
    
    username = context.args[0].replace('@', '')
    scanner_id = update.effective_user.id
    
    # Consultar actividad del último mes
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    one_month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    cursor.execute('''
        SELECT timestamp, message_type, COUNT(*) as count
        FROM activity_log
        WHERE timestamp > ? AND user_id IN (
            SELECT user_id FROM participants WHERE username = ?
        )
        GROUP BY DATE(timestamp), message_type
        ORDER BY timestamp DESC
        LIMIT 20
    ''', (one_month_ago, username))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        await update.message.reply_text(f"No hay suficiente actividad registrada de @{username}")
        return
    
    timeline_text = f"📅 **Timeline de actividad - @{username}**\n\n"
    
    for row in results:
        timestamp, msg_type, count = row
        date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')
        timeline_text += f"• {date}: {count} mensajes ({msg_type})\n"
    
    bot_instance.add_points(scanner_id, 15)
    timeline_text += f"\n✅ +15 puntos por análisis temporal"
    
    await update.message.reply_html(timeline_text)

async def patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analizar patrones de escritura"""
    if not context.args:
        await update.message.reply_text("Uso: /patterns @usuario")
        return
    
    username = context.args[0].replace('@', '')
    scanner_id = update.effective_user.id
    
    # Analizar mensajes recientes
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT message_text FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        ORDER BY timestamp DESC LIMIT 100
    ''', (username,))
    
    messages = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not messages:
        await update.message.reply_text(f"No hay suficientes mensajes de @{username}")
        return
    
    # Análisis básico
    all_text = ' '.join(messages)
    words = re.findall(r'\w+', all_text.lower())
    word_freq = Counter(words).most_common(10)
    
    avg_length = sum(len(msg) for msg in messages) / len(messages)
    
    analysis = f"""
🔍 **Análisis de Patrones - @{username}**

**Estadísticas de escritura:**
• Mensajes analizados: {len(messages)}
• Longitud promedio: {avg_length:.1f} caracteres
• Palabras más usadas:
"""
    
    for word, count in word_freq[:5]:
        analysis += f"  - '{word}': {count} veces\n"
    
    bot_instance.add_points(scanner_id, 20)
    analysis += f"\n✅ +20 puntos por análisis de patrones"
    
    await update.message.reply_html(analysis)

# ==================== PHISHING SIMULADO ====================

async def phish_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crear test de phishing"""
    creator_id = update.effective_user.id
    
    # Generar ID único para el test
    test_id = hashlib.md5(f"{creator_id}{time.time()}".encode()).hexdigest()[:8]
    
    # Guardar test
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO phishing_tests (test_id, creator_id, created_at)
        VALUES (?, ?, ?)
    ''', (test_id, creator_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    # Crear mensaje de phishing simulado
    keyboard = [[InlineKeyboardButton("🎁 Reclamar Premio", callback_data=f"phish_{test_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎉 ¡FELICIDADES! Has ganado un premio especial.\n"
        "Haz click abajo para reclamarlo:",
        reply_markup=reply_markup
    )
    
    await update.message.reply_text(
        f"✅ Test de phishing creado (ID: {test_id})\n"
        f"Los clicks serán registrados para entrenamiento."
    )

async def phishing_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback cuando alguien cae en phishing"""
    query = update.callback_query
    await query.answer()
    
    test_id = query.data.replace('phish_', '')
    user_id = query.from_user.id
    
    # Registrar click
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE phishing_tests SET clicks = clicks + 1 WHERE test_id = ?', (test_id,))
    cursor.execute('UPDATE participants SET phishing_failed = phishing_failed + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    await query.edit_message_text(
        f"⚠️ **¡ADVERTENCIA!**\n\n"
        f"{query.from_user.mention_html()}, acabas de hacer click en un enlace de phishing simulado.\n\n"
        f"**Lección aprendida:**\n"
        f"• No hagas click en enlaces sospechosos\n"
        f"• Verifica siempre el remitente\n"
        f"• Si parece demasiado bueno, probablemente es falso\n\n"
        f"Este fue un ejercicio de entrenamiento. En un ataque real, "
        f"tu información podría haber sido comprometida.",
        parse_mode='HTML'
    )

async def phish_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estadísticas de phishing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(clicks) FROM phishing_tests')
    total_clicks = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM phishing_tests')
    total_tests = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT username, phishing_failed 
        FROM participants 
        WHERE phishing_failed > 0 
        ORDER BY phishing_failed DESC 
        LIMIT 5
    ''')
    
    top_vulnerable = cursor.fetchall()
    conn.close()
    
    stats_text = f"""
📊 **Estadísticas de Phishing Simulado**

**General:**
• Tests creados: {total_tests}
• Clicks totales: {total_clicks}
• Tasa de éxito: {(total_clicks/max(total_tests, 1)*100):.1f}%

**Top 5 más vulnerables:**
"""
    
    for username, fails in top_vulnerable:
        stats_text += f"• @{username}: {fails} clicks\n"
    
    await update.message.reply_html(stats_text)

# ==================== CTF ====================

async def ctf_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver retos CTF activos"""
    challenges = [
        {
            'id': 1,
            'name': 'Metadatos Ocultos',
            'description': 'Encuentra la información oculta en la imagen del perfil del bot',
            'points': 50,
            'flag_format': 'FLAG{...}'
        },
        {
            'id': 2,
            'name': 'Patrón Temporal',
            'description': 'Descubre el patrón oculto en los timestamps de mensajes',
            'points': 75,
            'flag_format': 'FLAG{...}'
        },
        {
            'id': 3,
            'name': 'Correlación de Usuarios',
            'description': 'Identifica los usuarios que son la misma persona',
            'points': 100,
            'flag_format': 'FLAG{...}'
        }
    ]
    
    ctf_text = "🚩 **Retos CTF Activos:**\n\n"
    
    for challenge in challenges:
        ctf_text += f"**#{challenge['id']} - {challenge['name']}** ({challenge['points']} pts)\n"
        ctf_text += f"📝 {challenge['description']}\n"
        ctf_text += f"🎯 Formato: {challenge['flag_format']}\n\n"
    
    ctf_text += "Usa /submit_flag <flag> para enviar tu respuesta"
    
    await update.message.reply_html(ctf_text)

async def submit_flag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enviar flag de CTF"""
    if not context.args:
        await update.message.reply_text("Uso: /submit_flag FLAG{...}")
        return
    
    flag = ' '.join(context.args)
    user_id = update.effective_user.id
    
    # Flags correctas (en producción estarían en BD)
    correct_flags = {
        'FLAG{EXIF_DATA_ROCKS}': 50,
        'FLAG{TEMPORAL_ANALYSIS}': 75,
        'FLAG{SAME_WRITING_STYLE}': 100
    }
    
    if flag in correct_flags:
        points = correct_flags[flag]
        
        # Verificar si ya fue encontrada
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT found_by FROM ctf_flags WHERE flag_value = ?', (flag,))
        already_found = cursor.fetchone()
        
        if already_found:
            await update.message.reply_text(f"⚠️ Esta flag ya fue encontrada por otro participante")
            conn.close()
            return
        
        # Registrar flag
        cursor.execute('''
            INSERT INTO ctf_flags (flag_id, flag_value, points, found_by, found_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (hashlib.md5(flag.encode()).hexdigest()[:8], flag, points, user_id, datetime.now().isoformat()))
        
        cursor.execute('UPDATE participants SET ctf_flags_found = ctf_flags_found + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        bot_instance.add_points(user_id, points)
        
        await update.message.reply_html(
            f"🎉 **¡CORRECTO!**\n\n"
            f"Flag válida: {flag}\n"
            f"✅ +{points} puntos\n\n"
            f"¡Sigue así!"
        )
    else:
        await update.message.reply_text(f"❌ Flag incorrecta. Sigue intentando!")

# ==================== ESTADÍSTICAS ====================

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ranking de puntos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, points, osint_scans, ctf_flags_found
        FROM participants
        ORDER BY points DESC
        LIMIT 10
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    leaderboard_text = "🏆 **Leaderboard - Top 10**\n\n"
    
    medals = ['🥇', '🥈', '🥉']
    
    for i, (username, points, scans, flags) in enumerate(results):
        medal = medals[i] if i < 3 else f"{i+1}."
        leaderboard_text += f"{medal} @{username}: {points} pts\n"
        leaderboard_text += f"   📊 {scans} scans | 🚩 {flags} flags\n"
    
    await update.message.reply_html(leaderboard_text)

async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estadísticas personales"""
    user_id = update.effective_user.id
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT points, osint_scans, phishing_caught, phishing_failed, ctf_flags_found
        FROM participants WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        await update.message.reply_text("Aún no tienes estadísticas. Usa /start para registrarte")
        return
    
    points, scans, caught, failed, flags = result
    
    stats_text = f"""
📊 **Tus Estadísticas**

**Puntos totales:** {points} pts

**OSINT:**
• Scans realizados: {scans}

**Phishing:**
• Tests superados: {caught}
• Tests fallidos: {failed}

**CTF:**
• Flags encontradas: {flags}

¡Sigue entrenando para mejorar!
    """
    
    await update.message.reply_html(stats_text)

# ==================== COMANDOS FALTANTES ====================

async def reverse_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Búsqueda inversa de imagen (simulada)"""
    if not context.args:
        await update.message.reply_text(
            "Uso: /reverse_image <url_imagen>\n"
            "Ejemplo: /reverse_image https://ejemplo.com/foto.jpg"
        )
        return

    url = context.args[0]
    scanner_id = update.effective_user.id

    await update.message.reply_text(f"🔎 Realizando búsqueda inversa de imagen: {url}")

    # Simulación de búsqueda inversa (en producción se usaría una API real)
    findings = {
        'url': url,
        'scan_date': datetime.now().isoformat(),
        'similar_images': 3,
        'possible_sources': ['Google Images', 'TinEye', 'Bing Visual Search'],
        'faces_detected': 1,
        'metadata_stripped': True,
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO osint_scans (scanner_id, target_id, scan_type, findings, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (scanner_id, 0, 'reverse_image', json.dumps(findings), datetime.now().isoformat()))
    conn.commit()
    conn.close()

    bot_instance.add_points(scanner_id, 10)

    report = f"""
🖼️ **Búsqueda Inversa de Imagen**

**URL analizada:** {url}

**Resultados (simulados):**
• Imágenes similares encontradas: {findings['similar_images']}
• Fuentes consultadas: {', '.join(findings['possible_sources'])}
• Rostros detectados: {findings['faces_detected']}
• Metadatos eliminados: {'Sí' if findings['metadata_stripped'] else 'No'}

**Fecha del análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

✅ +10 puntos por búsqueda inversa de imagen

⚠️ Nota: Esta es una simulación educativa. En producción se usarían APIs reales (Google Vision, TinEye, etc.)
    """

    await update.message.reply_html(report)


async def metadata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extraer metadatos de imagen (simulado)"""
    # Verificar si el mensaje tiene una foto adjunta o si se responde a una foto
    photo = None
    if update.message.photo:
        photo = update.message.photo[-1]
    elif update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]

    scanner_id = update.effective_user.id

    if photo:
        await update.message.reply_text("📎 Analizando metadatos de la imagen adjunta...")
        file_id = photo.file_id
        file_size = photo.file_size or 0

        findings = {
            'source': 'telegram_photo',
            'file_id': file_id,
            'file_size': file_size,
            'camera_make': 'Desconocido (Telegram elimina EXIF)',
            'camera_model': 'Desconocido',
            'gps_coords': 'Eliminado por Telegram',
            'date_taken': 'Desconocido',
            'software': 'Desconocido',
            'scan_date': datetime.now().isoformat(),
        }
        source_info = f"Foto de Telegram (tamaño: {file_size} bytes)"
    elif context.args:
        url = context.args[0]
        await update.message.reply_text(f"📎 Analizando metadatos de: {url}")

        findings = {
            'source': url,
            'camera_make': 'Canon',
            'camera_model': 'EOS 5D Mark IV',
            'gps_coords': '40.4168° N, 3.7038° W',
            'date_taken': '2024-03-15 14:32:00',
            'software': 'Adobe Photoshop 2024',
            'scan_date': datetime.now().isoformat(),
        }
        source_info = url
    else:
        await update.message.reply_text(
            "Uso:\n"
            "• /metadata <url_imagen> — analizar imagen por URL\n"
            "• Responde a una foto con /metadata — analizar foto del chat"
        )
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO osint_scans (scanner_id, target_id, scan_type, findings, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (scanner_id, 0, 'metadata', json.dumps(findings), datetime.now().isoformat()))
    conn.commit()
    conn.close()

    bot_instance.add_points(scanner_id, 15)

    report = f"""
📋 **Metadatos de Imagen**

**Fuente:** {source_info}

**EXIF Data:**
• Cámara: {findings['camera_make']} {findings['camera_model']}
• Fecha de captura: {findings['date_taken']}
• Software: {findings['software']}
• Coordenadas GPS: {findings['gps_coords']}

**Análisis:**
• Fecha del scan: {datetime.now().strftime('%Y-%m-%d %H:%M')}

✅ +15 puntos por extracción de metadatos

⚠️ Nota: Simulación educativa. Los metadatos EXIF pueden revelar ubicación y dispositivo del autor.
    """

    await update.message.reply_html(report)


async def correlate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Correlacionar y comparar dos usuarios"""
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /correlate @usuario1 @usuario2")
        return

    username1 = context.args[0].replace('@', '')
    username2 = context.args[1].replace('@', '')
    scanner_id = update.effective_user.id

    await update.message.reply_text(f"🔗 Correlacionando @{username1} y @{username2}...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener mensajes de ambos usuarios
    cursor.execute('''
        SELECT message_text FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        ORDER BY timestamp DESC LIMIT 100
    ''', (username1,))
    messages1 = [row[0] for row in cursor.fetchall() if row[0]]

    cursor.execute('''
        SELECT message_text FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        ORDER BY timestamp DESC LIMIT 100
    ''', (username2,))
    messages2 = [row[0] for row in cursor.fetchall() if row[0]]

    # Obtener actividad temporal de ambos
    cursor.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as cnt
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        GROUP BY hour ORDER BY cnt DESC LIMIT 3
    ''', (username1,))
    hours1 = cursor.fetchall()

    cursor.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as cnt
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        GROUP BY hour ORDER BY cnt DESC LIMIT 3
    ''', (username2,))
    hours2 = cursor.fetchall()

    conn.close()

    # Calcular similitud de vocabulario
    words1 = set(re.findall(r'\w+', ' '.join(messages1).lower())) if messages1 else set()
    words2 = set(re.findall(r'\w+', ' '.join(messages2).lower())) if messages2 else set()
    common_words = words1 & words2
    similarity = len(common_words) / max(len(words1 | words2), 1) * 100

    # Horas activas en común
    active_hours1 = {h for h, _ in hours1}
    active_hours2 = {h for h, _ in hours2}
    common_hours = active_hours1 & active_hours2

    bot_instance.add_points(scanner_id, 25)

    report = f"""
🔗 **Correlación de Usuarios**

**@{username1}** vs **@{username2}**

**Mensajes analizados:**
• @{username1}: {len(messages1)} mensajes
• @{username2}: {len(messages2)} mensajes

**Similitud de vocabulario:** {similarity:.1f}%
**Palabras en común:** {len(common_words)}

**Horas activas en común:** {', '.join(sorted(common_hours)) or 'No hay datos suficientes'}

**Posible correlación:** {'⚠️ Alta' if similarity > 30 else '✅ Baja' if similarity > 0 else '❓ Sin datos suficientes'}

✅ +25 puntos por análisis de correlación
    """

    await update.message.reply_html(report)


async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Análisis de actividad de usuario"""
    if not context.args:
        await update.message.reply_text("Uso: /activity @usuario")
        return

    username = context.args[0].replace('@', '')
    scanner_id = update.effective_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total de mensajes
    cursor.execute('''
        SELECT COUNT(*) FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
    ''', (username,))
    total_messages = cursor.fetchone()[0] or 0

    # Distribución por hora del día
    cursor.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as cnt
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        GROUP BY hour ORDER BY cnt DESC LIMIT 5
    ''', (username,))
    hourly = cursor.fetchall()

    # Distribución por día de la semana
    cursor.execute('''
        SELECT strftime('%w', timestamp) as weekday, COUNT(*) as cnt
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        GROUP BY weekday ORDER BY cnt DESC
    ''', (username,))
    weekly = cursor.fetchall()

    # Primera y última actividad
    cursor.execute('''
        SELECT MIN(timestamp), MAX(timestamp)
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
    ''', (username,))
    first_last = cursor.fetchone()

    conn.close()

    if total_messages == 0:
        await update.message.reply_text(f"No hay actividad registrada para @{username}")
        return

    weekday_names = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

    activity_text = f"""
📈 **Análisis de Actividad - @{username}**

**Resumen:**
• Total de mensajes: {total_messages}
• Primera actividad: {first_last[0][:10] if first_last[0] else 'N/A'}
• Última actividad: {first_last[1][:10] if first_last[1] else 'N/A'}

**Horas más activas:**
"""
    for hour, count in hourly:
        activity_text += f"  • {hour}:00h — {count} mensajes\n"

    activity_text += "\n**Días más activos:**\n"
    for weekday, count in weekly[:3]:
        day_name = weekday_names[int(weekday)] if weekday else '?'
        activity_text += f"  • {day_name} — {count} mensajes\n"

    bot_instance.add_points(scanner_id, 15)
    activity_text += "\n✅ +15 puntos por análisis de actividad"

    await update.message.reply_html(activity_text)


async def common_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar grupos en común con usuario"""
    if not context.args:
        await update.message.reply_text("Uso: /common_groups @usuario")
        return

    username = context.args[0].replace('@', '')
    scanner_id = update.effective_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener chats donde el usuario ha tenido actividad
    cursor.execute('''
        SELECT DISTINCT chat_id, COUNT(*) as msgs
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        GROUP BY chat_id ORDER BY msgs DESC
    ''', (username,))
    user_chats = cursor.fetchall()

    # Obtener chats del usuario que hace la consulta
    cursor.execute('''
        SELECT DISTINCT chat_id
        FROM activity_log
        WHERE user_id = ?
    ''', (scanner_id,))
    my_chats = {row[0] for row in cursor.fetchall()}

    conn.close()

    common = [(chat_id, msgs) for chat_id, msgs in user_chats if chat_id in my_chats]

    if not user_chats:
        await update.message.reply_text(f"No hay actividad registrada para @{username}")
        return

    bot_instance.add_points(scanner_id, 10)

    groups_text = f"""
👥 **Grupos en Común - @{username}**

**Chats con actividad de @{username}:** {len(user_chats)}
**Grupos en común contigo:** {len(common)}
"""

    if common:
        groups_text += "\n**Grupos compartidos:**\n"
        for chat_id, msgs in common:
            groups_text += f"  • Chat ID {chat_id}: {msgs} mensajes\n"
    else:
        groups_text += "\nNo se encontraron grupos en común en la base de datos de este bot.\n"

    groups_text += "\n✅ +10 puntos por análisis de grupos"

    await update.message.reply_html(groups_text)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generar reporte OSINT completo"""
    if not context.args:
        await update.message.reply_text("Uso: /report @usuario")
        return

    username = context.args[0].replace('@', '')
    scanner_id = update.effective_user.id

    await update.message.reply_text(f"📄 Generando reporte OSINT completo de @{username}...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Datos del participante
    cursor.execute('''
        SELECT user_id, full_name, joined_at, points, osint_scans, phishing_failed, ctf_flags_found
        FROM participants WHERE username = ?
    ''', (username,))
    participant = cursor.fetchone()

    # Total de mensajes
    cursor.execute('''
        SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
    ''', (username,))
    msg_stats = cursor.fetchone()

    # Hora más activa
    cursor.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as cnt
        FROM activity_log
        WHERE user_id IN (SELECT user_id FROM participants WHERE username = ?)
        GROUP BY hour ORDER BY cnt DESC LIMIT 1
    ''', (username,))
    peak_hour = cursor.fetchone()

    # Últimos scans OSINT sobre este usuario
    cursor.execute('''
        SELECT scan_type, timestamp FROM osint_scans
        WHERE target_id IN (SELECT user_id FROM participants WHERE username = ?)
        ORDER BY timestamp DESC LIMIT 5
    ''', (username,))
    scans_on_user = cursor.fetchall()

    conn.close()

    if not participant:
        await update.message.reply_text(
            f"@{username} no está registrado en este bot.\n"
            "Solo se pueden generar reportes de usuarios que hayan usado /start."
        )
        return

    user_id, full_name, joined_at, points, osint_scans, phishing_failed, ctf_flags = participant
    total_msgs, first_msg, last_msg = msg_stats

    report_text = f"""
📊 **REPORTE OSINT COMPLETO**
━━━━━━━━━━━━━━━━━━━━━━━

**Objetivo:** @{username}
**Nombre:** {full_name or 'Desconocido'}
**User ID:** {user_id}
**Registrado:** {joined_at[:10] if joined_at else 'N/A'}

**Actividad:**
• Total de mensajes: {total_msgs or 0}
• Primera actividad: {first_msg[:10] if first_msg else 'N/A'}
• Última actividad: {last_msg[:10] if last_msg else 'N/A'}
• Hora pico: {peak_hour[0] + ':00h' if peak_hour else 'N/A'}

**Participación en el Lab:**
• Puntos acumulados: {points}
• Scans OSINT realizados: {osint_scans}
• Tests de phishing fallidos: {phishing_failed}
• Flags CTF encontradas: {ctf_flags}

**Scans recibidos:** {len(scans_on_user)}

━━━━━━━━━━━━━━━━━━━━━━━
**Escaneado por:** {update.effective_user.mention_html()}
**Fecha del reporte:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

✅ +20 puntos por generar reporte completo
    """

    bot_instance.add_points(scanner_id, 20)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO osint_scans (scanner_id, target_id, scan_type, findings, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (scanner_id, user_id, 'full_report', json.dumps({'target': username}), datetime.now().isoformat()))
    conn.commit()
    conn.close()

    await update.message.reply_html(report_text)


# ==================== COMANDOS DE ADMINISTRADOR ====================

async def give_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dar consentimiento a un usuario (solo admin)"""
    admin_id = update.effective_user.id

    if admin_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Este comando es solo para administradores.")
        return

    if not context.args:
        await update.message.reply_text("Uso: /give_consent @usuario")
        return

    username = context.args[0].replace('@', '')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE participants SET consent_given = 1 WHERE username = ?
    ''', (username,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_affected > 0:
        await update.message.reply_html(
            f"✅ Consentimiento otorgado a @{username}\n"
            f"El usuario puede participar plenamente en los ejercicios."
        )
    else:
        await update.message.reply_text(
            f"⚠️ Usuario @{username} no encontrado.\n"
            "El usuario debe usar /start primero para registrarse."
        )


async def reset_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reiniciar puntos de todos los participantes (solo admin)"""
    admin_id = update.effective_user.id

    if admin_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Este comando es solo para administradores.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if context.args and context.args[0].startswith('@'):
        # Reiniciar solo un usuario
        username = context.args[0].replace('@', '')
        cursor.execute('''
            UPDATE participants SET points = 0, osint_scans = 0,
            phishing_caught = 0, phishing_failed = 0, ctf_flags_found = 0
            WHERE username = ?
        ''', (username,))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        if rows > 0:
            await update.message.reply_html(f"✅ Puntos de @{username} reiniciados a 0.")
        else:
            await update.message.reply_text(f"⚠️ Usuario @{username} no encontrado.")
    else:
        # Reiniciar todos
        cursor.execute('''
            UPDATE participants SET points = 0, osint_scans = 0,
            phishing_caught = 0, phishing_failed = 0, ctf_flags_found = 0
        ''')
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        await update.message.reply_html(
            f"✅ Puntos de <b>todos los participantes</b> reiniciados a 0.\n"
            f"({rows} usuarios afectados)"
        )


# ==================== REGISTRO DE ACTIVIDAD ====================

async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registrar todos los mensajes para análisis"""
    if update.message:
        user = update.effective_user
        bot_instance.add_participant(user.id, user.username, user.full_name)
        bot_instance.log_activity(
            user.id,
            update.message.text or '[media]',
            'text' if update.message.text else 'media',
            update.effective_chat.id
        )

# ==================== MAIN ====================

def main():
    """Iniciar bot"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          OSINT LAB - Red Team Training Bot                  ║")
    print("║              Author: David Merchán                          ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    print("⚠️  SOLO PARA USO EDUCATIVO CON CONSENTIMIENTO")
    print("[*] Iniciando bot...\n")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("osint_scan", osint_scan))
    application.add_handler(CommandHandler("reverse_image", reverse_image))
    application.add_handler(CommandHandler("metadata", metadata))
    application.add_handler(CommandHandler("timeline", timeline))
    application.add_handler(CommandHandler("correlate", correlate))
    application.add_handler(CommandHandler("patterns", patterns))
    application.add_handler(CommandHandler("activity", activity))
    application.add_handler(CommandHandler("common_groups", common_groups))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("phish_create", phish_create))
    application.add_handler(CommandHandler("phish_stats", phish_stats))
    application.add_handler(CommandHandler("ctf_status", ctf_status))
    application.add_handler(CommandHandler("submit_flag", submit_flag))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("mystats", mystats))
    application.add_handler(CommandHandler("give_consent", give_consent))
    application.add_handler(CommandHandler("reset_points", reset_points))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(phishing_callback, pattern='^phish_'))
    
    # Log de mensajes
    application.add_handler(MessageHandler(filters.ALL, log_message))
    
    print("[+] Bot iniciado correctamente!")
    print("[+] Presiona Ctrl+C para detener\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
