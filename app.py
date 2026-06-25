"""
Hyderabad Yatra — Smart Travel in Hyderabad
A full-stack Flask application with login system
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
app.secret_key = 'hyderabad_yatra_secret_key_2025'
DATABASE = 'travel_guide.db'

# ─── HARDCODED USER CREDENTIALS ─────────────────────────
USERS = {
    'prasanna': 'prasanna@20'
}

# ─── DATABASE HELPERS ────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * 6371 * asin(sqrt(a))

# ─── AUTH ROUTES ─────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ─── DATABASE INITIALIZATION ────────────────────────────
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT NOT NULL,
            description TEXT, history TEXT, address TEXT,
            latitude REAL, longitude REAL,
            opening_time TEXT, closing_time TEXT, entry_fee TEXT,
            best_time TEXT, tips TEXT, rating REAL DEFAULT 4.0,
            image_url TEXT, special_events TEXT
        );
        CREATE TABLE IF NOT EXISTS food_places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, cuisine TEXT, specialty TEXT,
            address TEXT, latitude REAL, longitude REAL,
            price_range TEXT, rating REAL DEFAULT 4.0,
            veg_nonveg TEXT, image_url TEXT
        );
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT, address TEXT,
            latitude REAL, longitude REAL, price_per_night INTEGER,
            rating REAL DEFAULT 4.0, amenities TEXT,
            contact TEXT, image_url TEXT
        );
        CREATE TABLE IF NOT EXISTS bus_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_number TEXT, from_stop TEXT, to_stop TEXT,
            via TEXT, frequency TEXT, fare TEXT,
            first_bus TEXT, last_bus TEXT
        );
        CREATE TABLE IF NOT EXISTS budget_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT, duration TEXT,
            transport_cost INTEGER, food_cost INTEGER,
            accommodation_cost INTEGER, entry_fees INTEGER,
            total_cost INTEGER, description TEXT
        );
    ''')

    existing = cursor.execute("SELECT COUNT(*) FROM places").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    places_data = [
        ("Birla Mandir", "temple",
         "A stunning white marble temple dedicated to Lord Venkateswara, situated on a 280-ft high hillock called Naubath Pahad.",
         "Built in 1976 by the Birla Foundation using 2000 tons of white Rajasthani marble. It took 10 years to complete.",
         "Hill Fort Road, Naubath Pahad", 17.4062, 78.4691,
         "7:00 AM", "12:00 PM & 2:00 PM - 9:00 PM", "Free",
         "Evening for stunning city views", "Remove footwear before entering. Photography not allowed inside.",
         4.5, "https://images.unsplash.com/photo-1622546758596-f1f06ba11f58?w=600",
         "Maha Shivaratri, Vaikuntha Ekadashi"),

        ("Chilkur Balaji Temple", "temple",
         "Known as the 'Visa Balaji Temple', famous for granting visa wishes. One of the oldest temples in Hyderabad.",
         "Dating back to 500 years, this temple is unique as it doesn't accept money offerings (Hundi).",
         "Chilkur, Near Osman Sagar", 17.3616, 78.3437,
         "5:00 AM", "8:00 PM", "Free",
         "Early morning to avoid crowds", "No money offerings accepted. Be prepared for long queues on weekends.",
         4.6, "https://images.unsplash.com/photo-1609947017136-9dba43341569?w=600",
         "Brahmotsavam in March, Sri Rama Navami"),

        ("Jagannath Temple", "temple",
         "A beautiful temple dedicated to Lord Jagannath, Balabhadra, and Subhadra, built in the Kalinga style.",
         "Built in 2004, this is a replica of the famous Jagannath Temple in Puri, Odisha.",
         "Road No. 12, Banjara Hills", 17.4156, 78.4412,
         "5:00 AM", "9:00 PM", "Free",
         "During Rath Yatra festival", "Grand Rath Yatra is celebrated every year.",
         4.4, "https://images.unsplash.com/photo-1609947017136-9dba43341569?w=600",
         "Rath Yatra (June/July), Snana Yatra"),

        ("Peddamma Temple", "temple",
         "One of the most popular goddess temples in Hyderabad, dedicated to Goddess Peddamma.",
         "This temple has been a significant spiritual center for decades. The annual Bonalu festival here attracts millions.",
         "Jubilee Hills, Road No. 45", 17.4289, 78.4107,
         "5:30 AM", "9:00 PM", "Free",
         "During Bonalu festival (July/August)", "Very crowded during Bonalu. Wear comfortable clothes.",
         4.3, "https://images.unsplash.com/photo-1609947017136-9dba43341569?w=600",
         "Bonalu Festival (July/August)"),

        ("Mecca Masjid", "temple",
         "One of the oldest and largest mosques in India, and one of the iconic landmarks of Hyderabad.",
         "Construction began in 1617 under Muhammad Quli Qutb Shah and was completed in 1694 by Aurangzeb.",
         "Near Charminar, Old City", 17.3604, 78.4736,
         "4:00 AM", "9:30 PM", "Free",
         "Early morning or late afternoon", "Dress modestly. Non-Muslims can visit outside prayer times.",
         4.5, "https://images.unsplash.com/photo-1585155784229-aff921ccfa10?w=600",
         "Eid ul-Fitr, Eid ul-Adha, Shab-e-Meraj"),

        ("Charminar", "attraction",
         "The iconic monument and mosque built in 1591, symbolizing Hyderabad. A masterpiece of Indo-Islamic architecture.",
         "Built by Muhammad Quli Qutb Shah in 1591 to commemorate the elimination of plague.",
         "Charminar Road, Old City", 17.3616, 78.4747,
         "9:30 AM", "5:30 PM", "₹25 (Indians), ₹300 (Foreigners)",
         "Early morning for photography", "Visit the surrounding Laad Bazaar for bangles.",
         4.7, "https://images.unsplash.com/photo-1603813507806-0cf9689cbbe4?w=600",
         "Illuminated during festivals"),

        ("Golconda Fort", "attraction",
         "A magnificent medieval fortress known for its acoustic design, palaces, and ingenious water supply system.",
         "Originally a mud fort built by the Kakatiya dynasty in the 13th century, later expanded by the Qutb Shahi dynasty.",
         "Ibrahim Bagh, Hyderabad", 17.3833, 78.4011,
         "8:00 AM", "5:30 PM", "₹15 (Indians), ₹200 (Foreigners)",
         "Morning; Evening Sound & Light Show", "Carry water. Wear comfortable shoes for climbing.",
         4.6, "https://images.unsplash.com/photo-1590766940554-634855926788?w=600",
         "Sound & Light Show daily at 6:30 PM"),

        ("Salar Jung Museum", "attraction",
         "One of India's three National Museums and the largest one-man collection of antiques in the world.",
         "Houses the art collection of Salar Jung III from Japan, China, India, Persia, Egypt, Europe, and North America.",
         "Salar Jung Road, Darulshifa", 17.3713, 78.4804,
         "10:00 AM", "5:00 PM (Closed Fridays)", "₹20 (Indians), ₹500 (Foreigners)",
         "Weekday mornings", "The Veiled Rebecca sculpture and Musical Clock are must-see.",
         4.5, "https://images.unsplash.com/photo-1564399580075-5dfe19c205f0?w=600",
         "Special exhibitions periodically"),

        ("Ramoji Film City", "attraction",
         "The world's largest integrated film studio complex, certified by Guinness World Records.",
         "Spread over 1666 acres, built by Ramoji Rao in 1996. Over 100 sets depicting locations worldwide.",
         "Anaspur Village, Hayathnagar", 17.2543, 78.6808,
         "9:00 AM", "5:30 PM", "₹1500 (Adults), ₹1200 (Children)",
         "Full day visit recommended", "Book online for discounts. Wear comfortable shoes.",
         4.4, "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600",
         "Special packages during holidays"),

        ("Hussain Sagar Lake", "attraction",
         "A heart-shaped lake with a massive 16m tall monolithic Buddha statue in the center.",
         "Built by Ibrahim Quli Qutb Shah in 1563. The Buddha statue weighing 350 tons was erected in 1992.",
         "Tank Bund Road", 17.4239, 78.4738,
         "Open 24 hours", "Boating: 8 AM - 9 PM", "Boating: ₹75 - ₹300",
         "Evening for sunset views", "Take a boat ride to Buddha statue. Visit Lumbini Park nearby.",
         4.3, "https://images.unsplash.com/photo-1590766940554-634855926788?w=600",
         "Laser show at Lumbini Park every evening"),

        ("Chowmahalla Palace", "attraction",
         "The stunning palace of the Nizams of Hyderabad, meaning 'Four Palaces'.",
         "Built during the Nizam era (18th-19th century), served as the official residence of the Nizams.",
         "Motigalli, Khilwat", 17.3581, 78.4718,
         "10:00 AM", "5:00 PM (Closed Fridays)", "₹80 (Indians), ₹200 (Foreigners)",
         "Morning for best photography", "Don't miss the Durbar Hall and vintage car collection.",
         4.5, "https://images.unsplash.com/photo-1564399580075-5dfe19c205f0?w=600",
         "Cultural events during heritage week"),

        ("Nehru Zoological Park", "attraction",
         "One of India's largest zoos spread over 380 acres, home to 1500+ species.",
         "Established in 1963, features natural habitat enclosures, safari park, butterfly park, and toy train.",
         "Bahadurpura, Near Mir Alam Tank", 17.3352, 78.4519,
         "8:30 AM", "5:00 PM (Closed Mondays)", "₹40 (Adults), ₹20 (Children)",
         "Morning hours, especially in winter", "Take the safari ride. Plan for 3-4 hours.",
         4.2, "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=600",
         "Lion Safari, Bear Safari on weekends"),
    ]

    for p in places_data:
        cursor.execute('''INSERT INTO places
            (name, category, description, history, address, latitude, longitude,
             opening_time, closing_time, entry_fee, best_time, tips, rating, image_url, special_events)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', p)

    food_data = [
        ("Paradise Biryani", "Hyderabadi", "Hyderabadi Dum Biryani",
         "SD Road, Secunderabad", 17.4399, 78.4983, "₹₹", 4.5, "Non-Veg",
         "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600"),
        ("Bawarchi", "Hyderabadi", "Special Biryani & Kebabs",
         "RTC X Roads, Musheerabad", 17.4021, 78.4869, "₹₹", 4.3, "Non-Veg",
         "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600"),
        ("Shah Ghouse", "Hyderabadi", "Biryani, Haleem, Kebabs",
         "Tolichowki, Near Golconda", 17.3950, 78.4100, "₹₹", 4.4, "Non-Veg",
         "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600"),
        ("Chutneys", "South Indian", "Dosas, Idli, Uttapam",
         "Banjara Hills, Road No. 1", 17.4156, 78.4495, "₹₹", 4.4, "Veg",
         "https://images.unsplash.com/photo-1630383249896-424e482df921?w=600"),
        ("Rajdhani Thali", "Rajasthani/Gujarati", "Unlimited Thali",
         "GVK One Mall, Banjara Hills", 17.4237, 78.4483, "₹₹₹", 4.3, "Veg",
         "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600"),
        ("Nimrah Cafe", "Irani", "Irani Chai & Osmania Biscuits",
         "Near Charminar, Old City", 17.3611, 78.4740, "₹", 4.6, "Both",
         "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600"),
        ("Pista House", "Hyderabadi", "Haleem (seasonal), Biryani",
         "Engine Bowli, Old City", 17.3750, 78.4612, "₹₹", 4.5, "Non-Veg",
         "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600"),
        ("MTR (Mavalli Tiffin Rooms)", "South Indian", "Filter Coffee, Rava Idli",
         "Inorbit Mall, Madhapur", 17.4359, 78.3877, "₹₹", 4.2, "Veg",
         "https://images.unsplash.com/photo-1630383249896-424e482df921?w=600"),
        ("AB's - Absolute Barbecues", "BBQ & Grill", "Live Grill Buffet",
         "Jubilee Hills, Road No. 36", 17.4306, 78.4131, "₹₹₹", 4.4, "Both",
         "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600"),
        ("Govind Dosa", "Street Food", "Cheese Dosa, Masala Dosa",
         "Gudimalkapur, Near Mehdipatnam", 17.3933, 78.4433, "₹", 4.3, "Veg",
         "https://images.unsplash.com/photo-1630383249896-424e482df921?w=600"),
    ]

    for f in food_data:
        cursor.execute('''INSERT INTO food_places
            (name, cuisine, specialty, address, latitude, longitude,
             price_range, rating, veg_nonveg, image_url)
            VALUES (?,?,?,?,?,?,?,?,?,?)''', f)

    hotels_data = [
        ("Taj Falaknuma Palace", "Luxury", "Engine Bowli, Falaknuma",
         17.3318, 78.4672, 25000, 4.8, "Heritage Palace, Pool, Spa, Restaurant",
         "+91-40-66298585", "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600"),
        ("ITC Kohenur", "Luxury", "HITEC City, Madhapur",
         17.4475, 78.3828, 12000, 4.7, "Pool, Spa, 6 Restaurants, Business Center",
         "+91-40-67676767", "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600"),
        ("Novotel Hyderabad", "Premium", "HITEC City, Madhapur",
         17.4453, 78.3810, 6000, 4.3, "Pool, Gym, Restaurant, Free WiFi",
         "+91-40-66824422", "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600"),
        ("Treebo Trend Maha", "Budget-Friendly", "Abids, Near Railway Station",
         17.3923, 78.4753, 1500, 3.8, "AC Rooms, Free WiFi, TV",
         "+91-40-44556677", "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600"),
        ("OYO Townhouse", "Budget", "Gachibowli",
         17.4401, 78.3489, 1200, 3.6, "AC, WiFi, Breakfast, Parking",
         "+91-9876543210", "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600"),
        ("FabHotel Prime", "Budget-Friendly", "Banjara Hills",
         17.4200, 78.4480, 1800, 3.9, "AC, WiFi, Restaurant, Parking",
         "+91-9988776655", "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600"),
        ("Taj Krishna", "Luxury", "Banjara Hills, Road No. 1",
         17.4180, 78.4500, 10000, 4.6, "Pool, Spa, 4 Restaurants, Banquet",
         "+91-40-66662323", "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600"),
        ("Lemon Tree Premier", "Mid-Range", "HITEC City",
         17.4470, 78.3835, 4500, 4.2, "Pool, Gym, Restaurant, Free WiFi",
         "+91-40-44404040", "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600"),
    ]

    for h in hotels_data:
        cursor.execute('''INSERT INTO hotels
            (name, category, address, latitude, longitude,
             price_per_night, rating, amenities, contact, image_url)
            VALUES (?,?,?,?,?,?,?,?,?,?)''', h)

    bus_data = [
        ("65", "Secunderabad", "Charminar", "Abids, Nampally", "Every 10 min", "₹10-30", "5:00 AM", "11:00 PM"),
        ("5K", "Secunderabad", "Golconda Fort", "Lakdikapul, Toli Chowki", "Every 15 min", "₹15-35", "5:30 AM", "10:30 PM"),
        ("86", "Mehdipatnam", "Charminar", "Shaikpet, Tolichowki", "Every 12 min", "₹10-25", "5:00 AM", "11:00 PM"),
        ("127", "MGBS", "Ramoji Film City", "Hayathnagar, Pedda Amberpet", "Every 30 min", "₹30-50", "6:00 AM", "9:00 PM"),
        ("10H", "Secunderabad", "Hussain Sagar", "Tank Bund, Necklace Road", "Every 10 min", "₹10-20", "5:30 AM", "10:30 PM"),
        ("49M", "Mehdipatnam", "HITEC City", "Gachibowli, Kondapur", "Every 8 min", "₹15-30", "5:00 AM", "11:30 PM"),
        ("290", "Secunderabad", "Nehru Zoo Park", "Nampally, Afzalgunj", "Every 20 min", "₹10-25", "5:30 AM", "10:00 PM"),
        ("216", "MGBS", "Chilkur Balaji", "Mehdipatnam, Himayat Sagar", "Every 45 min", "₹20-40", "6:00 AM", "8:00 PM"),
        ("47", "Secunderabad", "Jubilee Hills", "Ameerpet, Panjagutta", "Every 10 min", "₹10-25", "5:00 AM", "11:00 PM"),
        ("119", "MGBS", "Salar Jung Museum", "Afzalgunj", "Every 15 min", "₹10-20", "5:30 AM", "10:30 PM"),
    ]

    for b in bus_data:
        cursor.execute('''INSERT INTO bus_routes
            (route_number, from_stop, to_stop, via, frequency, fare, first_bus, last_bus)
            VALUES (?,?,?,?,?,?,?,?)''', b)

    budget_data = [
        ("Backpacker Special", "1 Day", 200, 500, 0, 100, 800,
         "Quick temple + Charminar tour with street food."),
        ("Budget Explorer", "2 Days", 500, 1200, 1500, 300, 3500,
         "Covers major temples, Charminar, Golconda Fort with affordable hotel."),
        ("Comfort Traveler", "3 Days", 1000, 2500, 6000, 500, 10000,
         "Comprehensive tour including Ramoji Film City with mid-range hotel."),
        ("Premium Experience", "3 Days", 2000, 5000, 15000, 1500, 23500,
         "Luxury experience covering all attractions, fine dining, and premium hotel."),
        ("Pilgrim Package", "2 Days", 400, 1000, 1200, 0, 2600,
         "Focused temple tour: Birla Mandir, Chilkur Balaji, Jagannath, Peddamma."),
    ]

    for b in budget_data:
        cursor.execute('''INSERT INTO budget_plans
            (plan_name, duration, transport_cost, food_cost,
             accommodation_cost, entry_fees, total_cost, description)
            VALUES (?,?,?,?,?,?,?,?)''', b)

    conn.commit()
    conn.close()
    print("✅ Database initialized with Hyderabad data!")

# ─── ROUTES ──────────────────────────────────────────────

@app.route('/')
def home():
    places = query_db("SELECT * FROM places ORDER BY rating DESC LIMIT 6")
    food = query_db("SELECT * FROM food_places ORDER BY rating DESC LIMIT 4")
    return render_template('index.html', places=places, food=food)

@app.route('/places')
def all_places():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    if category != 'all' and search:
        places = query_db("SELECT * FROM places WHERE category=? AND name LIKE ? ORDER BY rating DESC", (category, f'%{search}%'))
    elif category != 'all':
        places = query_db("SELECT * FROM places WHERE category=? ORDER BY rating DESC", (category,))
    elif search:
        places = query_db("SELECT * FROM places WHERE name LIKE ? ORDER BY rating DESC", (f'%{search}%',))
    else:
        places = query_db("SELECT * FROM places ORDER BY rating DESC")
    return render_template('places.html', places=places, category=category, search=search)

@app.route('/place/<int:place_id>')
def place_detail(place_id):
    place = query_db("SELECT * FROM places WHERE id=?", (place_id,), one=True)
    if not place:
        return "Place not found", 404
    nearby_food = []
    for f in query_db("SELECT * FROM food_places"):
        dist = haversine(place['latitude'], place['longitude'], f['latitude'], f['longitude'])
        if dist < 5:
            nf = dict(f)
            nf['distance'] = round(dist, 1)
            nearby_food.append(nf)
    nearby_food.sort(key=lambda x: x['distance'])
    bus_routes = query_db("SELECT * FROM bus_routes")
    return render_template('place_detail.html', place=place, nearby_food=nearby_food[:5], bus_routes=bus_routes)

@app.route('/food')
def food_places():
    cuisine = request.args.get('cuisine', 'all')
    diet = request.args.get('diet', 'all')
    query = "SELECT * FROM food_places WHERE 1=1"
    params = []
    if cuisine != 'all':
        query += " AND cuisine=?"
        params.append(cuisine)
    if diet != 'all':
        query += " AND veg_nonveg=?"
        params.append(diet)
    query += " ORDER BY rating DESC"
    food = query_db(query, params)
    cuisines = query_db("SELECT DISTINCT cuisine FROM food_places")
    return render_template('food.html', food=food, cuisines=cuisines, cuisine=cuisine, diet=diet)

@app.route('/hotels')
def hotels():
    budget = request.args.get('budget', 'all')
    if budget == 'budget':
        hotels_list = query_db("SELECT * FROM hotels WHERE price_per_night <= 2000 ORDER BY rating DESC")
    elif budget == 'mid':
        hotels_list = query_db("SELECT * FROM hotels WHERE price_per_night > 2000 AND price_per_night <= 7000 ORDER BY rating DESC")
    elif budget == 'luxury':
        hotels_list = query_db("SELECT * FROM hotels WHERE price_per_night > 7000 ORDER BY rating DESC")
    else:
        hotels_list = query_db("SELECT * FROM hotels ORDER BY rating DESC")
    return render_template('hotels.html', hotels=hotels_list, budget=budget)

@app.route('/transport')
def transport():
    search = request.args.get('search', '')
    if search:
        routes = query_db(
            "SELECT * FROM bus_routes WHERE from_stop LIKE ? OR to_stop LIKE ? OR via LIKE ? OR route_number LIKE ?",
            (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        routes = query_db("SELECT * FROM bus_routes")
    return render_template('transport.html', routes=routes, search=search)

@app.route('/budget')
def budget():
    plans = query_db("SELECT * FROM budget_plans ORDER BY total_cost ASC")
    return render_template('budget.html', plans=plans)

@app.route('/map')
def live_map():
    places = query_db("SELECT id, name, category, latitude, longitude, rating, address FROM places")
    food = query_db("SELECT id, name, latitude, longitude, rating, address FROM food_places")
    hotels_list = query_db("SELECT id, name, latitude, longitude, rating, address FROM hotels")
    return render_template('map.html', places=places, food=food, hotels=hotels_list)

# ─── API ENDPOINTS ───────────────────────────────────────

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json or {}
    interest = data.get('interest', 'all')
    budget_level = data.get('budget', 'medium')
    diet = data.get('diet', 'both')

    if interest == 'all':
        places = query_db("SELECT * FROM places ORDER BY rating DESC LIMIT 5")
    else:
        places = query_db("SELECT * FROM places WHERE category=? ORDER BY rating DESC LIMIT 5", (interest,))

    if diet == 'both':
        food = query_db("SELECT * FROM food_places ORDER BY rating DESC LIMIT 3")
    elif diet == 'veg':
        food = query_db("SELECT * FROM food_places WHERE veg_nonveg='Veg' OR veg_nonveg='Both' ORDER BY rating DESC LIMIT 3")
    else:
        food = query_db("SELECT * FROM food_places WHERE veg_nonveg='Non-Veg' OR veg_nonveg='Both' ORDER BY rating DESC LIMIT 3")

    if budget_level == 'low':
        hotels_list = query_db("SELECT * FROM hotels WHERE price_per_night <= 2000 ORDER BY rating DESC LIMIT 2")
    elif budget_level == 'high':
        hotels_list = query_db("SELECT * FROM hotels WHERE price_per_night > 7000 ORDER BY rating DESC LIMIT 2")
    else:
        hotels_list = query_db("SELECT * FROM hotels WHERE price_per_night > 2000 AND price_per_night <= 7000 ORDER BY rating DESC LIMIT 2")

    return jsonify({
        'places': [dict(p) for p in places],
        'food': [dict(f) for f in food],
        'hotels': [dict(h) for h in hotels_list]
    })

@app.route('/api/nearby', methods=['GET'])
def nearby():
    lat = float(request.args.get('lat', 17.385))
    lng = float(request.args.get('lng', 78.4867))
    radius = float(request.args.get('radius', 5))
    results = []
    for place in query_db("SELECT * FROM places"):
        dist = haversine(lat, lng, place['latitude'], place['longitude'])
        if dist <= radius:
            p = dict(place)
            p['distance'] = round(dist, 2)
            results.append(p)
    results.sort(key=lambda x: x['distance'])
    return jsonify(results)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
