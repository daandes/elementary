from os import path
from typing import Optional, Tuple

from azure.storage.blob import BlobServiceClient, ContentSettings

from elementary.config.config import Config
from elementary.tracking.tracking_interface import Tracking
from elementary.utils import bucket_path
from elementary.utils.log import get_logger

logger = get_logger(__name__)

class AZClient:
    def __init__(self, config: Config, tracking: Optional[Tracking] = None):
        self.config = config
        self.client = BlobServiceClient(account_url=f"https://{config.az_storage_account_name}.blob.core.windows.net", credential=config.az_storage_account_key)
        self.tracking = tracking

        #WEBSITE_URL = f"https://{config.az_storage_account_name}.blob.core.windows.net/{config.az_blob_container_name}"
        # 
        # with open(file_path, "rb") as data:
        #     blob_client.upload_blob(data)
        # https://<account-name>.blob.core.windows.net/<container-name>/<blob-name>


    #required
    @classmethod
    def create_client(
        cls, config: Config, tracking: Optional[Tracking] = None
    ) -> Optional["AZClient"]:
        return cls(config, tracking=tracking) if config.has_az else None

    #required
    def send_report(
        self, local_html_file_path: str, remote_bucket_file_path: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        report_filename = (
            bucket_path.basename(remote_bucket_file_path)
            if remote_bucket_file_path
            else path.basename(local_html_file_path)
        )
        bucket_website_url = None
        bucket_report_path = remote_bucket_file_path or report_filename

        my_content_settings = ContentSettings(content_type='text/html')

        logger.info(f'Uploading to Az blob bucket "{self.config.az_bucket_name}"')

        blob = self.client.get_blob_client(self.config.az_blob_container_name, self.config.gcs_bucket_name)

        with open(local_html_file_path, "rb") as data:
            blob.upload_blob(data, overwrite=True, content_settings=my_content_settings)
        logger.info("Uploaded report to AZ.")    


        # bucket website?

        return True, bucket_website_url
    
    # def get_bucket_website_url(self) -> Optional[str]:
    #     try:
    #         return f"https://{self.config.az_storage_account_name}.<zone>.web.core.windows.net/{blob_path}"
    #     except Exception as e:
    #         self.logger.error(f"Failed to get bucket website URL: {e}")
    #         return None