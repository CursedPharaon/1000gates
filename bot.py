import asyncio
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from supabase import create_client, Client

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8858271245:AAHMRubTDf_-_cmraJyW18Ka6w4VpDSP_JQ"
SUPABASE_URL = "https://tmjqafqecjpizawdruzq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRtanFhZnFlY2pwaXphd2RydXpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4OTk2OTYsImV4cCI6MjA5NTQ3NTY5Nn0.8K7i5QEbjYWSvqw78P8RSR_abYM8uCRZbvC9Hp12bac"

# Инициализация Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== ДАННЫЕ ИГРЫ ==========
ENEMIES = [
    {"name": "🍄 Лесной тролль", "hp": 280, "atk": 32, "gold": 110, "xp": 52, "glory": 6},
    {"name": "🔥 Огненный элементаль", "hp": 340, "atk": 41, "gold": 150, "xp": 70, "glory": 9},
    {"name": "⚔️ Теневой рыцарь", "hp": 430, "atk": 55, "gold": 210, "xp": 105, "glory": 14},
    {"name": "❄️ Ледяной голем", "hp": 510, "atk": 68, "gold": 280, "xp": 140, "glory": 18},
    {"name": "💀 Древний скелет", "hp": 470, "atk": 72, "gold": 310, "xp": 160, "glory": 21},
    {"name": "🐉 Пустынный дракон", "hp": 640, "atk": 92, "gold": 440, "xp": 230, "glory": 29},
    {"name": "🌀 Магистр хаоса", "hp": 580, "atk": 98, "gold": 490, "xp": 260, "glory": 33},
    {"name": "🪨 Каменный титан", "hp": 790, "atk": 115, "gold": 660, "xp": 360, "glory": 41},
    {"name": "👑 Король орков", "hp": 710, "atk": 108, "gold": 610, "xp": 330, "glory": 38},
    {"name": "⚡ Громовой дух", "hp": 860, "atk": 128, "gold": 790, "xp": 440, "glory": 50},
    {"name": "🌋 Владыка магмы", "hp": 1020, "atk": 152, "gold": 980, "xp": 550, "glory": 65},
    {"name": "🐉 Изначальный дракон", "hp": 1250, "atk": 185, "gold": 1350, "xp": 760, "glory": 85}
]

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

# Хранилище текущих боёв (user_id -> enemy_index, enemy_hp)
active_battles = {}

# ========== РАБОТА С БАЗОЙ ДАННЫХ ==========
async def get_or_create_player(user_id: int, username: str):
    """Получить игрока из БД или создать нового"""
    response = supabase.table("players").select("*").eq("username", str(user_id)).execute()
    
    if response.data:
        return response.data[0]
    else:
        # Создаём нового игрока
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
            "talent_points": 1
        }
        response = supabase.table("players").insert(new_player).execute()
        return response.data[0]

async def save_player(user_id: int, player_data: dict):
    """Сохранить данные игрока"""
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

def get_player_stats_text(player):
    """Текст со статистикой игрока"""
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
    text += f"📊 Опыт: {player.get('xp', 0)}/{100 + player.get('level', 1) * 15}"
    return text

