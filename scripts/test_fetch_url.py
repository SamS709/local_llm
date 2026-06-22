"""
Fetch a Sphinx-style documentation page (e.g. NVIDIA Isaac Sim docs)
and convert it to clean Markdown text — useful for reading or feeding to an LLM.

pip install requests beautifulsoup4 html2text lxml
"""

import requests
from bs4 import BeautifulSoup
import html2text


def fetch_clean_markdown(url: str) -> str:
    """Fetch a documentation page and return clean markdown text."""
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # Sphinx docs (like this NVIDIA site) put the real content inside
    # <article> or a div with role="main". Strip nav/sidebar/footer noise.
    main = (
        soup.find("article")
        or soup.find("div", {"role": "main"})
        or soup.find("main")
        or soup.body
    )

    # Remove elements that add no value for an LLM / reader
    for tag in main.select("nav, .headerlink, script, style, .sidebar, .related"):
        tag.decompose()

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0  # don't hard-wrap lines

    markdown = converter.handle(str(main))
    return markdown.strip()


def crawl_section(link_prefix: str, max_pages: int = 30000) -> dict:
    """
    Crawl all pages under `link_prefix` (used both as the starting URL and
    as the filter for which discovered links to follow).
 
    e.g. link_prefix="https://docs.isaacsim.omniverse.nvidia.com/4.5.0/isaac_lab_tutorials/index.html"
    will start there and follow any link starting with
    "https://docs.isaacsim.omniverse.nvidia.com/4.5.0/isaac_lab_tutorials/".
 
    Returns {url: markdown_text}.
    """
    import os
    import urllib.parse
 
    # Use the prefix's directory as the link filter (so index.html itself
    # still matches), and as the starting point for the crawl.
    start_url = link_prefix
    prefix_dir = link_prefix.rsplit("/", 1)[0] + "/"
 
    visited = {}
    to_visit = [start_url]
 
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
 
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.status_code != 200:
            continue
 
        soup = BeautifulSoup(resp.text, "lxml")
        visited[url] = fetch_clean_markdown(url)
 
        for a in soup.find_all("a", href=True):
            href = urllib.parse.urljoin(url, a["href"])
            href = href.split("#")[0]  # drop in-page anchors
            if href.startswith(prefix_dir) and href not in visited:
                to_visit.append(href)
 
    return visited



def write_visited(visited: dict, dir: str) -> None:
    """
    Write each {url: markdown_text} pair from `visited` to its own .md file
    inside `dir`. The filename is derived from the last path segment of the
    URL, e.g. ".../tutorial_core_hello_robot.html" -> "tutorial_core_hello_robot.md".
    """
    import os
    import urllib.parse
 
    os.makedirs(dir, exist_ok=True)
 
    for url, markdown in visited.items():
        path = urllib.parse.urlparse(url).path
        filename = os.path.basename(path)  # e.g. "tutorial_core_hello_robot.html"
 
        if filename.endswith(".html"):
            filename = filename[: -len(".html")]
        filename += ".md"
 
        out_path = os.path.join(dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown)
 
        print(f"wrote {out_path} ({len(markdown)} chars)")

if __name__ == "__main__":
    url = "https://docs.isaacsim.omniverse.nvidia.com/4.5.0/isaac_lab_tutorials/index.html"
    md = fetch_clean_markdown(url)
    print(md)

    # Example: crawl the whole isaac_lab_tutorials section
    print("CRAWLING PAGES...")
    pages = crawl_section(
        link_prefix="https://docs.ansible.com/projects/ansible/latest",
    )
    print(len(pages), "PAGES CRAWLED...")
    print("WRITING PAGES...")
    write_visited(pages, "AnsibleDocs")
    print("DONE !")
