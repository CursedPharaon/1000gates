import asyncio
import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from supabase import create_client, Client

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8858271245:AAHMRubTDf_-_cmraJyW18Ka6w4VpDSP_JQ"
SUPABASE_URL = "https://tmjqafqecjpizawdruzq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRtanFhZnFlY2pwaXphd2RydXpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4OTk2OTYsImV4cCI6MjA5NTQ3NTY5Nn0.8K7i5QEbjYWSvqw78P8RSR_abYM8uCRZbvC9Hp12bac"

# Админ (твой Telegram username)
ADMIN_USERNAME = "cursed_pharaon"

logging.basicConfig(level=logging.INFO)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== ДАННЫЕ ИГРЫ ==========
# КВЕСТЫ (12 штук)
QUESTS = [
    {"id": 0, "name": "🍄 Лесной тролль", "hp": 280, "atk": 32, "gold": 110, "xp": 52, "glory": 6, "key": "Медный ключ", "key_chance": 0.6, "materials": [{"name": "Троллья кровь", "qty": 1, "chance": 0.8}]},
    {"id": 1, "name": "🔥 Огненный элементаль", "hp": 340, "atk": 41, "gold": 150, "xp": 70, "glory": 9, "key": "Огненный ключ", "key_chance": 0.55, "materials": [{"name": "Пламенный цветок", "qty": 1, "chance": 0.7}]},
    {"id": 2, "name": "⚔️ Теневой рыцарь", "hp": 430, "atk": 55, "gold": 210, "xp": 105, "glory": 14, "key": "Теневой ключ", "key_chance": 0.5, "materials": [{"name": "Теневые нити", "qty": 2, "chance": 0.9}]},
    {"id": 3, "name": "❄️ Ледяной голем", "hp": 510, "atk": 68, "gold": 280, "xp": 140, "glory": 18, "key": "Ледяной ключ", "key_chance": 0.45, "materials": [{"name": "Ледяной осколок", "qty": 2, "chance": 0.8}]},
    {"id": 4, "name": "💀 Древний скелет", "hp": 470, "atk": 72, "gold": 310, "xp": 160, "glory": 21, "key": "Костяной ключ", "key_chance": 0.4, "materials": [{"name": "Древняя кость", "qty": 3, "chance": 0.9}]},
    {"id": 5, "name": "🐉 Пустынный дракон", "hp": 640, "atk": 92, "gold": 440, "xp": 230, "glory": 29, "key": "Драконий ключ", "key_chance": 0.35, "materials": [{"name": "Драконья чешуя", "qty": 1, "chance": 0.6}]},
    {"id": 6, "name": "🌀 Магистр хаоса", "hp": 580, "atk": 98, "gold": 490, "xp": 260, "glory": 33, "key": "Магический ключ", "key_chance": 0.3, "materials": [{"name": "Древний пергамент", "qty": 1, "chance": 0.7}]},
    {"id": 7, "name": "🪨 Каменный титан", "hp": 790, "atk": 115, "gold": 660, "xp": 360, "glory": 41, "key": "Рунический ключ", "key_chance": 0.25, "materials": [{"name": "Рунический камень", "qty": 2, "chance": 0.8}]},
    {"id": 8, "name": "👑 Король орков", "hp": 710, "atk": 108, "gold": 610, "xp": 330, "glory": 38, "key": "Королевский ключ", "key_chance": 0.3, "materials": [{"name": "Трофей орка", "qty": 2, "chance": 0.9}]},
    {"id": 9, "name": "⚡ Громовой дух", "hp": 860, "atk": 128, "gold": 790, "xp": 440, "glory": 50, "key": "Громовой ключ", "key_chance": 0.2, "materials": [{"name": "Эссенция бури", "qty": 1, "chance": 0.6}]},
    {"id": 10, "name": "🌋 Владыка магмы", "hp": 1020, "atk": 152, "gold": 980, "xp": 550, "glory": 65, "key": "Магмовый ключ", "key_chance": 0.15, "materials": [{"name": "Осколок магмы", "qty": 3, "chance": 0.9}]},
    {"id": 11, "name": "🐉 Изначальный дракон", "hp": 1250, "atk": 185, "gold": 1350, "xp": 760, "glory": 85, "key": "Древний ключ", "key_chance": 0.1, "materials": [{"name": "Драконье сердце", "qty": 1, "chance": 0.5}]}
]

