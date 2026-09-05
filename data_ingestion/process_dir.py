import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader, generic
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from collections import Counter

if __name__ == "__main__":
    
    def load_docs(dir: str) -> List[Any]:
        
        '''
        This function loads code files, documentations and readme from the given directory
        To load code files we use - generic loader from langchain
        To load pdf files we use - PyMuPDFLoader file from langchain
        
        It stores these documents in a list and return it
        '''
        
        print("extracting pdf docs.....")
        
        pdf_path = Path(dir)
        pdf_files = list(pdf_path.glob("**/*.pdf"))
        
        print(f"{len(pdf_files)} pdfs are there to scan!\n")

        scanned_docs, pdf_docs =[], []
        
        try:
            for pdf_file in pdf_files:
                pdf_loader = PyMuPDFLoader(pdf_file)
                
                pdf_doc = pdf_loader.load()
                
                for doc in pdf_doc:
                    doc.metadata['file_name'] = pdf_file.name
                    doc.metadata['file_type'] = 'pdf'
                
                pdf_docs.extend(pdf_doc)
                
            scanned_docs.extend(pdf_docs)
        except Exception as e:
            print(f"Failed to scan a pdf, {e}")
        
        print(f"{len(pdf_docs)} pdf documents loaded successfully")
        
        try:
            code_docs_loader = generic.GenericLoader.from_filesystem(
                path = dir,
                glob = "**/*",
                suffixes = ['.py', '.js', '.cpp', '.c++'], #Type any language suffix your project includes
                parser = LanguageParser() # LanguageParser() must be there otherwise no files will be loaded
            )

            code_docs = code_docs_loader.load()
            
            scanned_docs.extend(code_docs)
            
            print(f"Scanned {len(scanned_docs)} code documents successfully....\n")
            
        except Exception as e:
            print(f"Reading some code files\n{e}")
        
        return scanned_docs
    
    def chunk_documents(scanned_docs: List[Any]) -> List[Any]:
        
        chunked_docs = []
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            separators = ['\n\n', '\n', ' ', '']
        )
        
        chunked_docs.extend(splitter.split_documents(scanned_docs))
        
        print(f"{len(scanned_docs)} documents chunked into {len(chunked_docs)}")
        
        return chunked_docs

def load_and_chunk(dir: str):
    
    #Scanning/Loading the files from the project diretory
    #The returned type will be list of langchain document data structre
    #We will then chunk these documents
    scanned_docs = load_docs(dir)
    
    #simple analysis
    
    content_types = Counter(
        doc.metadata.get("content_type", "None")
        for doc in scanned_docs
    )
    print(f"{content_types}\n")
    
    print(f"Before removing node_modules scripts docs are {len(scanned_docs)}")
    
    #Removing node_modules scripts as they are not required as context
    for doc in scanned_docs:
        if "node_modules" in doc.metadata.get("source", "no_source"):
            scanned_docs.remove(doc)
    
    scanned_docs = [doc for doc in scanned_docs if "node_modules" not in doc.metadata.get("source", "no_source")]
    
    print(f"After removing node_modules scripts docs are {len(scanned_docs)}")
    
    
    # print(f"Sample of scanned docs:\n{scanned_docs[-1]}")
    
    chunked_docs = chunk_documents(scanned_docs)
    
    return chunked_docs

if __name__ == "__main__":
    
    load_and_chunk("D:/Full Stack PBL")