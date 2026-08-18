import sqlite3



def import_sentences():
    conn = sqlite3.connect("GRAMMO.db")
    cursor = conn.cursor()

    with open("sentences.txt", "r", encoding="utf-8") as file:
        for line in file:
            line1 = line.strip()

            if not line1:
                continue  # Пропустить пустые строки

            level, sentence = line1.split("|", 1)   

            cursor.execute("INSERT INTO sentences (sentence, level, topic, type) VALUES (?, ?, ?, ?)", (sentence, int(level), "base", 0))



    conn.commit()
    conn.close()



import_sentences()
