class StorageUploadException(Exception):
    """Raised when a file upload to Supabase Storage fails."""
    pass

class StorageDeleteException(Exception):
    """Raised when deleting a file from Supabase Storage fails."""
    pass

class StorageSignedUrlException(Exception):
    """Raised when generating a signed URL fails."""
    pass