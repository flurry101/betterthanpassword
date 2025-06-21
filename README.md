## BetterThanPassword - yet another password strength checker

> built by someone who also reuses passwords. occasionally.


A Chrome extension + Flask backend for checking password strength in real time. 
Built mostly to find out: *"how hard can building a browser extension be?"* 
Turns out, not too bad.

## What it does
- You type a password. 
- It sends input to a local Flask server
- Server:
   - Does some basic analysis (entropy-ish) 
   - Checks if a password has been compromised in a data breach.
      - It uses a k-anonymity model via the Have I Been Pwned API.
      - Only the first 5 characters of the SHA-1 hash are sent — your password stays private.
- You get instant feedback on how weak (or strong) your password is. 
That's... it.

#### Why I made this
Was tired of  if my passwords were trash and also after reading (again) about how weak passwords are still a leading cause of security breaches. So, wanted to mess with chrome extensions and decided to build something that answers with a slightly more scientific "probably".. and Flask felt lightweight enough to glue stuff together. So I built this and learned stuff. Still don’t trust passwords D: 
Now it lives in this repo.

## Setup Instructions
1. Install python dependencies:
   ```bash
   pip install flask flask-cors
   ```

2. Load the extension:
   - open chrome and go to `chrome://extensions/`
   - enable "Developer mode"
   - click "Load unpacked" and select this folder

3. Start the flask server:
   ```bash
   python server.py
   ```

4. Use the extension:
Click the extension icon in Chrome. Type a password. See what happens.

## Note 
This is a dev version running on http://localhost:5000.
No data is sent anywhere else. No logging either. 
(Don’t push this live unless you like dealing with cors, real security implications or the fact that this was built in a day as a hobby.) 
