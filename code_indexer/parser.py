from tree_sitter import Language, Parser

# Build a shared library with the Java grammar (this happens once).
Language.build_library(
  'build/my-languages.so',
  ['vendor/tree-sitter-java'] # Path to the cloned tree-sitter-java repo
)
JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

def extract_method_chunks(file_path: str) -> list[dict]:
    """Parses a Java file and extracts all method declarations as chunks."""
    try:
        with open(file_path, 'rb') as f:
            source_code_bytes = f.read()
        
        tree = parser.parse(source_code_bytes)
        chunks = []
        
        for node in tree.root_node.children:
            if node.type == 'class_declaration':
                for class_body_node in node.children:
                    if class_body_node.type == 'class_body':
                        for method_node in class_body_node.children:
                            if method_node.type == 'method_declaration':
                                method_name_node = method_node.child_by_field_name('name')
                                if method_name_node:
                                    method_name = method_name_node.text.decode('utf8')
                                    start_line = method_node.start_point[0] + 1
                                    end_line = method_node.end_point[0] + 1
                                    code_snippet = method_node.text.decode('utf8')
                                    
                                    # Create a stable, unique ID for each method chunk
                                    chunk_id = f"{file_path}::{method_name}::{start_line}-{end_line}"
                                    
                                    chunks.append({
                                        "id": chunk_id,
                                        "code": code_snippet,
                                        "metadata": {
                                            "file_path": file_path,
                                            "method_name": method_name,
                                            "start_line": start_line,
                                            "end_line": end_line
                                        }
                                    })
        return chunks
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

