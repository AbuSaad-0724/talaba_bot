
import sqlite3
import datetime
import pytz

def get_now():
    return datetime.datetime.now(pytz.timezone('Asia/Tashkent')).isoformat()

def populate_library():
    # Use DB_PATH from config if possible, or direct string
    try:
        from config import DB_PATH
    except ImportError:
        DB_PATH = 'talaba_superbot.db'
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Sample Data
    materials = [
        # --- OLIY MATEMATIKA ---
        ('Matematika', 'Boshlang\'ich', 'video', 'Arifmetika asoslari (Video Dars)', '45 min', 'https://www.youtube.com/watch?v=example1', 'Sonlar, amallar va arifmetika asoslari.', 0),
        ('Matematika', 'Boshlang\'ich', 'pdf', 'Algebra: 7-sinf darsligi', '160 bet', 'https://n.ziyouz.com/books/darsliklar/7-sinf/Algebra%20(Sh.Alimov%20v.b.).pdf', 'Maktab o\'quvchilari uchun algebra darsligi.', 5*1024*1024),
        ('Matematika', 'O\'rta', 'pdf', 'Geometriya masalalar to\'plami', '200 bet', 'https://n.ziyouz.com/books/darsliklar/8-sinf/Geometriya%20(A.Pogorelov).pdf', 'Planimetriya bo\'yicha masalalar.', 8*1024*1024),
        ('Matematika', 'O\'rta', 'video', 'Trigonometriya asoslari', '55 min', 'https://www.youtube.com/watch?v=example2', 'Sinus, kosinus va tangens funksiyalari.', 0),
        ('Matematika', 'Yuqori', 'pdf', 'Oliy Matematika: I qism', '350 bet', 'https://n.ziyouz.com/books/kollej_va_litseylar/Oliy%20matematika%20(Yo.Soatov).pdf', 'Universitet talabalari uchun oliy matematika.', 12*1024*1024),
        ('Matematika', 'Yuqori', 'video', 'Matematik Analiz: Integrallar', '1 soat 20 min', 'https://www.youtube.com/watch?v=example3', 'Aniq va aniqmas integrallar bo\'yicha ma\'ruza.', 0),
        
        # --- FIZIKA ---
        ('Fizika', 'Boshlang\'ich', 'pdf', 'Fizika: 6-sinf darsligi', '140 bet', 'https://n.ziyouz.com/books/darsliklar/6-sinf/Fizika%20(P.Habibullayev).pdf', 'Fizika faniga kirish.', 4*1024*1024),
        ('Fizika', 'Boshlang\'ich', 'video', 'Mexanika qonunlari', '40 min', 'https://www.youtube.com/watch?v=phys1', 'Nyuton qonunlari va harakat.', 0),
        ('Fizika', 'O\'rta', 'pdf', 'Elektr va Magnetizm', '220 bet', 'https://n.ziyouz.com/books/darsliklar/8-sinf/Fizika%20(P.Habibullayev).pdf', 'Elektr maydon va magnit hodisalari.', 7*1024*1024),
        ('Fizika', 'Yuqori', 'pdf', 'Nazariy Fizika Asoslari', '400 bet', 'https://library.ziyonet.uz/uploads/books/2432/5345345.pdf', 'Kvant mexanikasi va nisbiylik nazariyasi.', 15*1024*1024),
        ('Fizika', 'Yuqori', 'video', 'Termodinamika', '1 soat', 'https://www.youtube.com/watch?v=phys2', 'Issiqlik va energiya almashinuvi.', 0),

        # --- INGLIZ TILI ---
        ('Ingliz tili', 'A1-A2', 'pdf', 'Essential Grammar in Use', '300 bet', 'https://example.com/murphy1.pdf', 'Raymond Murphy - Qizil kitob (Elementary).', 20*1024*1024),
        ('Ingliz tili', 'A1-A2', 'audio', 'Elementary Podcast Series', '25 min', 'https://example.com/podcast1.mp3', 'Ingliz tilini endi boshlovchilar uchun audiolar.', 10*1024*1024),
        ('Ingliz tili', 'B1-B2', 'pdf', 'English Grammar in Use', '350 bet', 'https://example.com/murphy2.pdf', 'Raymond Murphy - Ko\'k kitob (Intermediate).', 22*1024*1024),
        ('Ingliz tili', 'B1-B2', 'video', 'IELTS Speaking Tips', '15 min', 'https://youtube.com/ielts_tips', 'IELTS Speaking imtihonidan yuqori ball olish sirlari.', 0),
        ('Ingliz tili', 'C1-C2', 'pdf', 'Advanced Vocabulary List', '50 bet', 'https://example.com/adv_vocab.pdf', 'Yuqori darajadagi so\'zlar to\'plami.', 2*1024*1024),
        ('Ingliz tili', 'C1-C2', 'audio', 'BBC Learning English Drama', '45 min', 'https://example.com/drama.mp3', 'Murakkab dialoglar va hikoyalar.', 15*1024*1024),

        # --- RUS TILI ---
        ('Rus tili', 'Boshlang\'ich', 'pdf', 'Rus tili grammatikasi', '120 bet', 'https://example.com/rus_gram.pdf', 'O\'zbeklar uchun rus tili qo\'llanmasi.', 5*1024*1024),
        ('Rus tili', 'O\'rta', 'video', 'Rus tilida so\'zlashamiz', '30 min', 'https://youtube.com/rus_speak', 'Kundalik muloqot uchun video darslar.', 0),
        ('Rus tili', 'Yuqori', 'pdf', 'Rus Adabiyoti: Pushkin She\'rlari', '180 bet', 'https://example.com/pushkin.pdf', 'Klassik rus adabiyoti namunalari.', 6*1024*1024),

        # --- TARIX ---
        ('Tarix', 'Qadimgi', 'pdf', 'O\'zbekiston Tarixi (Eng qadimgi davr)', '250 bet', 'https://n.ziyouz.com/books/tarix/O\'zbekiston%20tarixi%20(1-kitob).pdf', 'Tosh davridan temir davrigacha.', 10*1024*1024),
        ('Tarix', 'O\'rta asrlar', 'video', 'Amir Temur saltanati', '1 soat', 'https://youtube.com/temur_doc', 'Amir Temur hayoti va yurishlari haqida hujjatli film.', 0),
        ('Tarix', 'Yangi davr', 'pdf', 'Jahon Tarixi: XIX-XX asrlar', '320 bet', 'https://n.ziyouz.com/books/darsliklar/10-sinf/Jahon%20tarixi.pdf', 'Sanoat inqilobi va jahon urushlari.', 12*1024*1024),

        # --- KIMYO ---
        ('Kimyo', 'Boshlang\'ich', 'pdf', 'Kimyo: 7-sinf', '130 bet', 'https://n.ziyouz.com/books/darsliklar/7-sinf/Kimyo.pdf', 'Kimyo faniga kirish, elementlar davriy jadvali.', 5*1024*1024),
        ('Kimyo', 'O\'rta', 'video', 'Organik Kimyo Reaksiyalari', '45 min', 'https://youtube.com/org_chem', 'Organik moddalar va ularning xossalari.', 0),
        ('Kimyo', 'Yuqori', 'pdf', 'Analitik Kimyo', '420 bet', 'https://example.com/analitik_kimyo.pdf', 'Moddalarni tahlil qilish usullari.', 18*1024*1024),

        # --- BIOLOGIYA ---
        ('Biologiya', 'Boshlang\'ich', 'pdf', 'Botanika: 5-sinf', '110 bet', 'https://n.ziyouz.com/books/darsliklar/5-sinf/Biologiya.pdf', 'O\'simliklar dunyosi.', 4*1024*1024),
        ('Biologiya', 'O\'rta', 'pdf', 'Odam Anatomiyasi', '280 bet', 'https://n.ziyouz.com/books/darsliklar/8-sinf/Odam%20va%20uning%20salomatligi.pdf', 'Inson tana tuzilishi va organlari.', 9*1024*1024),
        ('Biologiya', 'Yuqori', 'video', 'Genetika Asoslari', '50 min', 'https://youtube.com/genetics', 'DNK, irsiyat va o\'zgaruvchanlik.', 0),
        
        # --- DASTURLASH ---
        ('Dasturlash', 'Boshlang\'ich', 'video', 'Python: 0 dan boshlab', '2 soat', 'https://youtube.com/python_zero', 'Dasturlash muhitini o\'rnatish va ilk kod.', 0),
        ('Dasturlash', 'O\'rta', 'pdf', 'Algoritmlar (Grokking Algorithms)', '250 bet', 'https://example.com/grokking_algos.pdf', 'Algoritmlarni sodda tilda tushunish.', 8*1024*1024),
        ('Dasturlash', 'Yuqori', 'pdf', 'Clean Code (Toza Kod)', '400 bet', 'https://example.com/clean_code.pdf', 'Robert Martin - Professional darajada kod yozish.', 15*1024*1024)
    ]
    
    now = get_now()
    for m in materials:
        c.execute("""
            INSERT INTO library_materials (
                subject, level, material_type, title, duration, file_url, description, file_size, created_at, updated_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], now, now, 0))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(materials)} ta kutubxona materiali qo'shildi.")

if __name__ == "__main__":
    populate_library()
