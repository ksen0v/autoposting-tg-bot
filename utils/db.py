import asyncio
import sqlite3
from datetime import datetime, timedelta

from utils.logger import logger

database_path = 'bot_database.db'


async def init_db() -> None:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # USER TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        registration_date TEXT DEFAULT (DATETIME('now', 'localtime')),
        balance REAL DEFAULT 0.0,
        active_posts INTEGER DEFAULT 0,
        invited_by INTEGER DEFAULT NULL,
        publications_count INTEGER DEFAULT 0, 
        is_blocked INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        FOREIGN KEY (invited_by) REFERENCES users(user_id)
    )
    ''')

    # POSTS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_posts (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_post TEXT,
        user_id INTEGER,
        post_text TEXT,
        chat_id TEXT,
        add_time INTEGER,
        next_post_time TEXT,
        is_active INTEGER DEFAULT 1,
        data_created TEXT DEFAULT (DATETIME('now', 'localtime')),
        expiry_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    # REFERRALS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
        inviter_id INTEGER,
        join_date TEXT DEFAULT (DATETIME('now', 'localtime')),
        earned_amount REAL DEFAULT 0.0,
        FOREIGN KEY (inviter_id) REFERENCES users(user_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS publication_history (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id_default INTEGER,
        user_id INTEGER,
        post_time TEXT DEFAULT (DATETIME('now', 'localtime')))
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting TEXT UNIQUE,
        value INTEGER)
        ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topup_history (
        topup_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        user_id INTEGER,
        amount INTEGER,
        topup_time TEXT DEFAULT (DATETIME('now', 'localtime')))
        ''')

    conn.commit()
    conn.close()


async def add_topup_history(invoice_id, user_id, amount):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO topup_history (invoice_id, user_id, amount)
            VALUES (?, ?, ?)
            ''', (invoice_id, user_id, amount))

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f'Do not add topup history for {invoice_id}: {e}')
    finally:
        conn.close()


async def register_user(user_id, username, invited_by=None) -> bool:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # ADD NEW USER
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, invited_by)
        VALUES (?, ?, ?)
        ''', (user_id, username, invited_by))

        is_status = False

        if not invited_by and not await is_exist_user(user_id):
            cursor.execute('''
            INSERT OR IGNORE INTO referrals (referral_id, inviter_id)
            VALUES(?, ?)
            ''', (user_id, None))
            logger.info(f"Create new referrals table for new user: {user_id}")
            is_status = True
        elif invited_by and await add_new_referral(invited_by, user_id, conn, cursor):
            logger.info(f"Add new referral: {invited_by} invite {user_id}")
            is_status = True
        else:
            logger.info(f"Not add new referral: {invited_by} try invite {user_id}")
            is_status = False

        conn.commit()
        return is_status
    except Exception as e:
        logger.error(f"Error registering user: {e}")
    finally:
        conn.close()


async def add_new_referral(inviter_user_id, referral_user_id, conn, cursor) -> bool:
    try:
        # Check that the inviter does not invite himself
        if inviter_user_id == referral_user_id:
            return False

        # Check that both users is exist
        cursor.execute('SELECT 1 FROM users WHERE user_id IN (?, ?)', (inviter_user_id, referral_user_id))
        if len(cursor.fetchall()) != 2:
            return False

        # Add item to referrals table
        cursor.execute('''
        INSERT INTO referrals (referral_id, inviter_id, join_date)
        VALUES (?, ?, date('now'))
        ''', (referral_user_id, inviter_user_id))

        # Update item to users table
        cursor.execute('''
        UPDATE users
        SET invited_by = ?
        WHERE user_id = ?
        ''', (inviter_user_id, referral_user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Not add referrals: {e}")
        return False
    finally:
        conn.close()


async def get_profile_info(user_id) -> tuple:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT user_id, username, balance, active_posts, registration_date, invited_by
        FROM users WHERE user_id = ?
        ''', (user_id,))

        return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f'Do not get profile info for {user_id}: {e}')
    finally:
        conn.close()


async def get_username(user_id) -> str:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT username
        FROM users WHERE user_id = ?
        ''', (user_id,))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get username {user_id}: {e}')
    finally:
        conn.close()


async def get_referrals_list(user_id) -> list[dict]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT
            u.username,
            r.join_date
        FROM referrals r
        LEFT JOIN users u ON r.referral_id = u.user_id
        WHERE r.inviter_id = ?
        ORDER BY r.join_date DESC
        ''', (user_id,))

        columns = [column[0] for column in cursor.description]
        referrals = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return referrals
    except sqlite3.Error as e:
        logger.error(f"Error getting referrals list: {e}")
    finally:
        conn.close()


async def get_referral_info(user_id) -> tuple:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                SELECT COUNT(*) FROM referrals 
                WHERE inviter_id = ?
                ''', (user_id,))
        result = cursor.fetchone()
        total_refs = result[0] if result else '0'

        cursor.execute('''
        SELECT earned_amount FROM referrals
        WHERE referral_id = ?
        ''', (user_id,))
        earned_amount = cursor.fetchone()[0]

        return total_refs, earned_amount
    except sqlite3.Error as e:
        logger.error(f'Do not get referral info for {user_id}: {e}')
    finally:
        conn.close()


