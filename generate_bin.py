from dpython.niles.niles_upload import NILESUpload
import argparse
from argparse import RawTextHelpFormatter


def main():
    f"""
    In order to instantiate the niles class,
    1. a client id to niles api
    2. a client secret to niles api
    3. [Optional] url to change the endpoint base url
    """
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('branch', type=str, default="main", help='name of the branch')
    args = parser.parse_args()
    branch = args.branch
    NILESUpload.DEBUG = True
    obj = NILESUpload(
        # optional url="your niles api url",
        client_id="180dba1c-34e7-d124-6ae1-8f77437f5132",
        client_secret="fe3a3375-8606-7be5-4cc4-2468dcfe0376"
    )
    """
    If you want to cache your client_id and client_secret to make an empty parameter 'NILESUploader()' instantiation
    uncomment and call the static setup_env method once
    """
    # NILESUploader.setup_env()
    """
    If you already have your own bin file to upload, you dont need to run the
    request_to_receiver_api method
    """

    response = NILESUpload.request_to_receiver_api(
        url="http://10.9.106.112:443/api/v1/",
        # if trying to upload to home
        # clarity_url="https://e2e-ous.clarity.dexcomdev.com/",
        clarity_username="g7TestAcc+6455751585@s6wlznzv.mailosaur.net",
        clarity_password="20DEXCOM!@",
        # erase=True
        branch_name=str(branch)
        # if trying to save files as different names and path
        # save_bin_file_to="your new path + 'filename.bin'",
        # save_stdout_file_to="your new path + 'filename.txt'"
    )

    # obj.upload_bin_file(
    #     bin_file="path to bin file here",  # optionally you can pass the opened byte file
    #     # for ex. bin_file=base64.b64decode(response.get('file'))
    #     # if you want to save task output to else where
    #     save_niles_file_to="your new path + 'filename.txt")


if __name__ == "__main__":
    main()
