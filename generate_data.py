import csv
import random

pune_places = [
    ("Shaniwar Wada", 18.5195, 73.8553, "fort", "historical"),
    ("Aga Khan Palace", 18.5535, 73.9010, "palace", "historical"),
    ("Sinhagad Fort", 18.3663, 73.7559, "fort", "forts"),
    ("Pataleshwar Cave Temple", 18.5294, 73.8507, "cave", "historical"),
    ("Raja Dinkar Kelkar Museum", 18.5122, 73.8567, "museum", "historical"),
    ("Dagdusheth Halwai Ganpati Temple", 18.5185, 73.8567, "temple", "religious"),
    ("Parvati Hill Temple", 18.4966, 73.8521, "hill", "spiritual"),
    ("Pashan Lake", 18.5403, 73.7866, "lake", "nature"),
    ("Okayama Friendship Garden", 18.5091, 73.8270, "garden", "nature"),
    ("Empress Botanical Garden", 18.4988, 73.8944, "garden", "nature"),
    ("National War Memorial", 18.5167, 73.8943, "memorial", "historical"),
    ("Shinde Chhatri", 18.4881, 73.8875, "memorial", "historical"),
    ("Khadakwasla Dam", 18.4573, 73.7664, "dam", "nature"),
    ("Peacock Bay", 18.4608, 73.7765, "viewpoint", "nature"),
    ("Bund Garden", 18.5419, 73.8936, "park", "nature"),
    ("Osho Teerth Park", 18.5389, 73.9080, "park", "nature"),
    ("Vetal Tekdi", 18.5349, 73.8049, "trek", "nature"),
    ("Paragliding at Kamshet", 18.7588, 73.4703, "adventure", "adventure"),
    ("Lavasa", 18.4056, 73.5060, "lakeside", "city"),
    ("Rajiv Gandhi Zoological Park", 18.4570, 73.8652, "zoo", "nature"),
    ("ISKCON NVCC Temple", 18.4577, 73.8650, "temple", "religious"),
    ("Balewadi High Street", 18.5925, 73.7518, "shopping", "city"),
    ("Koregaon Park", 18.5366, 73.9008, "cafes", "city"),
    ("FC Road", 18.5222, 73.8416, "shopping", "city"),
    ("JM Road", 18.5235, 73.8473, "shopping", "city"),
    ("Vishrambaug Wada", 18.5164, 73.8545, "wada", "historical"),
    ("Khunya Murlidhar Temple", 18.5163, 73.8582, "temple", "religious"),
    ("Chatushringi Temple", 18.5437, 73.8295, "temple", "religious"),
    ("Baner Pashan Biodiversity Park", 18.5589, 73.7927, "park", "nature"),
    ("Blades of Glory Cricket Museum", 18.5044, 73.8290, "museum", "sports"),
    ("Shivneri Fort", 19.1977, 73.8541, "fort", "forts"),
    ("Lonavala Tiger Point", 18.7714, 73.4120, "viewpoint", "mountains"),
    ("Bhushi Dam", 18.7575, 73.4118, "dam", "nature"),
    ("Karla Caves", 18.7452, 73.4723, "caves", "historical"),
    ("Bedse Caves", 18.7192, 73.5448, "caves", "historical"),
    ("Pawna Lake", 18.6500, 73.5000, "lake", "camping"),
    ("Mulshi Lake and Dam", 18.5371, 73.4087, "lake", "nature"),
    ("Bhandardara", 19.5417, 73.7450, "waterfall", "nature"),
    ("Lal Mahal", 18.5196, 73.8561, "palace", "historical"),
    ("Tribal Museum Pune", 18.5286, 73.8478, "museum", "cultural"),
    ("Saras Baug", 18.4960, 73.8580, "garden", "nature"),
    ("Kamala Nehru Park", 18.5092, 73.8274, "park", "nature"),
    ("Sambhaji Park", 18.5286, 73.8432, "park", "nature"),
    ("Pune Railway Museum", 18.5286, 73.8770, "museum", "historical"),
    ("Omkareshwar Temple", 18.5294, 73.8507, "temple", "religious"),
    ("Taljai Hill", 18.4815, 73.8573, "hill", "nature"),
    ("Hanuman Tekdi", 18.5042, 73.8345, "hill", "spiritual"),
    ("Katraj Snake Park", 18.4346, 73.8593, "wildlife", "nature"),
    ("Katraj Lake", 18.4362, 73.8617, "lake", "nature"),
    ("Pune War Cemetery", 18.5299, 73.8812, "memorial", "historical"),
    ("Ohel David Synagogue", 18.5254, 73.8855, "synagogue", "historical"),
    ("Amanora Mall", 18.5550, 73.9288, "mall", "shopping"),
    ("Phoenix Marketcity", 18.5598, 73.9050, "mall", "shopping"),
    ("Seasons Mall", 18.4614, 73.8634, "mall", "shopping"),
    ("Westend Mall", 18.5219, 73.8395, "mall", "shopping"),
    ("Kalyani Nagar", 18.5504, 73.9200, "street food", "food"),
    ("Mandai Market", 18.5167, 73.8554, "market", "shopping"),
    ("Imagica Theme Park", 18.7639, 73.2614, "amusement", "adventure"),
    ("Della Adventure Park", 18.7602, 73.4089, "adventure", "adventure"),
    ("Fergusson College", 18.5212, 73.8396, "education", "historical"),
    ("College of Engineering Pune", 18.5300, 73.8476, "education", "historical"),
    ("Pune University", 18.5590, 73.8085, "university", "historical"),
    ("National Film Archive", 18.5282, 73.8398, "archive", "cultural"),
    ("Kasba Ganpati Temple", 18.5196, 73.8574, "temple", "religious"),
    ("Kesari Wada", 18.5178, 73.8544, "wada", "historical"),
    ("Deccan Gymkhana", 18.5239, 73.8402, "heritage", "historical"),
    ("Chaturshringi Wildlife", 18.5590, 73.8075, "wildlife", "nature"),
    ("Pashan Tekdi", 18.5450, 73.7900, "trek", "nature"),
    ("Pune Cantonment", 18.5136, 73.8816, "cantonment", "historical"),
    ("Wet N Joy Water Park", 18.7236, 73.4147, "water park", "adventure"),
    ("Xthrill Water Park", 18.7247, 73.5200, "water park", "adventure"),
    ("Appu Ghar Pune", 18.6500, 73.7500, "amusement", "family"),
    ("Panshet Dam", 18.3840, 73.6140, "dam", "nature"),
    ("Varasgaon Dam", 18.3900, 73.6000, "dam", "nature"),
    ("Temghar Dam", 18.4500, 73.5700, "dam", "nature"),
    ("Neelkantheshwar", 18.4000, 73.5900, "temple", "spiritual"),
    ("Torna Fort", 18.2700, 73.6200, "fort", "adventure"),
    ("Rajgad Fort", 18.2400, 73.6800, "fort", "adventure"),
    ("Tikona Fort", 18.6300, 73.5100, "fort", "adventure"),
    ("Lohagad Fort", 18.7000, 73.4800, "fort", "adventure"),
    ("Visapur Fort", 18.7100, 73.4900, "fort", "adventure"),
    ("Korigad Fort", 18.6200, 73.3800, "fort", "adventure"),
    ("Tung Fort", 18.6500, 73.4500, "fort", "adventure"),
    ("Purandar Fort", 18.2800, 73.9700, "fort", "adventure"),
    ("Rohida Fort", 18.1500, 73.8200, "fort", "adventure"),
    ("Bhuleshwar Temple", 18.4200, 74.1500, "temple", "spiritual"),
    ("Ranjangaon Mahaganpati", 18.7500, 74.2400, "temple", "spiritual"),
    ("Theur Chintamani", 18.5200, 74.0500, "temple", "spiritual"),
    ("Morgaon Mayureshwar", 18.2700, 74.3200, "temple", "spiritual"),
    ("Lenyadri Girijatmaj", 19.2300, 73.8800, "temple", "spiritual"),
    ("Ozar Vighnahar", 19.1800, 73.9500, "temple", "spiritual"),
    ("BAPS Shri Swaminarayan Mandir", 18.4400, 73.8300, "temple", "spiritual"),
    ("Ekvira Aai Temple", 18.7500, 73.4700, "temple", "spiritual"),
    ("Prati Shirdi Shirgaon", 18.6900, 73.6800, "temple", "spiritual"),
    ("Dehu Gatha Mandir", 18.7100, 73.7600, "temple", "spiritual"),
    ("Alandi", 18.6700, 73.8900, "temple", "spiritual"),
    ("Ramdara Temple", 18.4400, 74.0200, "temple", "spiritual"),
    ("Bopdev Ghat", 18.3900, 73.8900, "viewpoint", "nature"),
    ("Dive Ghat", 18.4200, 73.9900, "viewpoint", "nature"),
    ("Mastani Mahal", 18.4200, 73.9950, "palace", "historical")
]