async def is_exist_user(user_id) -> bool:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT 1 FROM users WHERE user_id = ?
        ''', (user_id,))

        if cursor.fetchone():
            return True
        return False
    except sqlite3.Error as e:
        logger.error(f'Do not get is_exist for {user_id}: {e}')
    finally:
        conn.close()


async def add_user_balance(user_id, amount) -> bool:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE users SET balance = balance + ? WHERE user_id = ?
        ''', (amount, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set user balance for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def get_user_invited_by(user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT invited_by FROM users WHERE user_id = ?
        ''', (user_id,))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get user inviter for {user_id}: {e}')
    finally:
        conn.close()


async def get_posts_list(user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT post_id, post_text, chat_id, add_time, is_active, type_post, next_post_time
        FROM user_posts WHERE user_id = ?
        ''', (user_id,))

        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f'Do not get user posts list for {user_id}: {e}')
    finally:
        conn.close()


async def add_post(user_id, post_text, chat_id, add_time, is_active=True, type_post='no_link', expiry_date_days=30) -> bool:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    expiry_date = (datetime.now() + timedelta(days=expiry_date_days)).strftime('%Y-%m-%d %H:%M:%S')
    next_post_time = (datetime.now() + timedelta(minutes=add_time)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute('''
        INSERT INTO user_posts (user_id, post_text, chat_id, add_time, is_active, type_post, expiry_date, next_post_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, post_text, chat_id, add_time, is_active, type_post, expiry_date, next_post_time))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not add post to posts list for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def delete_post(post_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        DELETE FROM user_posts WHERE post_id = ?
        ''', (post_id,))

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f'Do not delete post {post_id}: {e}')
    finally:
        conn.close()


async def get_post(post_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT post_text, chat_id, add_time, is_active, type_post, expiry_date, next_post_time
        FROM user_posts WHERE post_id = ?
        ''', (post_id,))

        return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Do not get post id={post_id}: {e}")
    finally:
        conn.close()


async def get_type_post(post_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT type_post
        FROM user_posts WHERE post_id = ?
        ''', (post_id,))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get type post for {post_id}: {e}')
    finally:
        conn.close()


async def edit_post_text(post_id, post_text):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE user_posts 
            SET post_text = ? WHERE post_id = ?
            ''', (post_text, post_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not edit post text for {post_id}: {e}')
        return False
    finally:
        conn.close()


async def remove_post(post_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                DELETE FROM user_posts WHERE post_id = ?
                ''', (post_id,))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not remove post for {post_id}: {e}')
        return False
    finally:
        conn.close()


async def get_balance(user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                    SELECT balance FROM users WHERE user_id = ?
                    ''', (user_id,))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get user balance for {user_id}: {e}')
    finally:
        conn.close()


async def remove_balance(user_id, amount):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                        UPDATE users SET balance = balance - ? WHERE user_id = ?
                        ''', (amount, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set user balance for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def get_expired_posts(time_now):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                SELECT post_id, user_id FROM user_posts 
                WHERE is_active = 1 AND expiry_date < ?
            ''', (time_now,))

        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f'Do not get expired posts: {e}')
    finally:
        conn.close()


async def set_is_active_post(post_id, is_active = 0):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                    UPDATE user_posts SET is_active = ? 
                    WHERE post_id = ?
                ''', (is_active, post_id))

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f'Do not set is_active for post {post_id}: {e}')
    finally:
        conn.close()


async def get_post_for_publication(time_now):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                        SELECT post_text, chat_id, post_id, user_id, add_time FROM user_posts 
                        WHERE next_post_time <= ? AND is_active = 1
                    ''', (time_now,))

        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f'Do not get posts for publication for time {time_now}: {e}')
    finally:
        conn.close()


async def set_next_post_time(next_time, post_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                            UPDATE user_posts
                            SET next_post_time = ? WHERE post_id = ?
                        ''', (next_time, post_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not get posts for publication for time {next_time}: {e}')
        return False
    finally:
        conn.close()


async def add_earned_amount(user_id, amount):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                            UPDATE referrals
                            SET earned_amount = earned_amount + ? WHERE referral_id = ?
                        ''', (amount, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set earned amount for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def get_active_posts(user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT active_posts
        FROM users WHERE user_id = ?
        ''', (user_id,))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get active posts count for {user_id}: {e}')
    finally:
        conn.close()


