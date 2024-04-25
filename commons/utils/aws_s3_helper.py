import os
import asyncio
import aiobotocore
from dotenv import load_dotenv
from aiobotocore.session import AioSession

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
REGION_NAME = "ap-southeast-1"


class S3Helper:
    async def upload_file_to_s3(self, file_path, s3_key):
        session = aiobotocore.session.AioSession()
        async with session.create_client(
            "s3",
            region_name=REGION_NAME,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
        ) as client:
            try:
                with open(file_path, "rb") as file_data:
                    await client.put_object(
                        Bucket=AWS_S3_BUCKET_NAME, Key=s3_key, Body=file_data
                    )
                print(f"File {file_path} uploaded to {s3_key}")
            except Exception as e:
                print(f"An error occurred while uploading file to S3: {e}")

    async def list_files_in_s3_bucket(self):
        session = AioSession()
        async with session.create_client(
            "s3",
            region_name=REGION_NAME,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
        ) as client:
            try:
                response = await client.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME)
                for item in response.get("Contents", []):
                    print(f"File found in bucket: {item['Key']}")
            except Exception as e:
                print(f"An error occurred while listing files in S3 bucket: {e}")

    async def download_file_from_s3(self, s3_key, local_file_path):
        session = AioSession()
        async with session.create_client(
            "s3",
            region_name=REGION_NAME,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
        ) as client:
            try:
                response = await client.get_object(
                    Bucket=AWS_S3_BUCKET_NAME, Key=s3_key
                )
                with open(local_file_path, "wb") as file:
                    file.write(await response["Body"].read())
                print(f"File {s3_key} downloaded to {local_file_path}")
            except Exception as e:
                print(f"An error occurred while downloading file from S3: {e}")

    async def delete_file_from_s3(self, s3_key):
        session = AioSession()
        async with session.create_client(
            "s3",
            region_name=REGION_NAME,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
        ) as client:
            try:
                await client.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=s3_key)
                print(f"File {s3_key} deleted from S3 bucket {AWS_S3_BUCKET_NAME}")
            except Exception as e:
                print(f"An error occurred while deleting file from S3: {e}")


if __name__ == "__main__":
    s3_helper = S3Helper()
    # Example usage:
    # To download a file from S3
    # asyncio.run(
    #     s3_helper.download_file_from_s3(
    #         "high_q/augmented_wikipedia.txt",
    #         "data/formatted_data/augmented_wikipedia.txt",
    #     )
    # )

    # asyncio.run(
    #     s3_helper.upload_file_to_s3(
    #         "data/scraped_data/scraped_project_docs.txt",
    #         "high_q/scraped_project_docs.txt",
    #     )
    # )

    # To list out the files in the S3 bucket
    asyncio.run(s3_helper.list_files_in_s3_bucket())

    # asyncio.run(delete_file_from_s3("scraped_TOA_articles_labeled.txt"))
