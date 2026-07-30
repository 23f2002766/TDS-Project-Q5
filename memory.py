# Chat history
chat_memory = {}

# Last uploaded file
last_uploaded_file = {}


def add_message(chat_id, role, content):
    if chat_id not in chat_memory:
        chat_memory[chat_id] = []

    chat_memory[chat_id].append({
        "role": role,
        "content": content
    })


def get_history(chat_id):
    return chat_memory.get(chat_id, [])


def set_last_file(chat_id, file_path):
    last_uploaded_file[chat_id] = file_path


def get_last_file(chat_id):
    return last_uploaded_file.get(chat_id)