def get_enemy_text(enemy, current_hp):
    """Текст врага"""
    percent = (current_hp / enemy["hp"]) * 100
    bar = "█" * int(percent // 10) + "░" * (10 - int(percent // 10))
    return f"*{enemy['name']}*\n❤️ {bar} {current_hp}/{enemy['hp']} HP"

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    """Главная клавиатура (в бою)"""
    keyboard = [
        [InlineKeyboardButton("⚔️ АТАКА", callback_data="attack")],
        [InlineKeyboardButton("💚 ЛЕЧЕНИЕ", callback_data="heal")],
        [InlineKeyboardButton("🔨 ЗАТОЧКА +1", callback_data="upgrade")],
        [InlineKeyboardButton("🌀 СМЕНА ВРАГА", callback_data="next_enemy")],
        [InlineKeyboardButton("🏪 МАГАЗИН", callback_data="shop"),
         InlineKeyboardButton("⭐ ТАЛАНТЫ", callback_data="talents")],
        [InlineKeyboardButton("📦 СТАТЫ", callback_data="stats"),
         InlineKeyboardButton("🏆 ТОП", callback_data="top")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_shop_keyboard():
    """Клавиатура магазина"""
    keyboard = []
    for i, w in enumerate(WEAPONS):
        keyboard.append([InlineKeyboardButton(f"{w['name']} +{w['dmg']} — {w['cost']}💰", callback_data=f"buy_{i}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_talents_keyboard():
    """Клавиатура талантов"""
    keyboard = [
        [InlineKeyboardButton("💪 СИЛА (+урон)", callback_data="talent_dmg")],
        [InlineKeyboardButton("🎯 МЕТКОСТЬ (+крит)", callback_data="talent_crit")],
        [InlineKeyboardButton("❤️ ЖИВУЧЕСТЬ (+HP)", callback_data="talent_hp")],
        [InlineKeyboardButton("◀️ НАЗАД", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Только кнопка назад"""
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

# ========== ОБРАБОТЧИКИ КОМАНД ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = await get_or_create_player(user.id, user.first_name)
    
    # Создаём первого врага
    enemy = ENEMIES[0]
    active_battles[user.id] = {
        "enemy_idx": 0,
        "enemy_hp": enemy["hp"]
    }
    
    text = f"🌀 *Добро пожаловать, {user.first_name}!*\n\n"
    text += get_player_stats_text(player)
    text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy['hp'])}"
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    # Получаем данные игрока из БД
    player_data = await get_or_create_player(user_id, update.effective_user.first_name)
    
    # Получаем текущего врага
    battle = active_battles.get(user_id)
    if not battle:
        battle = {"enemy_idx": 0, "enemy_hp": ENEMIES[0]["hp"]}
        active_battles[user_id] = battle
    
    enemy = ENEMIES[battle["enemy_idx"]]
    enemy_hp = battle["enemy_hp"]
    
    # ===== АТАКА =====
    if data == "attack":
        if enemy_hp <= 0:
            await query.edit_message_text("❌ Враг уже побеждён! Нажми «СМЕНА ВРАГА»", reply_markup=get_back_keyboard())
            return
        
        # Игрок атакует
        dmg = get_player_damage(player_data)
        is_crit = random.random() < get_crit_chance(player_data)
        if is_crit:
            dmg = int(dmg * 1.7)
        
        enemy_hp -= dmg
        battle["enemy_hp"] = max(0, enemy_hp)
        
        result_text = f"⚔️ Ты нанёс *{dmg}* урона"
        if is_crit:
            result_text += " *КРИТИЧЕСКИЙ УДАР!*"
        result_text += "!\n\n"
        
        # Проверка победы
        if enemy_hp <= 0:
            # Награда
            gold_gain = enemy["gold"] + random.randint(0, 50)
            glory_gain = enemy["glory"]
            xp_gain = enemy["xp"]
            
            player_data["gold"] = player_data.get("gold", 0) + gold_gain
            player_data["glory"] = player_data.get("glory", 0) + glory_gain
            player_data["xp"] = player_data.get("xp", 0) + xp_gain
            
            # Проверка уровня
            need_xp = 100 + player_data.get("level", 1) * 15
            level_up = False
            while player_data["xp"] >= need_xp:
                player_data["level"] += 1
                player_data["xp"] -= need_xp
                player_data["max_hp"] += 20
                player_data["talent_points"] = player_data.get("talent_points", 0) + 1
                need_xp = 100 + player_data["level"] * 15
                level_up = True
            
            # Восстанавливаем HP до нового максимума
            player_data["hp"] = get_max_hp(player_data)
            await save_player(user_id, player_data)
            
            result_text += f"🏆 *ПОБЕДА!*\n"
            result_text += f"+{gold_gain}💰 +{glory_gain}✨ +{xp_gain}⭐ опыта\n"
            if level_up:
                result_text += f"✨ *УРОВЕНЬ {player_data['level']}!* +1 очко талантов ✨\n"
            result_text += f"\nНажми «СМЕНА ВРАГА» для продолжения!"
            
            await query.edit_message_text(result_text, parse_mode="Markdown", reply_markup=get_back_keyboard())
            return
        
        # Враг атакует в ответ
        enemy_dmg = random.randint(enemy["atk"] - 10, enemy["atk"] + 5)
        enemy_dmg = max(5, enemy_dmg)
        
        player_hp = player_data.get("hp", get_max_hp(player_data))
        player_hp -= enemy_dmg
        player_data["hp"] = max(0, player_hp)
        await save_player(user_id, player_data)
        
        result_text += f"😈 *{enemy['name']}* атакует и наносит *{enemy_dmg}* урона!\n"
        
        if player_hp <= 0:
            result_text += f"\n💀 *ТЫ ПОВЕРЖЕН!*\nВосстановлен в таверне за 15% золота."
            player_data["hp"] = get_max_hp(player_data)
            player_data["gold"] = max(300, int(player_data.get("gold", 0) * 0.85))
            await save_player(user_id, player_data)
        
        # Обновляем текст
        player_data["hp"] = player_hp
        text = result_text + "\n" + get_player_stats_text(player_data)
        text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy_hp)}"
        
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== ЛЕЧЕНИЕ =====
    elif data == "heal":
        cost = 45
        gold = player_data.get("gold", 0)
        max_hp = get_max_hp(player_data)
        current_hp = player_data.get("hp", max_hp)
        
        if gold >= cost and current_hp < max_hp:
            heal_amount = 48
            new_hp = min(max_hp, current_hp + heal_amount)
            player_data["hp"] = new_hp
            player_data["gold"] = gold - cost
            await save_player(user_id, player_data)
            
            text = f"💚 Восстановлено *{heal_amount}* HP! -{cost}💰\n\n"
            text += get_player_stats_text(player_data)
            text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy_hp)}"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            error = "❌ Не хватает золота или HP полное!"
            text = error + "\n\n" + get_player_stats_text(player_data)
            text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy_hp)}"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== ЗАТОЧКА ОРУЖИЯ =====
    elif data == "upgrade":
        upgrade_level = player_data.get("weapon_upgrade", 0)
        if upgrade_level >= 12:
            await query.edit_message_text("🔨 Оружие уже заточено до +12! Максимум.", reply_markup=get_back_keyboard())
            return
        
        cost = 300 + upgrade_level * 120
        gold = player_data.get("gold", 0)
        
        if gold < cost:
            await query.edit_message_text(f"❌ Не хватает {cost} золота для заточки!", reply_markup=get_back_keyboard())
            return
        
        chance = max(0.3, 0.85 - upgrade_level * 0.045)
        
        if random.random() < chance:
            player_data["weapon_upgrade"] = upgrade_level + 1
            player_data["gold"] = gold - cost
            await save_player(user_id, player_data)
            text = f"✅ *УСПЕХ!* Оружие +{upgrade_level + 1} (урон +{(upgrade_level + 1) * 5})\n\n"
            text += get_player_stats_text(player_data)
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            lost = int(cost * 0.5)
            player_data["gold"] = gold - lost
            await save_player(user_id, player_data)
            text = f"💥 *ПРОВАЛ ЗАТОЧКИ!* Потеряно {lost} золота. Оружие не сломалось.\n\n"
            text += get_player_stats_text(player_data)
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== СМЕНА ВРАГА =====
    elif data == "next_enemy":
        new_idx = (battle["enemy_idx"] + 1) % len(ENEMIES)
        new_enemy = ENEMIES[new_idx]
        battle["enemy_idx"] = new_idx
        battle["enemy_hp"] = new_enemy["hp"]
        active_battles[user_id] = battle
        
        text = f"🌀 Новый противник!\n\n"
        text += get_player_stats_text(player_data)
        text += f"\n\n*Твой противник:*\n{get_enemy_text(new_enemy, new_enemy['hp'])}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== МАГАЗИН =====
    elif data == "shop":
        text = "*🏪 ОРУЖЕЙНАЯ МАСТЕРА*\n\n"
        text += get_player_stats_text(player_data)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_shop_keyboard())
    
    elif data.startswith("buy_"):
        weapon_idx = int(data.split("_")[1])
        weapon = WEAPONS[weapon_idx]
        current_idx = WEAPONS.index(next((w for w in WEAPONS if w["name"] == player_data.get("weapon_name", "")), WEAPONS[0]))
        
        if weapon_idx <= current_idx:
            await query.answer("❌ Это оружие слабее или такое же!", show_alert=True)
            return
        
        if player_data.get("gold", 0) >= weapon["cost"]:
            player_data["gold"] -= weapon["cost"]
            player_data["weapon_name"] = weapon["name"]
            player_data["weapon_dmg"] = weapon["dmg"]
            await save_player(user_id, player_data)
            text = f"✅ Куплено: *{weapon['name']}* +{weapon['dmg']} урона!\n\n"
            text += get_player_stats_text(player_data)
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_shop_keyboard())
        else:
            await query.answer("❌ Не хватает золота!", show_alert=True)
    
    # ===== ТАЛАНТЫ =====
    elif data == "talents":
        text = f"*⭐ ДРЕВО ТАЛАНТОВ*\nОчков: {player_data.get('talent_points', 0)}\n\n"
        text += f"💪 СИЛА: +{player_data.get('talent_dmg', 0) * 4} урона\n"
        text += f"🎯 МЕТКОСТЬ: +{player_data.get('talent_crit', 0) * 2.5:.0f}% крита\n"
        text += f"❤️ ЖИВУЧЕСТЬ: +{player_data.get('talent_hp', 0) * 5}% HP\n\n"
        text += get_player_stats_text(player_data)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_talents_keyboard())
    
    elif data.startswith("talent_"):
        talent_type = data.split("_")[1]
        points = player_data.get("talent_points", 0)
        
        if points <= 0:
            await query.answer("❌ Нет очков талантов!", show_alert=True)
            return
        
        if talent_type == "dmg":
            player_data["talent_dmg"] = player_data.get("talent_dmg", 0) + 1
        elif talent_type == "crit":
            player_data["talent_crit"] = player_data.get("talent_crit", 0) + 1
        elif talent_type == "hp":
            player_data["talent_hp"] = player_data.get("talent_hp", 0) + 1
        
        player_data["talent_points"] = points - 1
        await save_player(user_id, player_data)
        
        text = f"✅ Талант улучшен!\n\n"
        text += get_player_stats_text(player_data)
        text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy_hp)}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== СТАТЫ =====
    elif data == "stats":
        text = get_player_stats_text(player_data)
        text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy_hp)}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== ТОП ИГРОКОВ =====
    elif data == "top":
        response = supabase.table("players").select("name, glory, level, gold").order("glory", desc=True).limit(10).execute()
        text = "*🏆 ТОП-10 ПО СЛАВЕ 🏆*\n\n"
        for i, p in enumerate(response.data):
            text += f"{i+1}. {p.get('name', 'Unknown')} — ✨{p.get('glory', 0)} | Ур.{p.get('level', 1)} | 🪙{p.get('gold', 0)}\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())
    
    # ===== НАЗАД =====
    elif data == "back":
        text = get_player_stats_text(player_data)
        text += f"\n\n*Твой противник:*\n{get_enemy_text(enemy, enemy_hp)}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# ========== ЗАПУСК БОТА ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🎮 Бот запущен! Найди его в Telegram: @")
    app.run_polling()

if __name__ == "__main__":
    main()
