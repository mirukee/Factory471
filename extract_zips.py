import zipfile, os, io

out_dir = 'd:/factory471/notion_exports'
os.makedirs(out_dir, exist_ok=True)

zips = [f for f in os.listdir('d:/factory471') if f.endswith('.zip')]
for outer_name in sorted(zips):
    outer_path = f'd:/factory471/{outer_name}'
    print(f"Opening outer: {outer_name}")
    with zipfile.ZipFile(outer_path) as outer:
        for inner_name in outer.namelist():
            print(f"  Inner zip: {inner_name}")
            if inner_name.endswith('.zip'):
                inner_data = outer.read(inner_name)
                with zipfile.ZipFile(io.BytesIO(inner_data)) as inner:
                    files = inner.namelist()
                    print(f"  Files: {files}")
                    inner.extractall(out_dir)

print("Done!")
