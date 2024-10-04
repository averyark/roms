# @fileName: database.py
# @creation_date: 23/09/2024
# @authors: averyark

from typing import Optional, List
from icecream import ic
import sqlite3
from pydantic import BaseModel, Field

db_path = "mock-database.db"
db = sqlite3.connect(db_path)
db_cursor = db.cursor()

# TODO: Switch to SQLAlchemy

class UserData(BaseModel):
    # Shared
    user_id: int

    # Stored in Credentials
    hashed_password: str

    # Stored in UserSessionTokens
    session_tokens: List[str] = Field(default_factory=list)

    # Stored in UserData
    email: str
    first_name: str
    last_name: str
    birthday: str
    permission_level: int

    def commit(self):
        db_cursor.execute(
            f'''
                SELECT token FROM UserSessionTokens
                WHERE user_id = ?
            ''', (self.user_id,)
        )

        in_db_session_tokens = [row[0] for row in db_cursor.fetchall()]

        # Prepare lists for tokens to add and remove
        add_session_tokens = []
        remove_session_tokens = []

        # Identify tokens to add
        for token in self.session_tokens:
            if token not in in_db_session_tokens:
                add_session_tokens.append((self.user_id, token))

        # Identify tokens to remove
        for token in in_db_session_tokens:
            if token not in self.session_tokens:
                remove_session_tokens.append((self.user_id, token))

        # Insert new tokens
        if add_session_tokens:
            db_cursor.executemany(
                '''
                INSERT INTO UserSessionTokens (user_id, token)
                VALUES (?, ?)
                ''', add_session_tokens
            )

        # Remove old tokens
        if remove_session_tokens:
            db_cursor.executemany(
                '''
                DELETE FROM UserSessionTokens
                WHERE user_id = ? AND token = ?
                ''', remove_session_tokens
            )

        db_cursor.execute(
            f'''
                UPDATE Credentials
                    SET password = '{self.hashed_password}'
                WHERE user_id = {self.user_id}
            '''
        )

        columns = [field for field in self.model_fields.keys() if field != 'user_id' and field != 'hashed_password' and field != 'session_tokens']
        values = [getattr(self, field) for field in columns]

        set_clause = ", ".join([f"{col} = ?" for col in columns])

        query = f"UPDATE Userdata SET {set_clause} WHERE user_id = ?"

        ic(query)

        db_cursor.execute(query, values + [self.user_id])
        db.commit()

def get_user_data_in_dict(user_id: int):

    dict = {
        "user_id": user_id,
        "session_tokens": []
    }

    db_cursor.execute(
        f'''
            SELECT token FROM UserSessionTokens
            WHERE user_id IS {user_id}
        '''
    )

    for token in db_cursor.fetchall():
        dict["session_tokens"].append(token[0])

    db_cursor.execute(
        f'''
            SELECT password FROM Credentials
            WHERE user_id IS {user_id}
        '''
    )

    dict["hashed_password"] = db_cursor.fetchone()[0]

    db_cursor.execute(
        f'''
            SELECT
                email,
                first_name,
                last_name,
                birthday,
                permission_level
            FROM Userdata
            WHERE user_id IS {user_id}
        '''
    )
    userdata = db_cursor.fetchone()
    names = [description[0] for description in db_cursor.description]

    for index in range(0, len(names)):
        dict[names[index]] = userdata[index]

    return dict
