from common import utils, kube
import argparse
from argparse import RawTextHelpFormatter


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('image', type=str, help='''full image path example:
        gcr.io/prod-us-5g-ops-1/spark-data-lake:master-gha-105''')
    parser.add_argument('pipeline', type=str, default="test", help='''"rt" - for built-in list of realtime job in patest namespace
    "hr" - for built-in list of hourly/bulkdata job in patest namespace
    "clinic" - for built-in list of clinic job in patest namespace
    "discovery" - for built-in list of uam-save jobs in patest namespace
    "spc" - for streaming-pipeline-creator job in patest namespace
    "all" - for built-in list of all pipline in patest namespace (except streaming-pipeline-creator)
    ''')
    parser.add_argument("-d", '--debug', help='does not update; only prints out commands', action="store_true")
    parser.add_argument("-n", '--namespace', help='update specified namespace', action="store_true")
    parser.add_argument("-f", '--file', help='update from a text file containing a list of namespaces', action="store_true")
    parser.add_argument("-b", '--boot', help='check pods to boot before proceeding to update the next job.', action="store_true")
    args = parser.parse_args()
    pipeline = args.pipeline
    image = args.image
    namespace_list = kube.get_ns_list(pipeline)
    if args.namespace:
        namespace_list = [pipeline]
    if args.file:
        namespace_list = utils.convert_txt_file_to_list(pipeline)
    
    if args.debug:
        print("------- DEBUG RUN -------")
        print(f"Updating {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            print(f'\t- {i}')
        print(f"Image to update to: {image} \n")
        kube.update_image_for_namespace_list(image=image, NS_list=namespace_list, debug=True, boot=args.boot)
    else:
        print("------- REAL RUN -------")
        print(f"Updating {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            print(f'- {i}')
        print(f"Image to update to: {image} \n")
        kube.update_image_for_namespace_list(image=image, NS_list=namespace_list, debug=False, boot=args.boot)
    utils.exec_cmd('say -v Samantha "Image update successfully completed."')
    print("------- ALL UPDATES DONE -------")

if __name__ == "__main__":
    main()
