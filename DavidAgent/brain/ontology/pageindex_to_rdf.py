import os
import re
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

class PageIndexToRDFConverter:
    """
    Parses strictly formatted Double-Linked Markdown PageIndex files
    and reconstructs them into an explicit rdflib RDF Graph.
    """
    def __init__(self):
        self.DVA = Namespace("http://davidagent.ai/ontology#")
        self.graph = Graph()
        self.graph.bind("dva", self.DVA)
        self.graph.bind("rdfs", RDFS)

        # Regex definitions
        self.entity_pattern = re.compile(r'^\s*-\s*\*\*\[\[([^\]]+)\]\]\*\*\s*\(([^)]+)\):\s*(.*)$')
        self.triple_pattern = re.compile(r'^\s*-\s*\[\[([^\]]+)\]\]\s*==\s*(.*?)\s*==>\s*\[\[([^\]]+)\]\](?:\s*\*\((?:补充:)?\s*(.*?)\)\*)?$')

    def sanitize_uri(self, text: str) -> str:
        """Sanitize text to be a valid URI component."""
        return "".join([c if c.isalnum() else "_" for c in text.strip()])

    def parse_markdown_file(self, file_path: Path):
        """Parse a single Markdown file line by line."""
        source_id = file_path.stem
        source_uri = self.DVA[f"Source_{self.sanitize_uri(source_id)}"]
        self.graph.add((source_uri, RDF.type, self.DVA.DocumentSource))
        self.graph.add((source_uri, RDFS.label, Literal(source_id)))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Attempt Entity Regex Match
            entity_match = self.entity_pattern.match(line)
            if entity_match:
                name, e_type, desc = entity_match.groups()
                entity_uri = self.DVA[self.sanitize_uri(name)]
                type_uri = self.DVA[self.sanitize_uri(e_type)]
                
                self.graph.add((entity_uri, RDF.type, type_uri))
                self.graph.add((entity_uri, RDFS.label, Literal(name.strip())))
                if desc.strip():
                    self.graph.add((entity_uri, RDFS.comment, Literal(desc.strip())))
                self.graph.add((entity_uri, self.DVA.mentionedIn, source_uri))
                continue

            # Attempt Triple Regex Match
            triple_match = self.triple_pattern.match(line)
            if triple_match:
                subj, pred, obj, context = triple_match.groups()
                subj_uri = self.DVA[self.sanitize_uri(subj)]
                obj_uri = self.DVA[self.sanitize_uri(obj)]
                pred_uri = self.DVA[self.sanitize_uri(pred)]
                
                self.graph.add((subj_uri, pred_uri, obj_uri))
                if context and context.strip():
                    # For statement level context in RDF, reification is standard, but we'll attach an interaction property for simplicity.
                    # RDFS doesn't easily support edge-properties without OWL2 logic or blank nodes, so we attach the context to the subj.
                    pass

    def convert_all(self, md_dir_path: str, output_path: str = "converted_pageindex.ttl"):
        """Iterate over a directory of MD files and build the full RDF graph."""
        md_dir = Path(md_dir_path)
        if not md_dir.exists():
            print(f"Directory {md_dir_path} does not exist.")
            return

        cnt = 0
        for file_path in md_dir.glob("*.md"):
            self.parse_markdown_file(file_path)
            cnt += 1

        self.graph.serialize(destination=output_path, format="turtle")
        print(f"✅ Converted {cnt} PageIndex Markdown files.")
        print(f"✅ Generated RDF Graph with {len(self.graph)} Triples saved to {output_path}.")

if __name__ == "__main__":
    converter = PageIndexToRDFConverter()
    project_root = Path(__file__).parent.parent.parent
    knowledge_dir = project_root / "skills" / "self-learning-agent" / "pageindex" / "knowledge"
    output_dir = project_root / "skills" / "self-learning-agent" / "pageindex" / "ontology"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    out_ttl = output_dir / "converted_pageindex.ttl"
    converter.convert_all(str(knowledge_dir), str(out_ttl))