async def add_active_posts(user_id, count=1):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE users
        SET active_posts = active_posts + ? WHERE user_id = ?
        ''', (count, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not add active posts count for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def remove_active_posts(user_id, count=1):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE users
        SET active_posts = active_posts - ? WHERE user_id = ?
        ''', (count, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not remove active posts count for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def add_publication_history(post_id, user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO publication_history (post_id_default, user_id)
        VALUES (?, ?)
        ''', (post_id, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not add publication history for {post_id}: {e}')
        return False
    finally:
        conn.close()


async def set_settings():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT OR IGNORE INTO settings (setting, value)
        VALUES (?, ?)
        ''', ('published_posts_count', 0))

        cursor.execute('''
        INSERT OR IGNORE INTO settings (setting, value)
        VALUES (?, ?)
        ''', ('posting_countdown', 30))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set default settings: {e}')
        return False
    finally:
        conn.close()


async def set_countdown(countdown):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE settings
        SET value = ? WHERE setting = ?
        ''', ( countdown, 'posting_countdown'))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set default settings: {e}')
        return False
    finally:
        conn.close()


async def set_admin(user_id, flag):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE users
        SET is_admin = ? WHERE user_id = ?
        ''', (flag, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set admin {user_id}: {e}')
        return False
    finally:
        conn.close()


async def get_is_admin(user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT is_admin 
        FROM users WHERE user_id = ?
        ''', (user_id,))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get is_admin for {user_id}: {e}')
    finally:
        conn.close()


async def get_all_is_admin():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT user_id 
        FROM users WHERE is_admin = 1
        ''')
        admin_ids = [admin_id[0] for admin_id in cursor.fetchall()]

        return admin_ids
    except sqlite3.Error as e:
        logger.error(f'Do not get all admins: {e}')
    finally:
        conn.close()


async def get_publication_history():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT post_id, post_id_default, user_id, post_time
        FROM publication_history
        ''')

        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f'Do not get all admins: {e}')
    finally:
        conn.close()


async def get_countdown():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT value 
        FROM settings WHERE setting = ?
        ''', ('posting_countdown',))

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get countdown: {e}')
    finally:
        conn.close()


async def set_is_blocked(user_id, flag):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        UPDATE users 
        SET is_blocked = ? WHERE user_id = ?
        ''', (flag, user_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f'Do not set is_blocked(flag={flag}) for {user_id}: {e}')
        return False
    finally:
        conn.close()


async def get_all_is_blocked():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT user_id 
        FROM users WHERE is_blocked = 1
        ''')
        is_blocked_ids = [user_id[0] for user_id in cursor.fetchall()]

        return is_blocked_ids
    except sqlite3.Error as e:
        logger.error(f'Do not get all is_blocked: {e}')
    finally:
        conn.close()


async def get_all_user_ids():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT user_id FROM users WHERE is_blocked = 0 AND is_admin = 0
        ''')
        user_ids = [user_id[0] for user_id in cursor.fetchall()]

        return user_ids
    except sqlite3.Error as e:
        logger.error(f'Do not get all user_id: {e}')
    finally:
        conn.close()


async def get_posts_count_all():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT COUNT(*)
        FROM publication_history 
        ''')

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get posts count for current month: {e}')
    finally:
        conn.close()


async def get_posts_count_current_month():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT COUNT(*)
        FROM publication_history 
        WHERE strftime('%Y-%m', post_time) = strftime('%Y-%m', 'now', 'localtime')
        ''')

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get posts count for current month: {e}')
    finally:
        conn.close()


async def get_all_users_count():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT COUNT(*)
        FROM users 
        ''')

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get posts count for current month: {e}')
    finally:
        conn.close()


async def get_all_earned_amount():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT amount
            FROM topup_history
            ''')
        amount_formatted = [int(amount[0]) for amount in cursor.fetchall()]

        return sum(amount_formatted)
    except sqlite3.Error as e:
        logger.error(f'Do not get all earned amount for current month: {e}')
    finally:
        conn.close()


async def get_month_earned_amount():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                SELECT amount
                FROM topup_history
                WHERE strftime('%Y-%m', topup_time) = strftime('%Y-%m', 'now', 'localtime')
                ''')
        amount_formatted = [int(amount[0]) for amount in cursor.fetchall()]

        return sum(amount_formatted)
    except sqlite3.Error as e:
        logger.error(f'Do not get all earned amount for current month: {e}')
    finally:
        conn.close()


async def get_posts_count_current_day():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT COUNT(*)
        FROM publication_history 
        WHERE strftime('%Y-%m-%d', post_time) = strftime('%Y-%m-%d', 'now', 'localtime')
                    ''')

        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f'Do not get posts count for current day: {e}')
    finally:
        conn.close()


async def get_day_earned_amount():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
                SELECT amount
                FROM topup_history
                WHERE strftime('%Y-%m-%d', topup_time) = strftime('%Y-%m-%d', 'now', 'localtime')
                ''')
        amount_formatted = [int(amount[0]) for amount in cursor.fetchall()]

        return sum(amount_formatted)
    except sqlite3.Error as e:
        logger.error(f'Do not get earned amount for current day: {e}')
    finally:
        conn.close()