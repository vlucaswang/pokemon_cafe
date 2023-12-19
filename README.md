# Pokemon Cafe Spot Checking

This script check the free spot on Pokemon Cafe reservation site and send notifications.

I assume the script is running under Mac OSX, please change according to your environment.

## Steps

### 1.If the chrome webdriver needs to update, please run the following:

```bash
CHROME_VER=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  | grep -oE '\d+\.\d+\.\d+\.\d+')
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VER/mac-x64/chromedriver-mac-x64.zip
unzip chromedriver-mac-x64.zip
mv chromedriver-mac-x64/chromedriver .
```

### 2.Create Python Virtual Environment

```bash
python -m venv pokemon_cafe
source pokemon_cafe/bin/activate
pip install -r requirements.txt
```

### 3.Run the script

```bash
export MG_API_KEY=YOUR_MG_API_KEY
python pokemon_cafe_check.py
```

### 4.Enjoy