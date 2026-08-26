QUESTION_TEMPLATE = """Sen teknik bir değerlendirme uzmanısın. Aşağıdaki iş ilanı için {count} adet yetkinlik sorusu üret.

Pozisyon: {title}
Aranan beceriler: {skills}
Beklenen deneyim: {experience_years} yıl

Kurallar:
- Sorular yalnızca yukarıdaki becerileri ölçmelidir
- Her soru tek bir konuya odaklanmalıdır
- Deneyim yılına uygun zorlukta olmalıdır
- Sorular Türkçe olmalıdır
- Adaydan kısa ve teknik bir cevap beklenmelidir

Yanıtını yalnızca JSON dizisi olarak ver, başka hiçbir metin ekleme:
["soru 1", "soru 2", ...]"""


EVALUATION_TEMPLATE = """Sen teknik bir değerlendirme uzmanısın. Aşağıdaki yetkinlik sorusuna verilen cevabı değerlendir.

Soru: {question}
Cevap: {answer}

Kurallar:
- Cevabın teknik doğruluğunu değerlendir, yazım veya üslup değil
- Eksik ama doğru cevaplar kısmi puan alabilir
- Konuyla ilgisiz veya yanlış cevaplar 0 puan alır
- Boş veya anlamsız cevaplar 0 puan alır

Yanıtını yalnızca JSON nesnesi olarak ver, başka hiçbir metin ekleme:
{{"is_correct": true, "score": 100, "feedback": "kısa gerekçe"}}

score alanı 0 ile 100 arasında bir tam sayıdır."""