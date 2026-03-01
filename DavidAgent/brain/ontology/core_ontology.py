from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

class DavidAgentOntology:
    """
    Formal OWL Ontology definitions for DavidAgent's structural knowledge graph.
    """
    def __init__(self):
        self.DVA = Namespace("http://davidagent.ai/ontology#")
        self.graph = Graph()
        self.graph.bind("dva", self.DVA)
        self.graph.bind("owl", OWL)
        
    def build_ontology(self):
        """Construct the core formal classes and relationships restricting the Triple generation."""
        # Define Ontology metadata
        self.graph.add((self.DVA.DavidAgentOntology, RDF.type, OWL.Ontology))
        self.graph.add((self.DVA.DavidAgentOntology, RDFS.label, Literal("DavidAgent Core Ontology")))
        self.graph.add((self.DVA.DavidAgentOntology, RDFS.comment, Literal("A formal OWL-based ontology restricting and structuring DavidAgent's PageIndex knowledge representations.")))

        # Define Core Classes
        core_classes = {
            "Concept": "An abstract idea, generalized representation, or theoretical construct.",
            "Person": "A human individual, real or persona-based.",
            "Organization": "An organized body of people with a particular purpose, e.g., a company or open-source group.",
            "Model": "An AI model, algorithm, or mathematical construct (e.g., DeepSeek, Gemini).",
            "Framework": "A software architecture or infrastructural tool (e.g., PyVis, OpenClaw).",
            "Tool": "A utility, script, or component yielding specific capability.",
            "Component": "A distinct architectural organ inside the Multi-Agent topology."
        }

        for cls_name, cls_desc in core_classes.items():
            cls_uri = self.DVA[cls_name]
            self.graph.add((cls_uri, RDF.type, OWL.Class))
            self.graph.add((cls_uri, RDFS.label, Literal(cls_name)))
            self.graph.add((cls_uri, RDFS.comment, Literal(cls_desc)))

        # Define Object Properties (Relationships)
        object_properties = {
            "depends_on": (OWL.ObjectProperty, "Indicates a technical or conceptual dependency."),
            "developed_by": (OWL.ObjectProperty, "Indicates the creator (Person/Organization) of a Component/Model/Framework."),
            "part_of": (OWL.ObjectProperty, "Indicates mereological parthood."),
            "implements": (OWL.ObjectProperty, "Indicates the realization of a Concept."),
            "similar_to": (OWL.SymmetricProperty, "Indicates conceptual or functional proximity."),
            "conflicts_with": (OWL.SymmetricProperty, "Indicates opposing mechanics or exclusionary logic.")
        }

        for prop_name, (prop_type, prop_desc) in object_properties.items():
            prop_uri = self.DVA[prop_name]
            self.graph.add((prop_uri, RDF.type, prop_type))
            self.graph.add((prop_uri, RDFS.label, Literal(prop_name)))
            self.graph.add((prop_uri, RDFS.comment, Literal(prop_desc)))

        return self.graph

    def save_ontology(self, output_path: str = "core_ontology.ttl"):
        """Save the ontology to a TTL file."""
        self.build_ontology()
        self.graph.serialize(destination=output_path, format="turtle")
        print(f"✅ Ontology saved to {output_path} with {len(self.graph)} triples.")

if __name__ == "__main__":
    ontology = DavidAgentOntology()
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "skills" / "self-learning-agent" / "pageindex" / "ontology"
    output_dir.mkdir(parents=True, exist_ok=True)
    ontology.save_ontology(str(output_dir / "core_ontology.ttl"))