places_csv_path = "data/places.csv"
peak_hours_csv_path = "data/peak_hours_nearby.csv"
reviews_csv_path = "data/reviews.csv"

# Write places.csv
with open(places_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["city", "state", "place_name", "latitude", "longitude", "description_keyword", "activity_type", "rating"])
    for p in pune_places:
        rating = round(random.uniform(4.0, 4.8), 1)
        writer.writerow(["Pune", "Maharashtra", p[0], p[1], p[2], p[3], p[4], rating])

# Write peak_hours_nearby.csv
with open(peak_hours_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["place", "best_time", "avoid_time", "peak_season", "average_crowd", "nearby_attractions"])
    times = ["Morning (8-11 AM)", "Early Morning (6-9 AM)", "Evening (5-8 PM)", "Afternoon (1-4 PM)"]
    seasons = ["Oct-Mar", "Jul-Sep", "All Year", "Nov-Feb"]
    crowds = ["Low", "Medium", "High", "Very High"]
    for p in pune_places:
        bt = random.choice(times)
        at = random.choice(times)
        while at == bt: at = random.choice(times)
        ps = random.choice(seasons)
        ac = random.choice(crowds)
        na = "Local Markets, Scenic Viewpoints"
        writer.writerow([p[0], bt, at, ps, ac, na])

# Write reviews.csv
names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharv", "Ananya", "Diya", "Navya", "Kavya", "Myra", "Saanvi", "Aadya", "Aarohi", "Zara"]
comments = [
    "Amazing place to visit with family.",
    "Very peaceful and well maintained.",
    "A bit crowded on weekends but worth it.",
    "Highly recommended for nature lovers.",
    "Beautiful architecture and history.",
    "Great spot for photography.",
    "Loved the serene environment.",
    "A must-visit when in Pune.",
    "Food nearby is excellent.",
    "Good place for a short weekend trip."
]

with open(reviews_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["place", "user_name", "rating", "comment", "date"])
    for p in pune_places:
        uname = random.choice(names)
        rating = random.randint(3, 5)
        comment = random.choice(comments)
        date = f"2025-{random.randint(6, 12):02d}-{random.randint(1, 28):02d} {random.randint(9, 18):02d}:{random.randint(10, 50):02d}:00"
        writer.writerow([p[0], uname, rating, comment, date])

print("Generated exactly 100 entries for Pune across all 3 CSVs.")