# ЭЛИТНЫЕ БОССЫ (нужны ключи)
ELITE_BOSSES = [
    {"name": "🗿 Каменный страж", "hp": 800, "atk": 70, "gold": 500, "xp": 250, "glory": 30, "need_key": "Медный ключ", "materials": [{"name": "Осколок магмы", "qty": 2}]},
    {"name": "❄️ Ледяной дракон", "hp": 1200, "atk": 95, "gold": 750, "xp": 380, "glory": 45, "need_key": "Огненный ключ", "materials": [{"name": "Ледяной осколок", "qty": 2}]},
    {"name": "💀 Лич Некромант", "hp": 1800, "atk": 130, "gold": 1100, "xp": 550, "glory": 60, "need_key": "Теневой ключ", "materials": [{"name": "Теневые нити", "qty": 3}]},
    {"name": "🐉 Древний виверн", "hp": 2500, "atk": 170, "gold": 1600, "xp": 800, "glory": 80, "need_key": "Драконий ключ", "materials": [{"name": "Драконья чешуя", "qty": 3}]},
    {"name": "🌋 Повелитель магмы", "hp": 3400, "atk": 220, "gold": 2300, "xp": 1150, "glory": 110, "need_key": "Магмовый ключ", "materials": [{"name": "Осколок магмы", "qty": 5}]},
    {"name": "👑 Король драконов", "hp": 5000, "atk": 300, "gold": 3500, "xp": 1800, "glory": 160, "need_key": "Древний ключ", "materials": [{"name": "Драконье сердце", "qty": 2}]}
]

# ОРУЖИЕ
WEAPONS = [
    {"name": "⚔️ Ржавый меч", "dmg": 12, "cost": 0},
    {"name": "🗡️ Стальной клинок", "dmg": 24, "cost": 480},
    {"name": "🔥 Пламенный топор", "dmg": 38, "cost": 1050},
    {"name": "❄️ Ледяной рассекатель", "dmg": 54, "cost": 1780},
    {"name": "⚡ Громовой меч", "dmg": 72, "cost": 2750},
    {"name": "💀 Жнец душ", "dmg": 94, "cost": 4100},
    {"name": "🐉 Драконий гнев", "dmg": 120, "cost": 5900},
    {"name": "🌀 Клинок Хаоса", "dmg": 155, "cost": 8200},
    {"name": "⭐ Звёздный клинок", "dmg": 200, "cost": 11500},
    {"name": "🌌 Артефакт древних", "dmg": 280, "cost": 17000}
]

# Хранилище активных боёв
active_battles = {}

# ========== РАБОТА С БАЗОЙ ==========
async def get_or_create_player(user_id: int, username: str):
    response = supabase.table("players").select("*").eq("username", str(user_id)).execute()
    if response.data:
        return response.data[0]
    else:
        new_player = {
            "username": str(user_id),
            "name": username,
            "gold": 1400,
            "glory": 0,
            "level": 1,
            "hp": 210,
            "max_hp": 210,
            "xp": 0,
            "weapon_name": WEAPONS[0]["name"],
            "weapon_dmg": WEAPONS[0]["dmg"],
            "weapon_upgrade": 0,
            "player_class": "Воин",
            "talent_dmg": 0,
            "talent_crit": 0,
            "talent_hp": 0,
            "talent_points": 1,
            "keys": {},
            "materials": {},
            "armor": 0
        }
        supabase.table("players").insert(new_player).execute()
        return new_player

async def save_player(user_id: int, player_data: dict):
    supabase.table("players").update(player_data).eq("username", str(user_id)).execute()

# ========== ИГРОВЫЕ РАСЧЁТЫ ==========
def get_player_damage(player):
    weapon_dmg = player.get("weapon_dmg", 12)
    upgrade = player.get("weapon_upgrade", 0)
    talent_dmg = player.get("talent_dmg", 0)
    level = player.get("level", 1)
    base = weapon_dmg + upgrade * 5 + level * 2 + talent_dmg * 4
    return random.randint(base, base + 12)

