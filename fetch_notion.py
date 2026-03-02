import urllib.request
import json
import re
import sys

urls = {
    "snow-support": "https://actually-hamster-aa2.notion.site/Snow-Record-User-Support-2fb5e95d9ec18059b7eeca6bb6e8edc0",
    "snow-privacy": "https://actually-hamster-aa2.notion.site/Snow-Record-Privacy-Policy-2f95e95d9ec180a795c2e7620227c213",
    "snow-terms": "https://actually-hamster-aa2.notion.site/Snow-Record-Terms-of-Service-2f95e95d9ec180c4848adb22faecef63",
    "ssak-terms": "https://actually-hamster-aa2.notion.site/SSAK-Photo-Cleaner-Terms-of-Use-3085e95d9ec180be81c7ed77c15ad967",
    "ssak-support": "https://actually-hamster-aa2.notion.site/SSAK-Photo-Cleaner-User-Support-3085e95d9ec18097a411c690806706a4",
    "ssak-privacy": "https://actually-hamster-aa2.notion.site/SSAK-Photo-Cleaner-Privacy-Policy-3085e95d9ec180958805c5f9b73f507e",
    "wayin-privacy": "https://actually-hamster-aa2.notion.site/Wayin-Korea-Privacy-Policy-30f5e95d9ec18022ae32db27838d3b8c",
    "wayin-terms": "https://actually-hamster-aa2.notion.site/Wayin-Korea-Terms-of-Service-30f5e95d9ec180808495f51eb35965e6"
}

def extract_text(block):
    if not block or "value" not in block:
        return ""
    
    val = block["value"]
    block_type = val.get("type", "")
    
    text = ""
    props = val.get("properties", {})
    if "title" in props:
        for t in props["title"]:
            if isinstance(t, list):
                text += t[0]
            elif isinstance(t, str):
                text += t
                
    if block_type == "header":
        return f"\n# {text}\n"
    elif block_type == "sub_header":
        return f"\n## {text}\n"
    elif block_type == "sub_sub_header":
        return f"\n### {text}\n"
    elif block_type == "bulleted_list":
        return f"- {text}"
    elif block_type == "numbered_list":
        return f"1. {text}"
    elif block_type == "text":
        return text if text else ""
    return text

for name, url in urls.items():
    print(f"Fetching {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        match = re.search(r'window\.__INITIAL_STATE__=({.+?});</script>', html)
        if match:
            state = json.loads(match.group(1))
            
            # Find the main page block ID
            page_blocks = state.get("recordMap", {}).get("block", {})
            
            # The blocks might not be perfectly ordered, but we can try to find the Root
            root_id = list(page_blocks.keys())[0]  # usually the first one is the page
            for k, v in page_blocks.items():
                if v.get('value', {}).get('type') == 'page':
                    root_id = k
                    break
            
            root_block = page_blocks.get(root_id, {}).get("value", {})
            content_ids = root_block.get('content', [])
            
            page_title = extract_text(page_blocks.get(root_id))
            
            output = f"# {page_title.strip() if page_title else name}\n\n"
            
            for content_id in content_ids:
                if content_id in page_blocks:
                    txt = extract_text(page_blocks[content_id])
                    if txt:
                        output += txt + "\n"
                        
            with open(f"{name}.txt", "w", encoding="utf-8") as f:
                f.write(output)
            print(f"[{name}] Saved {len(output)} chars.")
        else:
            print(f"[{name}] Could not find __INITIAL_STATE__")
            
    except Exception as e:
        print(f"Error fetching {name}: {e}")

