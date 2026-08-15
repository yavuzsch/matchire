QUESTION_TEMPLATE = """Sen teknik bir mülakat uzmanısın. Aşağıdaki iş ilanı için {count} adet teknik mülakat sorusu üret.

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