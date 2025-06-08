# ASB Alumni Management System

A FastAPI-based REST API server for managing ASB alumni data with comprehensive CRUD operations.

## Features

- **Alumni Management**: Complete CRUD operations for alumni records
- **User Management**: User authentication and authorization system
- **Scrape History**: Track data scraping operations and history
- **CSV Upload**: Handle CSV file uploads and processing
- **Health Monitoring**: Built-in health check endpoints
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. **Clone the repository** (if applicable):

   ```bash
   git clone <repository-url>
   cd asb_be
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file with your database credentials:

   ```env
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=localhost
   DB_PORT=5432
   USE_POSTGRES=True
   ```

## Running the Application

### Method 1: Using the startup script (Recommended)

```bash
python start.py
```

### Method 2: Using uvicorn directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Using the main module

```bash
python -m app.main
```

### Method 4: Using Python directly

```bash
python app/main.py
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health
- **Root Endpoint**: http://localhost:8000/

## API Endpoints

### Health Endpoints

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/database` - Database connection health
- `GET /api/v1/health/detailed` - Detailed system health

### Alumni Endpoints

- `GET /api/v1/alumni/` - List alumni (with pagination and filters)
- `POST /api/v1/alumni/` - Create new alumni record
- `GET /api/v1/alumni/{id}` - Get alumni by ID
- `PUT /api/v1/alumni/{id}` - Update alumni record
- `DELETE /api/v1/alumni/{id}` - Delete alumni record
- `GET /api/v1/alumni/linkedin/{url}` - Get alumni by LinkedIn URL

### User Endpoints

- `GET /api/v1/users/` - List users (with pagination and filters)
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{id}` - Get user by ID
- `GET /api/v1/users/email/{email}` - Get user by email
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `GET /api/v1/users/admins` - Get admin users

### Scrape History Endpoints

- `GET /api/v1/scrape-history/` - List scrape history
- `POST /api/v1/scrape-history/` - Create scrape history record
- `GET /api/v1/scrape-history/{id}` - Get scrape history by ID
- `PUT /api/v1/scrape-history/{id}` - Update scrape history
- `DELETE /api/v1/scrape-history/{id}` - Delete scrape history
- `GET /api/v1/scrape-history/latest` - Get latest scrape histories

### CSV Upload Endpoints

- `GET /api/v1/csv-uploads/` - List CSV uploads
- `POST /api/v1/csv-uploads/` - Create CSV upload record
- `GET /api/v1/csv-uploads/{id}` - Get CSV upload by ID
- `PUT /api/v1/csv-uploads/{id}` - Update CSV upload
- `DELETE /api/v1/csv-uploads/{id}` - Delete CSV upload
- `GET /api/v1/csv-uploads/recent` - Get recent CSV uploads

## Environment Variables

| Variable       | Description            | Default   | Required |
| -------------- | ---------------------- | --------- | -------- |
| `DB_NAME`      | Database name          | -         | Yes      |
| `DB_USER`      | Database user          | -         | Yes      |
| `DB_PASSWORD`  | Database password      | -         | Yes      |
| `DB_HOST`      | Database host          | localhost | Yes      |
| `DB_PORT`      | Database port          | 5432      | Yes      |
| `USE_POSTGRES` | Use PostgreSQL         | True      | Yes      |
| `HOST`         | Server host            | 0.0.0.0   | No       |
| `PORT`         | Server port            | 8000      | No       |
| `RELOAD`       | Auto-reload on changes | true      | No       |
| `LOG_LEVEL`    | Logging level          | info      | No       |

## Development

### Running in Development Mode

```bash
python start.py
```

This will start the server with auto-reload enabled for development.

### Running in Production Mode

```bash
HOST=0.0.0.0 PORT=8000 RELOAD=false python start.py
```

### Testing the API

You can test the API using:

- The interactive documentation at `/docs`
- curl commands
- Postman or similar API testing tools
- Python requests library

Example curl command:

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Get alumni list
curl http://localhost:8000/api/v1/alumni/
```

## Project Structure

```
asb_be/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and utilities
│   │   ├── __init__.py
│   │   ├── alumni.py
│   │   ├── user.py
│   │   ├── scrape_history.py
│   │   └── csv_upload.py
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── alumni_service.py
│   │   ├── user_service.py
│   │   ├── scrape_history_service.py
│   │   └── csv_upload_service.py
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── health.py
│       ├── alumni.py
│       ├── users.py
│       ├── scrape_history.py
│       └── csv_upload.py
├── requirements.txt         # Python dependencies
├── start.py                # Startup script
├── .env.example            # Environment variables example
└── README.md               # This file
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**:

   - Ensure PostgreSQL is running
   - Check database credentials in `.env` file
   - Verify database exists and user has proper permissions

2. **Port Already in Use**:

   - Change the PORT in `.env` file or use a different port
   - Kill the process using the port: `lsof -ti:8000 | xargs kill -9`

3. **Module Import Errors**:
   - Ensure you're in the correct directory
   - Activate your virtual environment
   - Install all dependencies: `pip install -r requirements.txt`

### Logs

The application logs all requests and responses. Check the console output for debugging information.

## Contributing

1. Follow the clean code guidelines in the project
2. Add appropriate logging and error handling
3. Update documentation for new features
4. Test your changes thoroughly

## License

[Add your license information here]

# LinkedIn Profile Data Enrichment

This project uses Gemini AI to enrich LinkedIn profile data with additional metadata and insights about professionals' careers, companies, and industry context.

## Features

- Processes LinkedIn profile data from CSV format
- Uses Gemini AI to analyze and enrich profile information
- Provides insights about:
  - Professional context (industry, career level, expertise)
  - Company analysis (company type, startup status, size)
  - Educational background
  - Market insights
- Outputs both CSV and JSON formats for the enriched data

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your Gemini AI API key:

```
GOOGLE_API_KEY=your_api_key_here
```

3. Place your LinkedIn data CSV file (named `scraped_result.csv`) in the project directory.

## Usage

Run the script:

```bash
python enrich_linkedin_data.py
```

The script will:

1. Read the LinkedIn profile data from `scraped_result.csv`
2. Process each profile using Gemini AI
3. Generate enriched metadata
4. Save the results in two formats:
   - `enriched_linkedin_data.csv`: Full dataset with enriched metadata
   - `enriched_linkedin_data.json`: JSON format for better readability of nested structures

## Output Format

The enriched data includes the original LinkedIn profile information plus additional metadata in the following structure:

```json
{
  "professional_context": {
    "industry_category": "",
    "career_level": "",
    "expertise_areas": [],
    "career_trajectory": ""
  },
  "company_analysis": {
    "current_company_type": "",
    "is_startup": false,
    "company_size_estimate": "",
    "industry_position": "",
    "company_maturity_stage": ""
  },
  "educational_background": {
    "education_level": "",
    "field_specialization": "",
    "educational_progression": ""
  },
  "market_insights": {
    "geographical_focus": "",
    "market_sector": "",
    "emerging_trends": []
  }
}
```

## Error Handling

- The script will skip profiles with errors in the original data
- Any processing errors for individual profiles will be logged but won't stop the overall processing
- Failed profiles will be reported in the console output
