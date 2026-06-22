from docutils import nodes
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.frontend import OptionParser

def parse_rst(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    settings.report_level = 5  # suppress warnings to stderr
    document = new_document(filepath, settings)  # use filepath as doc source name
    parser.parse(text, document)
    return document

def extract_chunks(document):
    chunks = []

    def walk(node, heading_stack):
        if isinstance(node, nodes.section):
            title_node = node.next_node(nodes.title)
            title = title_node.astext() if title_node else ""
            new_stack = heading_stack + [title]

            body_parts = []
            for child in node.children:
                if isinstance(child, nodes.title):
                    continue
                if isinstance(child, nodes.section):
                    continue  # handled by recursion
                body_parts.append(child.astext())

            chunks.append({
                "heading_path": new_stack,
                "text": "\n\n".join(body_parts).strip(),
            })

            for child in node.children:
                if isinstance(child, nodes.section):
                    walk(child, new_stack)
        else:
            for child in node.children:
                walk(child, heading_stack)

    walk(document, [])
    return chunks


# Usage
if __name__ == "__main__":
    document = parse_rst("IsaacLab/docs/source/lab/isaaclab.actuators.rst")
    chunks = extract_chunks(document)
    for c in chunks:
        print(" > ".join(c["heading_path"]))
        print(c["text"][:200])
        print("---")