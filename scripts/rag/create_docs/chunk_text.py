import re
from scripts.rag.create_docs.extract_text import extract_markdowns, extract_rst
from docutils import nodes
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.frontend import OptionParser


_FIN_PHRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])")


# chunk par recouvrement: 
def chunk_taille_fixe(texte, taille=60, recouvrement=12):
    """Découpe par fenêtre fixe de N mots, avec recouvrement entre voisins."""
    if recouvrement >= taille:
        raise ValueError("le recouvrement doit être inférieur à la taille")
    mots = texte.split()
    pas = taille - recouvrement
    chunks, debut = [], 0
    while debut < len(mots):
        chunks.append(" ".join(mots[debut:debut + taille]))
        if debut + taille >= len(mots):
            break
        debut += pas
    return chunks


def segmenter_phrases(texte: str) -> list[str]:
    """Découpe un texte en phrases (segmentation simple par ponctuation)."""
    texte = " ".join(texte.split())
    if not texte:
        return []
    return [p.strip() for p in _FIN_PHRASE.split(texte) if p.strip()]

# chunk par phrase: 
def chunk_par_phrases(texte, max_mots=60):
    """Regroupe des phrases entières sans dépasser un budget de mots."""
    phrases = segmenter_phrases(texte)   # voir le guide sur le nettoyage
    chunks, courant, compte = [], [], 0
    for phrase in phrases:
        n = len(phrase.split())
        if courant and compte + n > max_mots:
            chunks.append(" ".join(courant))
            courant, compte = [], 0
        courant.append(phrase)
        compte += n
    if courant:
        chunks.append(" ".join(courant))
    return chunks


# chunk par section ( A PRIVILEGIER)
def chunk_par_sections_markdown(markdown: str, max_words: int = 60) -> list[dict]:
    """Découpe un Markdown sur ses titres : un chunk par section."""
    sections, titre, corps = [], "(préambule)", []
    for ligne in markdown.splitlines():
        if ligne.lstrip().startswith("#"):
            if any(l.strip() for l in corps):
                if len(corps) >= max_words:
                    sub_chunks = chunk_taille_fixe("\n".join(corps).strip(), taille=max_words, recouvrement = int(max_words/15.0))
                    for sub_chunk in sub_chunks:
                        sections.append({"title": titre, "text": "".join(sub_chunk)})
                else:
                    sections.append({"title": titre, "text": "\n".join(corps).strip()})
            titre, corps = ligne.lstrip("#").strip(), []
        else:
            corps.append(ligne)
    if any(l.strip() for l in corps):
        sections.append({"title": titre, "text": "\n".join(corps).strip()})
    return sections


def _parse_rst_text(rst_text: str):
    """Parse RST text into docutils document."""
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    settings.report_level = 5  # suppress warnings to stderr
    document = new_document("<rst-string>", settings)
    parser.parse(rst_text, document)
    return document


def _walk_rst_sections(node, heading_stack):
    sections = []
    if isinstance(node, nodes.section):
        title_node = node.next_node(nodes.title)
        title = title_node.astext() if title_node else ""
        new_stack = heading_stack + [title]

        body_parts = []
        for child in node.children:
            if isinstance(child, nodes.title):
                continue
            if isinstance(child, nodes.section):
                continue
            if isinstance(child, nodes.system_message):  # <-- add this
                continue
            body_parts.append(child.astext())

        sections.append({
            "heading_path": new_stack,
            "text": "\n\n".join(body_parts).strip(),
        })

        for child in node.children:
            if isinstance(child, nodes.section):
                sections.extend(_walk_rst_sections(child, new_stack))
    else:
        for child in node.children:
            sections.extend(_walk_rst_sections(child, heading_stack))
    return sections


def chunk_par_sections_rst(rst_text: str, max_words: int = 60) -> list[dict]:
    """Découpe un RST sur ses titres (via docutils) : un chunk par section.
    
    Args:
        rst_text: Raw RST string content
        max_words: Maximum words per chunk before splitting with fixed-size windows
        
    Returns:
        List of dicts with 'title' and 'text' keys
    """
    document = _parse_rst_text(rst_text)
    raw_sections = _walk_rst_sections(document, [])
    
    sections = []
    for section in raw_sections:
        text = section["text"]
        title = " > ".join(section["heading_path"]) if section["heading_path"] else "(préambule)"
        
        # Skip empty sections
        if not text.strip():
            continue
            
        word_count = len(text.split())
        
        if word_count >= max_words:
            sub_chunks = chunk_taille_fixe(text, taille=max_words, recouvrement=int(max_words/15.0))
            for sub_chunk in sub_chunks:
                sections.append({"title": title, "text": sub_chunk})
        else:
            sections.append({"title": title, "text": text.strip()})
    
    return sections



def chunk_par_sections_rst_autodoc(rst_text: str, max_words: int = 60) -> list[dict]:
    """Découpe un RST sur ses titres (via docutils) : un chunk par section.
    
    Args:
        rst_text: Raw RST string content
        max_words: Maximum words per chunk before splitting with fixed-size windows
        
    Returns:
        List of dicts with 'title' and 'text' keys
    """
    document = _parse_rst_text(rst_text)
    raw_sections = _walk_rst_sections(document, [])
    
    sections = []
    for section in raw_sections:
        text = section["text"]
        title = " > ".join(section["heading_path"]) if section["heading_path"] else "(préambule)"
        
        # Skip empty sections
        if not text.strip():
            continue
            
        word_count = len(text.split())
        
        if word_count >= max_words:
            sub_chunks = chunk_taille_fixe(text, taille=max_words, recouvrement=int(max_words/15.0))
            for sub_chunk in sub_chunks:
                sections.append({"title": title, "text": sub_chunk})
        else:
            sections.append({"title": title, "text": text.strip()})
    
    return sections


if __name__ == "__main__":
    corpus = extract_rst("IsaacLab", threshold=200)
    print(len(corpus))
    # print(corpus[10])
    for doc in corpus:
        # print(doc['source'])
        if doc['source'] == 'isaaclab.sim.utils':
            # print(doc['text'])
            chunk = chunk_par_sections_rst(doc['text'])
            print(chunk)
