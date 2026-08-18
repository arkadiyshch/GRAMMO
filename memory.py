from collections import defaultdict, defaultdict
from typing import Dict, List

user_contexts: Dict[int, List[str]] = defaultdict(list)

def get_user_messages(user_id: int):
    return user_contexts[user_id]


def add_user_message(user_id: int, role: str, content : str):
    user_contexts[user_id].append({"role": role, "content": content})

    if len(user_contexts[user_id]) > 15:
        user_contexts[user_id]=user_contexts[user_id][-15]

def clear_user_messages(user_id: int):
    user_contexts[user_id] = [] 
