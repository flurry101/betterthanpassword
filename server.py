from flask import Flask, request, jsonify
from flask_cors import CORS
import re, os, json, secrets, base64, qrcode, subprocess, math, hashlib, requests, string, random, sys
from typing import Dict, List, Tuple
from io import BytesIO

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["chrome-extension://*", "http://localhost:*", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "supports_credentials": True
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/health')
def health_check(): 
    return jsonify({
        "status": "healthy",
        "version": "1.0"
    }), 200

COMMON_WORDS_FILE = "common_words.json"
if not os.path.exists(COMMON_WORDS_FILE):
    COMMON_WORDS = {
        "common_pswds": ["pswd", "123456", "qwerty", "letmein", "admin"],
        "common_names": ["john", "mike", "david", "chris", "peter", "ram", "singh", "michael", "jennifer", "thomas", "jessica", "joshua", "ashley", "matthew", "sarah", "andrew", "amanda", "daniel", "james", "robert", "emma", "william", "olivia", "alexander", "sophia", "ryan", "isabella", "jacob", "emily", "michael", "madison", "joshua", "abigail", "matthew", "olivia", "ethan", "emma", "andrew", "ava", "daniel", "mia", "anthony", "amelia", "christopher", "harper", "joshua", "evelyn", "andrew", "abigail", "dylan", "emily", "logan", "elizabeth"],
        "common_words": ["football", "baseball", "dragon", "master", "monkey", "login"],
        "companies": ["google", "facebook", "twitter", "apple", "microsoft", "amazon"],
        "indian_names": ["arjun", "rahul", "priya", "neha", "amit", "suresh", "deepak", "kumar", "rajesh", "sanjay", "anita", "meera", "sunita", "kavita", "pradeep", "vijay", "suresh", "ramesh", "mahesh", "dinesh", "anand", "rajiv", "sanjay", "vivek", "nitin", "pankaj", "manish", "sachin", "rohit", "virat", "dhoni", "kohli", "rohit", "bumrah", "pandya", "rahane", "pujara", "ashwin", "jadeja", "bumrah", "priyanka", "deepika", "katrina", "alia", "kareena", "aishwarya", "shahrukh", "amir", "salman", "hrithik"],
        "indian_cities": ["mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata", "pune", "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane", "bhopal", "visakhapatnam", "patna", "vadodara", "ghaziabad", "ludhiana", "agra", "nashik", "faridabad", "meerut", "rajkot", "varanasi", "srinagar", "aurangabad", "dhanbad", "amritsar", "noida", "ranchi", "howrah", "gwalior", "jodhpur", "coimbatore", "vijayawada", "jabalpur", "gurgaon", "guwahati"],
        "indian_brands": ["tata", "reliance", "infosys", "tcs", "wipro", "hdfc", "icici", "sbi", "airtel", "jio", "maruti", "mahindra", "bajaj", "hero", "tvs", "ashok", "hindustan", "unilever", "itc", "nestle", "amul", "parle", "britannia", "cadbury", "colgate", "dabur", "patanjali", "titan", "tanishq", "kalyan", "bigbazaar", "flipkart", "myntra", "snapdeal", "paytm", "ola", "swiggy", "zomato", "make my trip", "irctc"],
        "common_words": ["football", "baseball", "dragon", "master", "monkey", "login", "welcome", "princess", "qwerty", "abc123", "trustno1", "letmein", "dragon", "baseball", "iloveyou", "starwars", "sunshine", "princess", "admin", "welcome", "shadow", "ashley", "football", "michael", "mustang", "summer", "hunter", "freedom", "whatever", "qwerty", "baseball", "dragon", "master", "monkey", "letmein", "shadow", "ashley", "sunshine", "michael", "football", "iloveyou", "trustno1", "welcome", "monkey", "login", "abc123", "starwars", "123123", "dragon", "passw0rd", "master", "hello", "freedom", "whatever", "qazwsx", "michael", "football", "baseball", "welcome", "shadow", "ashley", "sunshine", "michael", "football", "iloveyou", "trustno1", "welcome", "monkey", "login", "abc123", "starwars", "123123", "dragon", "passw0rd", "master", "hello", "freedom", "whatever", "qazwsx", "michael", "football", "baseball", "welcome", "shadow", "ashley", "sunshine", "michael", "football", "iloveyou", "trustno1", "welcome", "monkey", "login", "abc123", "starwars", "123123", "dragon", "passw0rd", "master", "hello", "freedom", "whatever", "qazwsx", "michael", "football", "baseball", "welcome", "shadow", "ashley", "sunshine", "michael", "football", "iloveyou", "trustno1", "welcome", "monkey", "login", "abc123", "starwars", "123123", "dragon", "passw0rd", "master"],
    }
    with open(COMMON_WORDS_FILE, 'w') as f:
        json.dump(COMMON_WORDS, f)
else:
    with open(COMMON_WORDS_FILE, 'r') as f:
        COMMON_WORDS = json.load(f)

def explain_weakness(pswd: str) -> List[str]:
    explain = []    
    if len(pswd) < 8:
        explain.append("Too short! Even your pet could guess this 🐕")
    elif len(pswd) < 12:
        explain.append("A bit longer would be safer 📏")
    lower_pass = pswd.lower()
    for cat, words in COMMON_WORDS.items():
        for word in words:
            if word in lower_pass:
                if cat == "common_pswds":
                    explain.append(f"'{word}' is one of the most commonly used pswds 😱")
                elif cat == "common_names":
                    explain.append(f"Using names like '{word}' makes it easy to guess 👤")
                elif cat == "common_words":
                    explain.append(f"The word '{word}' appears in dictionary attacks 📚")
                elif cat == "companies":
                    explain.append(f"Company names like '{word}' are easy to guess 🏢")
                elif cat == "keyboard_patterns":
                    explain.append("Keyboard patterns are the first thing hackers try 🎹")
    if re.search(r'(.)\1{2,}', pswd):
        explain.append("Repeated characters make your pswd weaker 🔁")
    if re.search(r'(?:012|123|234|345|456|567|678|789)', pswd):
        explain.append("Sequential numbers are too obvious 1️⃣2️⃣3️⃣")
    if re.search(r'19\d{2}|20\d{2}', pswd):
        explain.append("Using years is risky - especially birth years 📅")
    if not re.search(r'[A-Z]', pswd):
        explain.append("Add some UPPERCASE letters for variety 🔠")
    if not re.search(r'[a-z]', pswd):
        explain.append("Add some lowercase letters for variety 📝")
    if not re.search(r'\d', pswd):
        explain.append("Numbers make your pswd stronger 🔢")
    if not re.search(r'[^A-Za-z0-9]', pswd):
        explain.append("Special characters add extra protection #@!")
    return explain

def analyze_pswd_strength(pswd: str) -> Dict:
    analysis = {
        "score": 0,
        "feedback": [],
        "patterns_found": [],
        "suggestions": [],
        "hibp_breaches": 0,
        "weaknesses": [],
        "user_friendly_score": "Weak",  
        "emoji_rating": "🔓"  
    }    
    analysis["weaknesses"] = explain_weakness(pswd)    
    if len(pswd) >= 12:
        analysis["score"] += 20
    else:
        analysis["feedback"].append(f"pswd should be at least 12 characters")
        analysis["suggestions"].append(f"Add {12 - len(pswd)} more characters")

    has_upper = bool(re.search(r'[A-Z]', pswd))
    has_lower = bool(re.search(r'[a-z]', pswd))
    has_digit = bool(re.search(r'\d', pswd))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', pswd))
    diversity_score = sum([has_upper, has_lower, has_digit, has_special]) * 10
    analysis["score"] += diversity_score
    entropy = calculate_entropy(pswd)
    entropy_score = min(40, entropy / 2)
    analysis["score"] += entropy_score
    analysis["entropy"] = entropy
    pwned_count = check_haveibeenpwned(pswd)
    analysis["hibp_breaches"] = pwned_count
    if pwned_count > 0:
        analysis["score"] -= min(30, pwned_count)
        analysis["weaknesses"].append(f"Found in {pwned_count} data breaches! 😱")
    analysis["score"] = max(0, min(100, analysis["score"]))    
    if analysis["score"] >= 80:
        analysis["user_friendly_score"] = "Super Strong"
        analysis["emoji_rating"] = "🔒"
    elif analysis["score"] >= 60:
        analysis["user_friendly_score"] = "Strong"
        analysis["emoji_rating"] = "🔐"
    elif analysis["score"] >= 40:
        analysis["user_friendly_score"] = "Good"
        analysis["emoji_rating"] = "🔑"
    elif analysis["score"] >= 20:
        analysis["user_friendly_score"] = "Could Be Better"
        analysis["emoji_rating"] = "⚠️"
    else:
        analysis["user_friendly_score"] = "Needs Work"
        analysis["emoji_rating"] = "🔓"
    return analysis

def calculate_entropy(pswd: str) -> float:
    char_counts = {}
    for char in pswd:
        char_counts[char] = char_counts.get(char, 0) + 1
    entropy = 0
    length = len(pswd)
    for count in char_counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    
    return entropy * len(pswd)

def check_haveibeenpwned(pswd: str) -> int:
    pswd_hash = hashlib.sha1(pswd.encode('utf-8')).hexdigest().upper()
    prefix,suffix = pswd_hash[:5],pswd_hash[5:]
    try:
        response = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            headers={'Add-Padding': 'true'},
            timeout=5
        )
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            for hash_suffix, count in hashes:
                if hash_suffix == suffix:
                    return int(count)
    except Exception as e:
        print(f"Error checking HaveIBeenPwned: {e}")
    return 0

