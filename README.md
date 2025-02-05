# SQL Agent System with Groq & DSPy

This project is a Python-based SQL agent system that uses Groq's LLM (Large Language Model) for natural language processing and database query generation. It integrates with a MySQL database to process user queries, generate corresponding SQL queries, execute them, and handle errors with intelligent debugging.

### Key Features:
- **Groq-based LLM** for generating SQL queries from natural language.
- **SQL execution** with error handling and debugging.
- **Asynchronous execution** for better performance and scalability.
- **Customizable retry logic** for handling query failures.
- **Database connection pooling** for efficient resource management.

---

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package installer)

Additionally, you will need:

- **Groq API Key**: Sign up on [Groq Console](https://console.groq.com/) and get your API key.
- **MySQL Database**: You will need a running MySQL instance and database access credentials.
- **Python Libraries**: The project uses several third-party libraries, which can be installed via `pip`.

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>


### 2. Install Dependencies
Create a virtual environment and install the necessary packages:

- python3 -m venv venv
- source venv/bin/activate  # For Linux/macOS
- venv\Scripts\activate     # For Windows
- pip install -r requirements.txt

### 3. Set Up Environment Variables
Create a .env file in the root of your project and define the following environment variables:

- GROQ_API_KEY=<your_groq_api_key>
- mysql_host=localhost
- mysql_port=3306
- mysql_user=root
- mysql_password=<your_mysql_password>
- mysql_database=chatbot







