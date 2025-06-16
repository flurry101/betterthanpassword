## BetterThanPassword - yet another password strength checker

> built by someone who also reuses passwords. occasionally.


A Chrome extension + Flask backend for checking password strength in real time. 
Built mostly to find out: *"how hard can building a browser extension be?"* 
(answer: not that hard but maybe messy enough to learn something)

### What it does
- You type a password. 
- It sends input to a local Flask server
- Server does some basic analysis (entropy-ish) 
- You get instant feedback on how weak (or strong) your password is. 
- That's... it.

#### Why I made this
Was tired of  if my passwords were trash and also after I read about how weak passwords are still a leading cause of security breaches. So, wanted to mess with chrome extensions and decided to build something that answers with a slightly more scientific "probably".. and Flask felt simple. So I built this. Learned stuff. Still don’t trust passwords D: Now it lives in this repo.

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
No data is sent anywhere else. 
(don’t push this live unless you like dealing with cors and this half-baked logic) 
- want to make it worse? use eval() :D, hardcode you passwords, disable CORS recklessly, and definitely log everything!



