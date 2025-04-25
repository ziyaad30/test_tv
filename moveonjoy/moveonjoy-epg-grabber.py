import os
import gzip
import xml.etree.ElementTree as ET
import requests

name = "moveonjoy"
save_as_gz = True  

output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "epgs")
os.makedirs(output_dir, exist_ok=True)  

tvg_ids_file = os.path.join(os.path.dirname(__file__), f"{name}-tvg-ids.txt")
output_file = os.path.join(output_dir, f"{name}-epg.xml")
output_file_gz = output_file + '.gz'

def fetch_and_extract_xml(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    if url.endswith('.gz'):
        try:
            decompressed_data = gzip.decompress(response.content)
            return ET.fromstring(decompressed_data)
        except Exception as e:
            print(f"Failed to decompress and parse XML from {url}: {e}")
            return None
    else:
        try:
            return ET.fromstring(response.content)
        except Exception as e:
            print(f"Failed to parse XML from {url}: {e}")
            return None

def filter_and_build_epg(urls):
    with open(tvg_ids_file, 'r') as file:
        valid_tvg_ids = set(line.strip() for line in file)

    root = ET.Element('tv')

    for url in urls:
        print(f"Fetching xml ({url})...")
        epg_data = fetch_and_extract_xml(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if tvg_id in valid_tvg_ids:
                print(f"tvg-id -> {tvg_id}")
                root.append(channel)

        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if tvg_id in valid_tvg_ids:
                title = programme.find('title')
                if title is not None:
                    title_text = title.text if title is not None else 'No title'

                    if title_text == 'NHL Hockey' or title_text == 'Live: NFL Football':
                        subtitle = programme.find('sub-title')
                        subtitle_text = subtitle.text if subtitle else 'No subtitle'
                        programme.find('title').text = title_text + " " + subtitle_text

                    root.append(programme)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")


urls = [
    'https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS2.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_IE1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_ZA1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_PLEX1.xml.gz'
]

if __name__ == "__main__":
    filter_and_build_epg(urls)
