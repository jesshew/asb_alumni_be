from fastapi import APIRouter, HTTPException, UploadFile, File, status
import os
import logging

logger = logging.getLogger(__name__)

# Create upload directory in the same folder as this file
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create router with prefix and tags
router = APIRouter(prefix="/csv-uploads", tags=["CSV Uploads"])

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Simple endpoint to upload and save a CSV file locally."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No filename provided"
        )

    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only CSV files are allowed"
        )

    try:
        # Save file with original filename
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {
            "message": "File uploaded successfully",
            "saved_path": file_path
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
