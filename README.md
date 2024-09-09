# Risk Factor Profile Scraping Tool

This project is a web scraping tool designed to scrape risk factor profiles from the [CSI Korea website](https://www.csi.go.kr). The tool automates the process of collecting data using Playwright for browser automation and BeautifulSoup for parsing HTML content. The extracted data is saved as Excel files.

## Features

- Scrapes data based on `param02` and `param232` values.
- Automatically resumes from the last processed page using a checkpointing system.
- Retries scraping a page up to 3 times in case of network or timeout issues.
- Stores the scraped data in Excel format, avoiding illegal characters in filenames.

## Prerequisites

- Python 3.10 or higher
- Playwright
- Pandas
- BeautifulSoup4
- Tqdm
- Fire

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Install Playwright and its dependencies:
    ```bash
    playwright install
    ```

## Directory Structure

```
. ├── risk_factor_profile.py  # Main script to run the web scraping process
    ├── requirements.txt      # List of required Python packages
    ├── README.md             # Project documentation
    └── utils                 # Utility functions and modules
        ├── __init__.py       # Init file for the utils module
        ├── decorators.py     # Retry decorator for handling timeouts
        ├── files.py          # File saving, checkpoint handling, and illegal character replacement
        ├── logging.py        # Logging configuration and setup
        └── scrapings.py      # Functions for scraping pages and extracting data
```

## Usage

To run the scraping tool, execute the following command:

```bash
python risk_factor_profile.py

Command-line Arguments
params (optional): Path to the input JSON file containing param02 and param232 values. Defaults to extracted_data.json.
output (optional): Output directory to save the Excel files. Defaults to risk_factor_profiles.
checkpoint (optional): Path to the checkpoint file. Defaults to logs/checkpoint.txt.
```

Example command:

```
python risk_factor_profile.py --params='input.json' --output='output_directory' --checkpoint='tmp/my_checkpoint'
```

### Input File Format

The input file should be a JSON file with the following structure:

```json
[
  {
    "param02": "02",
    "param232": "003"
  },
  {
    "param02": "07",
    "param232": "204"
  }
]
```

### Checkpointing

The tool uses a checkpoint system to save progress. If the scraping is interrupted or needs to be resumed, the tool will start from the last saved checkpoint. The checkpoint is stored in logs/checkpoint.txt by default.

### Retry Mechanism

The tool automatically retries fetching a page up to 3 times in case of a TimeoutError due to network issues or page load timeouts.

## Logs

Logs are stored in the logs directory and provide detailed information about the scraping process. A file called risk_factor_profile.log is created, which includes both debug-level information and runtime errors.

## Troubleshooting

### Common Errors

- **TimeoutError:** If the network is slow or the server is unresponsive, the tool will automatically retry up to 3 times. You can increase the delay between retries by modifying the `retry_on_timeout` decorator in `utils/decorators.py`.
- **ModuleNotFoundError:** Ensure that all dependencies are installed correctly by running `pip install -r requirements.txt`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for parsing HTML.

## Author

Created by [pikaybh](https://github.com/pikaybh).