def get_crit_chance(player):
    talent_crit = player.get("talent_crit", 0)
    return 0.08 + talent_crit * 0.025

def get_max_hp(player):
    base_hp = player.get("max_hp", 210)
    talent_hp = player.get("talent_hp", 0)
    return int(base_hp * (1 + talent_hp * 0.05))

def get_keys_text(player):
    keys = player.get("keys", {})
    if not keys:
        return "нет"
    return ", ".join([f"{k}: {v}" for k, v in keys.items()])

def get_materials_text(player):
    mats = player.get("materials", {})
    if not mats:
        return "нет"
    return ", ".join([f"{k}: {v}" for k, v in mats.items()])

def get_player_stats_text(player):
    max_hp = get_max_hp(player)
    dmg = get_player_damage(player)
    crit = get_crit_chance(player) * 100
    upgrade = player.get("weapon_upgrade", 0)
    weapon_name = player.get("weapon_name", "⚔️ Меч")
    
    text = f"🎭 *{player.get('player_class', 'Воин')}* | Уровень {player.get('level', 1)}\n"
    text += f"❤️ {player.get('hp', max_hp)}/{max_hp} HP\n"
    text += f"⚔️ Урон: {dmg}\n"
    text += f"🎯 Крит: {crit:.1f}%\n"
    text += f"🗡️ {weapon_name}"
    if upgrade > 0:
        text += f" +{upgrade}"
    text += f"\n🪙 {player.get('gold', 0)} золота\n"
    text += f"✨ {player.get('glory', 0)} славы\n"
    text += f"⭐ Очков талантов: {player.get('talent_points', 0)}\n"
    text += f"📊 Опыт: {player.get('xp', 0)}/{100 + player.get('level', 1) * 15}\n"
    text += f"🔑 Ключи: {get_keys_text(player)}\n"
    text += f"📦 Материалы: {get_materials_text(player)}"
    return text

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📜 КВЕСТЫ", callback_data="quests")],
        [InlineKeyboardButton("👑 ЭЛИТНЫЕ БОССЫ", callback_data="elite_bosses")],
        [InlineKeyboardButton("🏪 МАГАЗИН", callback_data="shop"),
         InlineKeyboardButton("⭐ ТАЛАНТЫ", callback_data="talents")],
        [InlineKeyboardButton("📦 СТАТЫ", callback_data="stats"),
         InlineKeyboardButton("🏆 ТОП", callback_data="top")],
        [InlineKeyboardButton("🔨 ЗАТОЧКА +1", callback_data="upgrade")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quests_keyboard():
    keyboard = []
    for q in QUESTS:
        keyboard.append([InlineKeyboardButton(q["name"], callback_data=f"quest_{q['id']}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_elite_keyboard(player):
    keyboard = []
    for i, b in enumerate(ELITE_BOSSES):
        has_key = player.get("keys", {}).get(b["need_key"], 0) > 0
        status = "✅" if has_key else "🔒"
        keyboard.append([InlineKeyboardButton(f"{status} {b['name']} (нужен {b['need_key']})", callback_data=f"elite_{i}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_shop_keyboard():
    keyboard = []
    for i, w in enumerate(WEAPONS):
        keyboard.append([InlineKeyboardButton(f"{w['name']} +{w['dmg']} — {w['cost']}💰", callback_data=f"buy_{i}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_talents_keyboard():
    keyboard = [
        [InlineKeyboardButton("💪 СИЛА (+урон)", callback_data="talent_dmg")],
        [InlineKeyboardButton("🎯 МЕТКОСТЬ (+крит)", callback_data="talent_crit")],
        [InlineKeyboardButton("❤️ ЖИВУЧЕСТЬ (+HP)", callback_data="talent_hp")],
        [InlineKeyboardButton("◀️ НАЗАД", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_battle_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚔️ АТАКА", callback_data="attack"),
         InlineKeyboardButton("💚 ЛЕЧЕНИЕ", callback_data="heal")],
        [InlineKeyboardButton("🚪 СДАЧА", callback_data="surrender")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД", callback_data="back")]])

# ========== АДМИН-КОМАНДЫ ==========
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("❌ У вас нет прав администратора!")
        return
    
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❌ Использование: /админ <команда> <username> <значение>\n\nКоманды:\nлвл, голд, слава, хп, урон, броня, ключ, материал")
        return
    
    cmd = args[0].lower()
    target_name = args[1]
    
    response = supabase.table("players").select("*").eq("username", target_name).execute()
    if not response.data:
        await update.message.reply_text(f"❌ Игрок {target_name} не найден!")
        return
    
    player = response.data[0]
    
    try:
        if cmd == "лвл":
            new_level = int(args[2])
            player["level"] = new_level
            player["max_hp"] = 210 + (new_level - 1) * 20
            player["hp"] = player["max_hp"]
            await update.message.reply_text(f"✅ Игроку {target_name} установлен уровень {new_level}")
        
        elif cmd == "голд":
            player["gold"] = int(args[2])
            await update.message.reply_text(f"✅ Игроку {target_name} установлено золото {args[2]}")
        
        elif cmd == "слава":
            player["glory"] = int(args[2])
            await update.message.reply_text(f"✅ Игроку {target_name} установлена слава {args[2]}")
        
        elif cmd == "хп":
            player["hp"] = int(args[2])
            player["max_hp"] = int(args[2])
            await update.message.reply_text(f"✅ Игроку {target_name} установлено HP {args[2]}")
        
        elif cmd == "урон":
            player["weapon_dmg"] = int(args[2])
            await update.message.reply_text(f"✅ Игроку {target_name} установлен урон оружия {args[2]}")
        
        elif cmd == "броня":
            player["armor"] = int(args[2])
            await update.message.reply_text(f"✅ Игроку {target_name} установлена броня {args[2]}")
        
        elif cmd == "ключ":
            if len(args) < 4:
                await update.message.reply_text("❌ Использование: /админ ключ username Название_ключа 5")
                return
            key_name = args[2]
            key_qty = int(args[3])
            keys = player.get("keys", {})
            keys[key_name] = keys.get(key_name, 0) + key_qty
            player["keys"] = keys
            await update.message.reply_text(f"✅ Игроку {target_name} добавлен ключ {key_name} x{key_qty}")
        
        elif cmd == "материал":
            if len(args) < 4:
                await update.message.reply_text("❌ Использование: /админ материал username Название_материала 5")
                return
            mat_name = args[2]
            mat_qty = int(args[3])
            mats = player.get("materials", {})
            mats[mat_name] = mats.get(mat_name, 0) + mat_qty
            player["materials"] = mats
            await update.message.reply_text(f"✅ Игроку {target_name} добавлен материал {mat_name} x{mat_qty}")
        
        else:
            await update.message.reply_text("❌ Неизвестная команда. Доступно: лвл, голд, слава, хп, урон, броня, ключ, материал")
            return
        
        supabase.table("players").update(player).eq("username", target_name).execute()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# ========== ОБРАБОТЧИКИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = await get_or_create_player(user.id, user.first_name)
    
    text = f"🌀 *Добро пожаловать, {user.first_name}!*\n\n"
    text += get_player_stats_text(player)
    text += "\n\n*Выбери действие:*"
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    player = await get_or_create_player(user_id, update.effective_user.first_name)
    
    # КВЕСТЫ (список)
    if data == "quests":
        await query.edit_message_text("📜 *Выбери квеста:*", parse_mode="Markdown", reply_markup=get_quests_keyboard())
        return
    
    # НАЧАТЬ КВЕСТ
    if data.startswith("quest_"):
        quest_id = int(data.split("_")[1])
        quest = QUESTS[quest_id]
        
        active_battles[user_id] = {
            "type": "quest",
            "enemy": quest.copy(),
            "enemy_hp": quest["hp"]
        }
        
        text = f"⚔️ *{quest['name']}*\n❤️ {quest['hp']}/{quest['hp']} HP\n⚔️ Атака: {quest['atk']}\n\n💰 Награда: {quest['gold']} золота, {quest['xp']} опыта, {quest['glory']} славы\n🔑 Шанс ключа: {int(quest['key_chance']*100)}%\n📦 Шанс материала: {int(quest['materials'][0]['chance']*100)}%"
        
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        return
    
    # ЭЛИТНЫЕ БОССЫ (список)
    if data == "elite_bosses":
        await query.edit_message_text("👑 *Элитные боссы (нужны ключи):*", parse_mode="Markdown", reply_markup=get_elite_keyboard(player))
        return
    
    # НАЧАТЬ ЭЛИТНОГО БОССА
    if data.startswith("elite_"):
        boss_id = int(data.split("_")[1])
        boss = ELITE_BOSSES[boss_id]
        
        keys = player.get("keys", {})
        if keys.get(boss["need_key"], 0) <= 0:
            await query.answer(f"❌ Нужен {boss['need_key']}!", show_alert=True)
            return
        
        keys[boss["need_key"]] -= 1
        if keys[boss["need_key"]] == 0:
            del keys[boss["need_key"]]
        player["keys"] = keys
        await save_player(user_id, player)
        
        active_battles[user_id] = {
            "type": "elite",
            "enemy": boss.copy(),
            "enemy_hp": boss["hp"]
        }
        
        materials_text = ", ".join([f"{m['name']} x{m['qty']}" for m in boss['materials']])
        text = f"⚔️ *ЭЛИТНЫЙ БОСС: {boss['name']}*\n❤️ {boss['hp']}/{boss['hp']} HP\n⚔️ Атака: {boss['atk']}\n\n💰 Награда: {boss['gold']} золота, {boss['xp']} опыта, {boss['glory']} славы\n📦 Материалы: {materials_text}"
        
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        return
    
    # АТАКА
    if data == "attack":
        battle = active_battles.get(user_id)
        if not battle:
            await query.edit_message_text("❌ Нет активного боя! Начни квест или босса.", reply_markup=get_main_keyboard())
            return
        
        enemy = battle["enemy"]
        enemy_hp = battle["enemy_hp"]
        
        if enemy_hp <= 0:
            await query.edit_message_text("❌ Враг уже побеждён!", reply_markup=get_back_keyboard())
            return
        
        dmg = get_player_damage(player)
        is_crit = random.random() < get_crit_chance(player)
        if is_crit:
            dmg = int(dmg * 1.7)
        
        enemy_hp -= dmg
        battle["enemy_hp"] = max(0, enemy_hp)
        
        result_text = f"⚔️ Ты нанёс *{dmg}* урона"
        if is_crit:
            result_text += " *КРИТИЧЕСКИЙ УДАР!*"
        result_text += "!\n\n"
        
        if enemy_hp <= 0:
            gold_gain = enemy["gold"] + random.randint(0, 50)
            glory_gain = enemy["glory"]
            xp_gain = enemy["xp"]
            
            player["gold"] = player.get("gold", 0) + gold_gain
            player["glory"] = player.get("glory", 0) + glory_gain
            player["xp"] = player.get("xp", 0) + xp_gain
            
            if battle["type"] == "quest" and "key" in enemy:
                if random.random() < enemy["key_chance"]:
                    keys = player.get("keys", {})
                    keys[enemy["key"]] = keys.get(enemy["key"], 0) + 1
                    player["keys"] = keys
                    result_text += f"🔑 Выпал *{enemy['key']}*!\n"
            
            if "materials" in enemy:
                mats = player.get("materials", {})
                for mat in enemy["materials"]:
                    if random.random() < mat.get("chance", 1.0):
                        mats[mat["name"]] = mats.get(mat["name"], 0) + mat["qty"]
                        result_text += f"📦 Выпал *{mat['name']}* x{mat['qty']}!\n"
                player["materials"] = mats
            
            need_xp = 100 + player.get("level", 1) * 15
            level_up = False
            while player["xp"] >= need_xp:
                player["level"] += 1
                player["xp"] -= need_xp
                player["max_hp"] += 20
                player["talent_points"] = player.get("talent_points", 0) + 1
                need_xp = 100 + player["level"] * 15
                level_up = True
            
            player["hp"] = get_max_hp(player)
            await save_player(user_id, player)
            
            result_text += f"\n🏆 *ПОБЕДА!*\n+{gold_gain}💰 +{glory_gain}✨ +{xp_gain}⭐\n"
            if level_up:
                result_text += f"✨ *УРОВЕНЬ {player['level']}!* +1 очко талантов ✨\n"
            
            del active_battles[user_id]
            await query.edit_message_text(result_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
            return
        
        enemy_dmg = random.randint(enemy["atk"] - 8, enemy["atk"] + 4)
        enemy_dmg = max(5, enemy_dmg)
        
        player_hp = player.get("hp", get_max_hp(player))
        player_hp -= enemy_dmg
        player["hp"] = max(0, player_hp)
        await save_player(user_id, player)
        
        result_text += f"😈 *{enemy['name']}* атакует и наносит *{enemy_dmg}* урона!\n"
        
        if player_hp <= 0:
            result_text += f"\n💀 *ТЫ ПОВЕРЖЕН!*\nВосстановлен в таверне за 15% золота."
            player["hp"] = get_max_hp(player)
            player["gold"] = max(300, int(player.get("gold", 0) * 0.85))
            await save_player(user_id, player)
            del active_battles[user_id]
            await query.edit_message_text(result_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
            return
        
        text = result_text + f"\n*{enemy['name']}*\n❤️ {battle['enemy_hp']}/{enemy['hp']} HP\n\n"
        text += get_player_stats_text(player)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        return
    
    # ЛЕЧЕНИЕ
    if data == "heal":
        cost = 45
        gold = player.get("gold", 0)
        max_hp = get_max_hp(player)
        current_hp = player.get("hp", max_hp)
        
        if gold >= cost and current_hp < max_hp:
            heal_amount = 48
            new_hp = min(max_hp, current_hp + heal_amount)
            player["hp"] = new_hp
            player["gold"] = gold - cost
            await save_player(user_id, player)
            
            battle = active_battles.get(user_id)
            if battle:
                text = f"💚 Восстановлено *{heal_amount}* HP! -{cost}💰\n\n*{battle['enemy']['name']}*\n❤️ {battle['enemy_hp']}/{battle['enemy']['hp']} HP\n\n"
                text += get_player_stats_text(player)
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
            else:
                await query.edit_message_text(f"💚 Восстановлено *{heal_amount}* HP! -{cost}💰\n\n{get_player_stats_text(player)}", parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            await query.answer("❌ Не хватает золота или HP полное!", show_alert=True)
        return
    
    # СДАЧА
    if data == "surrender":
        if user_id in active_battles:
            del active_battles[user_id]
        await query.edit_message_text("🚪 Ты сдался и вернулся в город.", reply_markup=get_main_keyboard())
        return
    
    # МАГАЗИН
    if data == "shop":
        text = "*🏪 ОРУЖЕЙНАЯ МАСТЕРА*\n\n" + get_player_stats_text(player)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_shop_keyboard())
        return
    
    if data.startswith("buy_"):
        weapon_idx = int(data.split("_")[1])
        weapon = WEAPONS[weapon_idx]
        current_name = player.get("weapon_name", "")
        current_idx = next((i for i, w in enumerate(WEAPONS) if w["name"] == current_name), 0)
        
        if weapon_idx <= current_idx:
            await query.answer("❌ Это оружие слабее или такое же!", show_alert=True)
            return
        
        if player.get("gold", 0) >= weapon["cost"]:
            player["gold"] -= weapon["cost"]
            player["weapon_name"] = weapon["name"]
            player["weapon_dmg"] = weapon["dmg"]
            await save_player(user_id, player)
            text = f"✅ Куплено: *{weapon['name']}* +{weapon['dmg']} урона!\n\n" + get_player_stats_text(player)
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_shop_keyboard())
        else:
            await query.answer("❌ Не хватает золота!", show_alert=True)
        return
    
    # ТАЛАНТЫ
    if data == "talents":
        text = f"*⭐ ДРЕВО ТАЛАНТОВ*\nОчков: {player.get('talent_points', 0)}\n\n"
        text += f"💪 СИЛА: +{player.get('talent_dmg', 0) * 4} урона\n"
        text += f"🎯 МЕТКОСТЬ: +{player.get('talent_crit', 0) * 2.5:.0f}% крита\n"
        text += f"❤️ ЖИВУЧЕСТЬ: +{player.get('talent_hp', 0) * 5}% HP\n\n"
        text += get_player_stats_text(player)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_talents_keyboard())
        return
    
    if data.startswith("talent_"):
        talent_type = data.split("_")[1]
        points = player.get("talent_points", 0)
        
        if points <= 0:
            await query.answer("❌ Нет очков талантов!", show_alert=True)
            return
        
        if talent_type == "dmg":
            player["talent_dmg"] = player.get("talent_dmg", 0) + 1
        elif talent_type == "crit":
            player["talent_crit"] = player.get("talent_crit", 0) + 1
        elif talent_type == "hp":
            player["talent_hp"] = player.get("talent_hp", 0) + 1
        
        player["talent_points"] = points - 1
        await save_player(user_id, player)
        
        text = f"✅ Талант улучшен!\n\n" + get_player_stats_text(player)
        battle = active_battles.get(user_id)
        if battle:
            text += f"\n\n*{battle['enemy']['name']}*\n❤️ {battle['enemy_hp']}/{battle['enemy']['hp']} HP"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        else:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return
    
    # СТАТЫ
    if data == "stats":
        text = get_player_stats_text(player)
        battle = active_battles.get(user_id)
        if battle:
            text += f"\n\n*{battle['enemy']['name']}*\n❤️ {battle['enemy_hp']}/{battle['enemy']['hp']} HP"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        else:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return
    
    # ТОП
    if data == "top":
        response = supabase.table("players").select("name, glory, level, gold").order("glory", desc=True).limit(10).execute()
        text = "*🏆 ТОП-10 ПО СЛАВЕ 🏆*\n\n"
        for i, p in enumerate(response.data):
            text += f"{i+1}. {p.get('name', 'Unknown')} — ✨{p.get('glory', 0)} | Ур.{p.get('level', 1)} | 🪙{p.get('gold', 0)}\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())
        return
    
    # ЗАТОЧКА
    if data == "upgrade":
        upgrade_level = player.get("weapon_upgrade", 0)
        if upgrade_level >= 12:
            await query.answer("🔨 Оружие уже заточено до +12!", show_alert=True)
            return
        
        cost = 300 + upgrade_level * 120
        gold = player.get("gold", 0)
        
        if gold < cost:
            await query.answer(f"❌ Не хватает {cost} золота!", show_alert=True)
            return
        
        chance = max(0.3, 0.85 - upgrade_level * 0.045)
        
        if random.random() < chance:
            player["weapon_upgrade"] = upgrade_level + 1
            player["gold"] = gold - cost
            await save_player(user_id, player)
            text = f"✅ *УСПЕХ!* Оружие +{upgrade_level + 1}\n\n" + get_player_stats_text(player)
        else:
            lost = int(cost * 0.5)
            player["gold"] = gold - lost
            await save_player(user_id, player)
            text = f"💥 *ПРОВАЛ!* Потеряно {lost} золота.\n\n" + get_player_stats_text(player)
        
        battle = active_battles.get(user_id)
        if battle:
            text += f"\n\n*{battle['enemy']['name']}*\n❤️ {battle['enemy_hp']}/{battle['enemy']['hp']} HP"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        else:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return
    
    # НАЗАД
    if data == "back":
        text = get_player_stats_text(player)
        battle = active_battles.get(user_id)
        if battle:
            text += f"\n\n*{battle['enemy']['name']}*\n❤️ {battle['enemy_hp']}/{battle['enemy']['hp']} HP"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_battle_keyboard())
        else:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return

# ========== HEALTHCHECK ДЛЯ RENDER ==========
from flask import Flask
import threading

flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive!", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# Запускаем Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()
# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))  # ← изменил на admin
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🎮 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