def generate_pswd_suggestions(analysis: Dict) -> List[str]:
    suggestions = []    
    if analysis["score"] < 60:
        suggestions.extend([
            "Use a longer pswd (at least 12 characters)",
            "Mix uppercase and lowercase letters",
            "Add numbers and special characters",
            "Avoid common patterns and keyboard sequences"
        ])
    if analysis["patterns_found"]:
        suggestions.append("Avoid using common patterns like keyboard sequences or repeated characters")
    return suggestions

def generate_roast(analysis: Dict) -> str:
    roasts = {
        'weak': [
            "Did you fall asleep on your keyboard? 😴",
            "Even my grandma could guess this! 👵",
            "pswd123? More like Hackme123! 🎯",
            "Are you trying to get hacked? Because that's how you get hacked! 🎣",
            "This pswd is about as secure as a chocolate padlock! 🍫"
        ],
        'medium': [
            "Not terrible, but not winning any security awards either. 🥉",
            "Meh, I've seen better pswds in phishing emails. 🎣",
            "You're trying, and that's what counts... I guess. 🤷",
            "Almost secure... like a door with three locks but one is broken. 🚪"
        ],
        'strong': [
            "Okay showoff, we get it - you know what pswd hygiene is! 🔐",
            "Finally, a pswd that doesn't make me cry! 😌",
            "Your pswd game is stronger than my coffee! ☕",
            "This pswd is like Fort Knox... if Fort Knox had emojis! 🏰"
        ]
    }
    if analysis["score"] >= 80:
        cat = 'strong'
    elif analysis["score"] >= 40:
        cat = 'medium'
    else:
        cat = 'weak'
    return random.choice(roasts[cat])

