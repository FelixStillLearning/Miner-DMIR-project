# MINER - Mining Information Retrieval

MINER is a desktop-based Information Retrieval System designed to help users efficiently search through document collections. It implements a Vector Space Model with Language Modeling (Dirichlet Smoothing) and utilizes the Tala Stemmer for effective text processing of Indonesian documents.

## Features

- **Document Indexing**: Support for .txt, .pdf, and .docx formats.
- **Advanced Preprocessing**:
  - Text Cleaning
  - Tokenization
  - Stopword Removal
  - **Tala Stemmer**: Specific stemming algorithm for Indonesian language. (Based on *Tala, F. Z. (2003)*).
- **Search Engine**:
  - Retrieval using Language Model with Dirichlet Smoothing.
  - Ranked results with scoring usage.
- **Graphical User Interface (GUI)**:
  - Built with CustomTkinter for a modern dark-mode experience.
  - Interactive results page with document previews.
  - File upload and management system.

## Project Structure

- `src/`: Core logic for preprocessing, indexing, and retrieval.
  - `preprocessing/`: Contains `tala_stemmer.py` and `stopword.py`.
  - `indexing/`: Inverted index implementation.
  - `retrieval/`: Search engine logic.
- `ui/`: User Interface components and pages.
- `data/`: Directory for storing raw and processed document data.
- `miner_app.py`: Main entry point for the application.

## Prerequisites

- Python 3.8 or higher
- pip (Python Package Installer)

## Installation

1. Clone the repository or extract the project files.
2. Open a terminal and navigate to the project directory.
3. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python miner_app.py
   ```
2. **Indexing Documents**:
   - Go to the **Upload** page (Folder icon in sidebar).
   - Click "Browse Folder" to select a directory containing your documents (.txt, .pdf, .docx).
   - Wait for the indexing process to complete.
3. **Searching**:
   - Navigate to the **Search** page (Magnifying glass icon).
   - Enter your query in the search bar.
   - Press Enter or click the Search button to view results.
4. **Viewing Results**:
   - Click "Open" on any result card to open the original file.
   - View snippet previews to see context matches.

## License

[Add License Information Here]
