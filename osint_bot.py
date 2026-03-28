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
BOT_TOKEN = "8395396525:AAE5f4ffIyPXDcJ5Wvcu6ZxzVA8xL3hSy2I"  # Token de @BotFather
ADMIN_IDS = [482330941]  # IDs de administradores del laboratorio

# Base de datos
DB_PATH = 'data/osint_lab.db'

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
    application.add_handler(CommandHandler("timeline", timeline))
    application.add_handler(CommandHandler("patterns", patterns))
    application.add_handler(CommandHandler("phish_create", phish_create))
    application.add_handler(CommandHandler("phish_stats", phish_stats))
    application.add_handler(CommandHandler("ctf_status", ctf_status))
    application.add_handler(CommandHandler("submit_flag", submit_flag))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("mystats", mystats))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(phishing_callback, pattern='^phish_'))
    
    # Log de mensajes
    application.add_handler(MessageHandler(filters.ALL, log_message))
    
    print("[+] Bot iniciado correctamente!")
    print("[+] Presiona Ctrl+C para detener\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