def generate_badges(analysis: Dict) -> List[Dict]:
    badges = []    
    pswd_length = len(analysis.get("pswd", ""))
    if pswd_length >= 20:
        badges.append({
            "icon": "🏰",
            "name": "Fortress Master",
            "description": "Used 20+ characters",
            "rarity": "legendary"
        })
    elif pswd_length >= 16:
        badges.append({
            "icon": "🗼",
            "name": "Tower Builder", 
            "description": "Used 16+ characters",
            "rarity": "epic"
        })
    elif pswd_length >= 12:
        badges.append({
            "icon": "🏠",
            "name": "Solid Foundation",
            "description": "Used 12+ characters",
            "rarity": "rare"
        })

    entropy = analysis.get("entropy", 0)
    if entropy >= 80:
        badges.append({
            "icon": "⚡",
            "name": "Chaos Lord",
            "description": "Extremely high pswd entropy",
            "rarity": "legendary"
        })
    elif entropy >= 60:
        badges.append({
            "icon": "🌪️",
            "name": "Entropy Master",
            "description": "Very high pswd entropy",
            "rarity": "epic"
        })
    elif entropy >= 40:
        badges.append({
            "icon": "🎯",
            "name": "Entropy Adept",
            "description": "Good pswd entropy",
            "rarity": "rare"
        })

    char_types = sum([
        bool(re.search(r'[A-Z]', analysis.get("pswd", ""))),
        bool(re.search(r'[a-z]', analysis.get("pswd", ""))),
        bool(re.search(r'\d', analysis.get("pswd", ""))),
        bool(re.search(r'[^A-Za-z0-9]', analysis.get("pswd", "")))
    ])
    
    if char_types == 4:
        badges.append({
            "icon": "🎨",
            "name": "Character Artist",
            "description": "Perfect mix of all character types",
            "rarity": "epic"
        })
    elif char_types == 3:
        badges.append({
            "icon": "🔠",
            "name": "Mix Master",
            "description": "Good variety of character types",
            "rarity": "rare"
        })

    if analysis.get("hibp_breaches", 0) == 0:
        badges.append({
            "icon": "🛡️",
            "name": "Unbreakable",
            "description": "Not found in any known breaches",
            "rarity": "epic"
        })

    if not analysis.get("patterns_found"):
        badges.append({
            "icon": "🌟",
            "name": "Pattern Breaker",
            "description": "No predictable patterns detected",
            "rarity": "rare"
        })

    if pswd_length >= 16 and entropy >= 60 and char_types == 4 and not analysis.get("patterns_found"):
        badges.append({
            "icon": "👑",
            "name": "pswd Royalty",
            "description": "Achieved excellence in all security aspects",
            "rarity": "legendary"
        })
    return badges

