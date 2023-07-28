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
        self.client = BlobServiceClient(account_url=f"https://{config.az_storage_account_name}.blob.core.windows.net", container_name=config.az_bucket_name, credential=config.az_storage_account_key)
        self.tracking = tracking

    @classmethod
    def create_client(
        cls, config: Config, tracking: Optional[Tracking] = None
    ) -> Optional["AZClient"]:
        return cls(config, tracking=tracking) if config.has_az else None

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
    
        logger.info(f'Uploading to Az blob bucket "{self.config.az_bucket_name}"')
        
        my_content_settings = ContentSettings(content_type='text/html')
        blob = self.client.get_blob_client(self.config.az_bucket_name, bucket_report_path)

        with open(local_html_file_path, "rb") as data:
            blob.upload_blob(data, overwrite=True, content_settings=my_content_settings)
        logger.info("Uploaded report to AZ.")    

        # TODO:
        # implement update_bucket_website logic
        # set the index_document from object StaticWebsite
        # see https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.17.0/azure.storage.blob.html#azure.storage.blob.StaticWebsite
        if self.config.update_bucket_website:
            # Check if the static website hosting is enabled for this storage account
            properties = self.client.get_service_properties()
            static_website_properties = properties['static_website']
            print(static_website_properties.enabled)
            if not static_website_properties.enabled:
            # if not properties.static_website.enabled:
                 raise Exception("Static website is not enabled on this blob")
            
            self.client.set_service_properties(
                static_website_properties={"index_document": "elementary_report.html"}
            )
            #self.blob_service_client.get_blob_client("$web", remote_blob_path)

        return True, bucket_website_url
    
    def get_bucket_website_url(self, blob_path: str) -> str:
        try:
            return f"https://{self.config.az_storage_account_name}.<zone>.web.core.windows.net/{blob_path}"
        except Exception as e:
            self.logger.error(f"Failed to get bucket website URL: {e}")
            return None