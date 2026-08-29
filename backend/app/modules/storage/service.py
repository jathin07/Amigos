import uuid
import logging
import os
from datetime import datetime, timezone
try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    boto3 = None
    Config = None
    ClientError = Exception
    HAS_BOTO3 = False
from flask import current_app

from app.models import db, UploadedFile, TeamMember
from app.domain.exceptions import NotFoundException, ValidationException, AuthorizationException
from .schemas import UPLOAD_RULES

logger = logging.getLogger(__name__)

class R2StorageService:
    def __init__(self):
        self.bucket_name = current_app.config.get("R2_BUCKET_NAME", "amigos-storage")
        self.endpoint_url = current_app.config.get("R2_ENDPOINT")
        self.access_key_id = current_app.config.get("R2_ACCESS_KEY_ID")
        self.secret_access_key = current_app.config.get("R2_SECRET_ACCESS_KEY")
        self.public_url = current_app.config.get("R2_PUBLIC_URL", "https://cdn.amigostourism.com").rstrip("/")
        self.expiry = current_app.config.get("R2_PRESIGNED_EXPIRY", 600)
        
        # Determine if we should mock boto3 client (e.g. during testing or if credentials missing)
        self.is_mock = current_app.config.get("TESTING", False) or not (
            self.endpoint_url and self.access_key_id and self.secret_access_key
        )
        
        if not self.is_mock:
            try:
                self.s3_client = boto3.client(
                    service_name="s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    config=Config(signature_version="s3v4")
                )
            except Exception as e:
                logger.warning(f"Failed to initialize R2 boto3 client, falling back to mock: {e}")
                self.is_mock = True
                self.s3_client = None
        else:
            self.s3_client = None

    def generate_presigned_url(self, folder: str, filename: str, content_type: str, file_size: int, actor_id: uuid.UUID | str) -> dict:
        """
        Command: Validates and generates a presigned URL to PUT upload direct to Cloudflare R2.
        Also registers an uncompleted UploadedFile record.
        """
        rules = UPLOAD_RULES.get(folder)
        if not rules:
            raise ValidationException(f"Folder '{folder}' is not whitelisted for storage upload.")

        # 1. Validate Extension and MIME type
        _, ext = os.path.splitext(filename.lower())
        if not ext or ext not in rules["allowed_extensions"]:
            raise ValidationException(f"Extension '{ext}' is not allowed for folder '{folder}'.")

        if content_type.lower() not in rules["allowed_mimes"]:
            raise ValidationException(f"Content-type '{content_type}' is not allowed for folder '{folder}'.")

        # 2. Validate Size Limit
        max_bytes = rules["max_size_mb"] * 1024 * 1024
        if file_size > max_bytes:
            raise ValidationException(f"File size of {file_size} bytes exceeds folder limit of {rules['max_size_mb']}MB.")

        # 3. Generate UUID Object Key
        object_uuid = uuid.uuid4()
        # Namespace matches 'public' or 'private'
        namespace = "private" if folder.startswith("private/") else "public"
        object_key = f"{folder}/{object_uuid}{ext}"

        # 4. S3/R2 PUT Request Parameters
        params = {
            "Bucket": self.bucket_name,
            "Key": object_key,
            "ContentType": content_type
        }
        if namespace == "public":
            # Set Cache-Control header for static CDN performance
            params["CacheControl"] = "public, max-age=31536000"

        # 5. Generate Presigned URL
        upload_url = None
        if self.is_mock:
            upload_url = f"https://mock-r2.cloudflarestorage.com/{self.bucket_name}/{object_key}?presigned=true"
        else:
            try:
                upload_url = self.s3_client.generate_presigned_url(
                    ClientMethod="put_object",
                    Params=params,
                    ExpiresIn=self.expiry
                )
            except ClientError as e:
                logger.error(f"R2 presigned URL generation failed: {e}")
                raise ValidationException("Failed to generate storage upload URL.")

        # 6. Save metadata to DB (Pending completion)
        uploaded_file = UploadedFile(
            object_key=object_key,
            original_filename=filename,
            file_size=file_size,
            content_type=content_type,
            namespace=namespace,
            folder=folder,
            uploaded_by_team_member_id=uuid.UUID(str(actor_id)) if actor_id else None,
            is_completed=False
        )
        db.session.add(uploaded_file)
        db.session.commit()

        # Audit/Debug Logging
        logger.info(
            f"Presigned URL generated: User={actor_id} Folder={folder} Key={object_key} Size={file_size} Bytes"
        )

        return {
            "upload_url": upload_url,
            "public_url": f"{self.public_url}/{object_key}",
            "object_key": object_key
        }

    def complete_upload(self, object_key: str, actor_id: uuid.UUID | str = None) -> UploadedFile:
        """
        Command: Verifies that the object exists in R2 and marks the record completed.
        """
        uploaded_file = db.session.scalar(
            db.select(UploadedFile).where(UploadedFile.object_key == object_key)
        )
        if not uploaded_file:
            raise NotFoundException("File metadata not registered in database.")

        if uploaded_file.is_completed:
            return uploaded_file

        # Verify against actual storage
        if not self.is_mock:
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            except ClientError as e:
                # 404 means user hasn't successfully PUTed yet
                logger.warning(f"Storage verify failed for {object_key}: {e}")
                raise ValidationException("File does not exist in storage bucket yet. Upload must be completed first.")

        # Mark completed
        uploaded_file.is_completed = True
        uploaded_file.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        logger.info(
            f"Upload Completed: User={actor_id} Key={object_key} Size={uploaded_file.file_size}"
        )
        return uploaded_file

    def delete_object(self, object_key: str, actor_id: uuid.UUID | str, user_permissions: set = None, user_role: str = None) -> bool:
        """
        Command: Deletes the object from R2 and removes the database record.
        Enforces ownership rules: Only the uploader or administrators can delete files.
        """
        uploaded_file = db.session.scalar(
            db.select(UploadedFile).where(UploadedFile.object_key == object_key)
        )
        if not uploaded_file:
            raise NotFoundException("File not found in storage record.")

        # 1. Authorization Ownership Check
        is_owner = uploaded_file.uploaded_by_team_member_id and str(uploaded_file.uploaded_by_team_member_id) == str(actor_id)
        is_admin = user_role == "Admin" or (user_permissions and "admin.full" in user_permissions)

        if not (is_owner or is_admin):
            # Check DB role as fallback if context missing
            member = db.session.get(TeamMember, actor_id)
            if member and member.role and member.role.name == "Admin":
                is_admin = True

        if not (is_owner or is_admin):
            raise AuthorizationException("Unauthorized: You do not own this file and are not an Administrator.")

        # 2. Remove from R2
        if not self.is_mock:
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            except ClientError as e:
                logger.error(f"R2 delete failed for key {object_key}: {e}")
                raise ValidationException("Failed to delete file from Cloudflare storage.")

        # 3. Remove database record
        db.session.delete(uploaded_file)
        db.session.commit()

        logger.info(
            f"Object deleted successfully: User={actor_id} Key={object_key} Role={user_role}"
        )
        return True

    def generate_download_url(self, object_key: str, actor_id: uuid.UUID | str, expires_in: int = 3600) -> dict:
        """
        Query: Returns the URL to access a file. 
        If private namespace, returns a secure presigned download GET URL.
        If public namespace, returns direct public CDN URL.
        """
        uploaded_file = db.session.scalar(
            db.select(UploadedFile).where(UploadedFile.object_key == object_key)
        )
        if not uploaded_file:
            raise NotFoundException("File record not found.")

        if not uploaded_file.is_completed:
            raise ValidationException("File upload is not complete.")

        # Public files serve from CDN directly
        if uploaded_file.namespace == "public":
            return {
                "download_url": f"{self.public_url}/{object_key}"
            }

        # Private files generate signed GET link
        download_url = None
        if self.is_mock:
            download_url = f"https://mock-r2.cloudflarestorage.com/{self.bucket_name}/{object_key}?signature=signed-download&expires={expires_in}"
        else:
            try:
                download_url = self.s3_client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.bucket_name, "Key": object_key},
                    ExpiresIn=expires_in
                )
            except ClientError as e:
                logger.error(f"R2 signed download generation failed: {e}")
                raise ValidationException("Failed to generate download URL.")

        return {
            "download_url": download_url
        }

    def cleanup_orphans(self, hours: int = 24) -> int:
        """
        Maintenance: Deletes uncompleted storage files older than threshold hours.
        """
        from datetime import timedelta
        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Query uncompleted UploadedFiles older than threshold
        # Since UploadedFile uses TimestampMixin, it has created_at
        orphans = db.session.scalars(
            db.select(UploadedFile).where(
                (UploadedFile.is_completed == False) & 
                (UploadedFile.created_at < threshold)
            )
        ).all()

        deleted_count = 0
        for orphan in orphans:
            try:
                # Delete from storage if not mock
                if not self.is_mock:
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=orphan.object_key)
                db.session.delete(orphan)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to clean up orphan object key {orphan.object_key}: {e}")

        if deleted_count > 0:
            db.session.commit()
            logger.info(f"Cleaned up {deleted_count} orphan storage objects.")
            
        return deleted_count
