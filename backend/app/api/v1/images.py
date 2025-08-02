from fastapi import APIRouter, HTTPException, status, Query
from app.services.unsplash_service import unsplash_service
from app.core.config import settings

router = APIRouter()


@router.get("/search/")
def search_images(
    query: str = Query(..., min_length=1),
    per_page: int = Query(10, ge=1, le=30),
    page: int = Query(1, ge=1)
):
    """Search for images on Unsplash"""
    try:
        results = unsplash_service.search_photos(
            query=query,
            per_page=per_page,
            page=page
        )
        
        # Format response to include only necessary data
        formatted_results = []
        for photo in results.get("results", []):
            formatted_results.append({
                "id": photo["id"],
                "description": photo.get("description", ""),
                "alt_description": photo.get("alt_description", ""),
                "urls": {
                    "regular": photo["urls"]["regular"],
                    "small": photo["urls"]["small"],
                    "thumb": photo["urls"]["thumb"]
                },
                "user": {
                    "name": photo["user"]["name"],
                    "username": photo["user"]["username"]
                },
                "download_url": photo["links"]["download_location"]
            })
        
        return {
            "results": formatted_results,
            "total": results.get("total", 0),
            "total_pages": results.get("total_pages", 0)
        }
        
    except ValueError as e:
        # Handle Unsplash API authentication and validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching images: {str(e)}"
        )


@router.get("/{photo_id}")
def get_image_details(photo_id: str):
    """Get details of a specific image"""
    try:
        photo = unsplash_service.get_photo(photo_id)
        
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        return {
            "id": photo["id"],
            "description": photo.get("description", ""),
            "alt_description": photo.get("alt_description", ""),
            "urls": photo["urls"],
            "user": {
                "name": photo["user"]["name"],
                "username": photo["user"]["username"]
            },
            "download_url": photo["links"]["download_location"]
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle Unsplash API authentication and validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting image details: {str(e)}"
        )


@router.post("/select/")
def select_image(photo_id: str, download_url: str):
    """Select an image (triggers download tracking)"""
    try:
        success = unsplash_service.trigger_download(download_url)
        
        return {
            "photo_id": photo_id,
            "success": success,
            "message": (
                "Image selection recorded" if success
                else "Could not record selection"
            )
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error selecting image: {str(e)}"
        )


@router.get("/credentials/")
def check_credentials():
    """Check Unsplash API credentials and status"""
    try:
        # Check if credentials are configured
        access_key_configured = bool(settings.UNSPLASH_ACCESS_KEY)
        secret_key_configured = bool(settings.UNSPLASH_SECRET_KEY)
        
        if not access_key_configured:
            return {
                "status": "not_configured",
                "message": "Unsplash Access Key not configured",
                "access_key": False,
                "secret_key": secret_key_configured,
                "api_limits": None
            }
        
        # Get API limits and validate credentials
        api_limits = unsplash_service.get_api_limits()
        credentials_valid = api_limits.get("status_code") == 200
        
        return {
            "status": "configured" if credentials_valid else "invalid",
            "message": (
                "Credentials are valid and working"
                if credentials_valid
                else "Credentials configured but invalid"
            ),
            "access_key": access_key_configured,
            "secret_key": secret_key_configured,
            "api_limits": {
                "rate_limit": api_limits.get("rate_limit"),
                "remaining": api_limits.get("remaining"),
                "reset_time": api_limits.get("reset_time")
            } if credentials_valid else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking credentials: {str(e)}"
        )


@router.get("/stats/")
def get_user_stats():
    """Get current user's API usage statistics (requires secret key)"""
    try:
        stats = unsplash_service.get_user_stats()
        
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "User stats not available. "
                    "Requires both Access Key and Secret Key."
                )
            )
        
        return {
            "user": stats.get("username", "Unknown"),
            "total_likes": stats.get("total_likes", 0),
            "total_photos": stats.get("total_photos", 0),
            "total_collections": stats.get("total_collections", 0),
            "downloads": stats.get("downloads", 0),
            "views": stats.get("views", 0)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user stats: {str(e)}"
        )
