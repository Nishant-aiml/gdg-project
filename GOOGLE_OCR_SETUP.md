# Google Cloud Vision API OCR Setup

## Free Tier
- **1,000 images per month** are free
- Each image counts as 1 unit for text detection
- After free tier: $1.50 per 1,000 units

## Setup Instructions

### Option 1: Service Account (Recommended)

1. **Create a Google Cloud Project** (if you don't have one):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Cloud Vision API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

3. **Create Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "ocr-service")
   - Grant role: "Cloud Vision API User"
   - Click "Done"

4. **Download Credentials**:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file

5. **Set Environment Variable**:
   ```bash
   # Add to .env file
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
   ```

### Option 2: Default Credentials (For Development)

If you have `gcloud` CLI installed:

```bash
gcloud auth application-default login
```

This will use your personal Google account credentials.

## Installation

```bash
cd backend
pip install google-cloud-vision
```

## How It Works

1. **Primary**: Google Cloud Vision API (if credentials available)
2. **Fallback**: PaddleOCR (if Google OCR fails or unavailable)

The system automatically:
- Tries Google OCR first (free tier)
- Falls back to PaddleOCR if Google OCR fails or quota exceeded
- Logs which service is being used

## Usage

No code changes needed! The OCR service automatically uses Google Vision API if credentials are available.

## Monitoring Usage

Check your usage in Google Cloud Console:
- Navigate to "APIs & Services" > "Dashboard"
- Select "Cloud Vision API"
- View "Quotas" to see usage

## Notes

- Free tier resets monthly
- If you exceed 1,000 images, you'll be charged $1.50 per 1,000 additional images
- Service account method is more secure than API keys
- PaddleOCR remains as fallback (no cost, runs locally)