def generate_passkey() -> Dict:
    passkey = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(passkey)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return {
        "passkey": passkey,
        "qr_code": qr_code
    }

def generate_memorable_pswd() -> str:
    adjectives = ["Happy", "Brave", "Clever", "Swift", "Bright"]
    nouns = ["Dragon", "River", "Mountain", "Forest", "Star"]
    special_chars = "!@#$%^&*"
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    number = str(random.randint(100, 999))
    special = random.choice(special_chars)
    return f"{adj}{special}{noun}{number}"

def generate_random_pswd(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Custom password generator
import string

def generate_custom_pswd(custom_word, use_lowercase, use_uppercase, use_numbers, use_symbols, length):
    charsets = ''
    if use_lowercase:
        charsets += string.ascii_lowercase
    if use_uppercase:
        charsets += string.ascii_uppercase
    if use_numbers:
        charsets += string.digits
    if use_symbols:
        charsets += string.punctuation
    if not charsets:
        charsets = string.ascii_letters
    # Ensure custom_word fits
    if len(custom_word) > length:
        custom_word = custom_word[:length]
    remaining_len = length - len(custom_word)
    if remaining_len < 0:
        remaining_len = 0
    random_part = ''.join(secrets.choice(charsets) for _ in range(remaining_len))
    # Place custom_word at a random position
    import random
    insert_at = random.randint(0, remaining_len) if custom_word else 0
    pswd = random_part[:insert_at] + custom_word + random_part[insert_at:]
    return pswd

@app.route('/check_pswd', methods=['POST', 'OPTIONS'])
def check_pswd():
    if request.method == 'OPTIONS':
        return '', 204  
    try:
        data = request.get_json()
        if not data or 'pswd' not in data:
            return jsonify({"error": "No pswd provided"}), 400
        pswd = data.get('pswd', '')
        analysis = analyze_pswd_strength(pswd)
        analysis["pswd"] = pswd
        analysis["roast"] = generate_roast(analysis)
        analysis["badges"] = generate_badges(analysis)
        del analysis["pswd"]
        return jsonify(analysis)     
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_pswd', methods=['POST', 'OPTIONS']) 
def generate_pswd():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        pswd_type = data.get('type', 'random')
        
        if pswd_type == 'passkey':
            return jsonify(generate_passkey())
        elif pswd_type == 'memorable':
            return jsonify({
                "pswd": generate_memorable_pswd()
            })
        elif pswd_type == 'custom':
            # Custom password generation
            custom_word = data.get('custom_word', '')
            use_lowercase = data.get('use_lowercase', True)
            use_uppercase = data.get('use_uppercase', True)
            use_numbers = data.get('use_numbers', True)
            use_symbols = data.get('use_symbols', True)
            length = data.get('length', 16)
            pswd = generate_custom_pswd(custom_word, use_lowercase, use_uppercase, use_numbers, use_symbols, length)
            return jsonify({"pswd": pswd})
        else:  # random
            length = data.get('length', 16)
            return jsonify({
                "pswd": generate_random_pswd(length)
            })
    except Exception as e:
        print(f"pswd generation error: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

def install_requirements():
    required_packages = ['flask-cors', 'qrcode', 'pillow', 'requests']
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *required_packages])
        print("Successfully installed required packages!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    try:
        print("checking and installing required packages...")
        if not install_requirements():
            print("warning: some packages might be missing", file=sys.stderr)
        print("\nstarting server on http://localhost:5000")
        app.run(
            host='localhost',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except Exception as e:
        print(f"Failed to start server: {str(e)}", file=sys.stderr)
