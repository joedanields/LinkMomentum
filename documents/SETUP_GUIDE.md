````markdown
# 🚀 LinkedIn Event Photo Curator - Setup Guide

## Step-by-Step Installation

### Step 1: Set Up Python Environment

1. **Open PowerShell** in the project directory

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### Step 2: Configure LinkedIn API

1. **Go to LinkedIn Developers Portal:**
   - Visit: https://www.linkedin.com/developers/apps
   - Sign in with your LinkedIn account

2. **Create a New App:**
   - Click "Create app" button
   - Fill in the required information:
     - **App name:** "Event Photo Curator" (or any name you prefer)
     - **LinkedIn Page:** Select your company page (you need to have or create one)
     - **Privacy policy URL:** Can use a placeholder initially
     - **App logo:** Optional (recommended for professional look)
   - Click "Create app"

3. **Configure OAuth 2.0 Settings:**
   - Go to the **"Auth"** tab in your app
   - Under "OAuth 2.0 settings":
     - Click "Add redirect URL"
     - Enter: `http://localhost:8000/auth/linkedin/callback`
     - Click "Update"

4. **Request API Products:**
   - Go to the **"Products"** tab
   - Request access to:
     - ✅ **"Share on LinkedIn"** - Required for posting
     - ✅ **"Sign In with LinkedIn"** - Required for authentication
   - Click "Request access" for each product
   - LinkedIn usually approves instantly for most accounts

5. **Copy Your Credentials:**
   - Go back to the **"Auth"** tab
   - Find your **Client ID** and **Client Secret**
   - Copy these values

6. **Update .env File:**
   - Open `.env` file in the project root
   - Replace the placeholder values:
     ```
     LINKEDIN_CLIENT_ID=your_actual_client_id_here
     LINKEDIN_CLIENT_SECRET=your_actual_client_secret_here
     ```

### Step 3: Run the Application

1. **Start the FastAPI server:**
   ```powershell
   python main.py
   ```

2. **Open your browser:**
   - Navigate to: `http://localhost:8000`

3. **Connect LinkedIn:**
   - Click the "Connect LinkedIn" button in the top-right
   - Authorize the application
   - You should see "Connected" status

### Step 4: Use the Application

1. **Upload Photos:**
   - Click the upload area or drag & drop 10-15 event photos
   - Wait for AI processing (usually takes 10-30 seconds)

2. **Review Results:**
   - See quality metrics for each image
   - AI automatically selects the best 10 images
   - Toggle selection by clicking on images

3. **Post to LinkedIn:**
   - Add an optional caption
   - Click "Post to LinkedIn"
   - Your selected images will be posted to your profile!

## 🔧 Configuration Options

Edit `.env` to customize:

### Quality Threshold (0.0 - 1.0)
```
QUALITY_THRESHOLD=0.6
```
- Higher = More strict quality filtering
- Lower = More lenient, includes more images

### Blur Detection
```
BLUR_THRESHOLD=100
```
- Lower values = More strict blur detection
- Higher values = More lenient

### Number of Selected Images
```
MAX_SELECTED_IMAGES=10
```
- Change to select more or fewer images automatically

### Duplicate Detection
```
DUPLICATE_THRESHOLD=5
```
- Lower values = More strict duplicate detection
- Higher values = Only catches very similar images

## 🐛 Troubleshooting

### LinkedIn Authentication Issues

**Problem:** "Authentication failed" or redirect doesn't work

**Solutions:**
- Verify redirect URI in LinkedIn Developer Portal matches exactly: `http://localhost:8000/auth/linkedin/callback`
- Check Client ID and Secret are copied correctly (no extra spaces)
- Make sure "Share on LinkedIn" and "Sign In with LinkedIn" products are approved
- Try clearing browser cookies and cache

### Image Upload Issues

**Problem:** Images not uploading or processing

**Solutions:**
- Check file format (only JPEG, PNG supported)
- Ensure total size doesn't exceed 50MB
- Maximum 20 files at once
- Check console for error messages

### OpenCV Installation Issues on Windows

**Problem:** `pip install opencv-python` fails

**Solution:**
```powershell
pip install opencv-python-headless
```

Then edit `requirements.txt` to replace `opencv-python` with `opencv-python-headless`

---

**Built with ❤️ to save professionals hours of manual work!**

````
