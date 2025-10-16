# Selenium Automation

A Python-based Selenium automation tool for downloading documents from Abbott Lab Central portal.

## Overview

This project automates the process of logging into the Abbott Lab Central website and downloading product documents (PDFs) based on a list of product IDs. The downloaded files are automatically renamed to their corresponding product IDs for easy identification.

## Features

- 🔐 Automated login to Abbott Lab Central portal
- 📥 Batch download of product documents
- 🏷️ Automatic file renaming based on product IDs
- 📊 Progress logging with Loguru
- ⏱️ Download timeout handling
- 🔄 Duplicate file prevention

## Project Structure

```
selenium/
├── src/
│   └── abbott.py         # Main automation script
├── data/
│   └── list.txt          # List of product IDs to download
├── results/
│   └── PDF/              # Downloaded documents storage
├── logs/                 # Application logs
├── scripts/              # Utility scripts
├── notebooks/            # Jupyter notebooks for testing
├── pyproject.toml        # Project dependencies and metadata
├── requirements.txt      # Python dependencies (if needed)
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
└── README.md             # This file
```

## Requirements

- Python >= 3.13
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

### Dependencies

```toml
selenium >= 4.36.0
loguru >= 0.7.3
```

## Installation

### Using UV (Recommended)

```bash
# Install dependencies
uv sync
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### 1. Credentials

Update the credentials in `src/abbott.py`:

```python
EMAIL = "your_email@domain.com"
PASSWORD = "your_password"
```

> ⚠️ **Security Note**: Consider using environment variables or a secure credential manager instead of hardcoding credentials.

### 2. Product ID List

Create a `data/list.txt` file with one product ID per line:

```
product_id_1
product_id_2
product_id_3
```

### 3. Download Folder

The default download location is `results/PDF/`. You can modify this in `src/abbott.py`:

```python
DOWNLOAD_FOLDER = "results/PDF"
```

## Usage

### Basic Usage

```bash
# Activate virtual environment (if using venv)
source .venv/bin/activate

# Run the automation script
python src/abbott.py
```

### Using UV

```bash
uv run python src/abbott.py
```

## How It Works

1. **Initialization**: Sets up Chrome WebDriver with custom download preferences
2. **Login**: Navigates to Abbott Lab Central and authenticates using provided credentials
3. **Product Processing**: Iterates through the product ID list
4. **Download & Rename**: Downloads each product document and renames it to the corresponding product ID
5. **Tracking**: Maintains a set of processed files to avoid duplicate operations

## Key Functions

### `wait_for_download_and_rename()`

Monitors the download folder for newly downloaded files and renames them accordingly.

**Parameters:**
- `download_folder` (str): Path to the download directory
- `product_id` (str): Product ID to use for renaming
- `processed_files` (set): Set of file paths already processed
- `timeout` (int): Maximum wait time in seconds (default: 60)

**Returns:**
- `bool`: True if successful, False if timeout occurs

## Logging

The application uses Loguru for structured logging. Logs include:
- Download progress
- File renaming operations
- Success/error messages
- Timeout warnings

## Docker Support

Docker configuration files are included for containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Troubleshooting

### Common Issues

1. **ChromeDriver version mismatch**
   - Ensure ChromeDriver version matches your Chrome browser version
   - Update ChromeDriver: `pip install --upgrade selenium`

2. **Download timeout**
   - Increase timeout value in `wait_for_download_and_rename()`
   - Check network connection

3. **Login failures**
   - Verify credentials are correct
   - Check if website structure has changed (XPath selectors may need updates)

4. **File not found errors**
   - Ensure `data/list.txt` exists and contains valid product IDs
   - Verify `results/PDF/` directory is created

## Development

### Running Tests

```bash
# Run test notebooks
jupyter notebook notebooks/
```

### Code Style

The project follows Python best practices with type hints and comprehensive documentation.

## Security Considerations

- **Credentials**: Store sensitive information in environment variables or use a secrets manager
- **Access Control**: Ensure proper permissions on credential files
- **Logging**: Avoid logging sensitive information

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions, please [add contact information or issue tracker link].

## Acknowledgments

- Built with [Selenium WebDriver](https://www.selenium.dev/)
- Logging powered by [Loguru](https://github.com/Delgan/loguru)
