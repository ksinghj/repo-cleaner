# GitHub Repository Cleaner

A Python script to help clean up and manage your GitHub repositories.

## Requirements

*   Python 3.6 or higher
*   `pip` (Python package installer)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd <YOUR_REPOSITORY_DIRECTORY>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   On Linux/macOS:

        ```bash
        source venv/bin/activate
        ```

    *   On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Make the `run_cleaner.sh` script executable:**

    ```bash
    chmod +x run_cleaner.sh
    ```

2.  **Run the script:**

    ```bash
    ./run_cleaner.sh
    ```

    The script will then guide you through the process of cleaning your GitHub repositories.

## Configuration

*   **`requirements.txt`:**  This file lists the Python packages required to run the script.  You can add or remove dependencies as needed.
