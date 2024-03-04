from common import utils, kube
import argparse
from argparse import RawTextHelpFormatter


netskope_ips="66.85.67.20/32,104.154.31.59/30,34.123.228.176/32,34.72.71.80/32,24.206.101.62/31,24.206.102.57/32,24.206.102.58/32,24.206.107.62/31,24.206.110.66/31,24.206.112.87/32,24.206.112.88/32,24.206.114.60/31,24.206.115.66/31,24.206.67.20/31,24.206.73.90/31,24.206.77.78/31,24.206.79.26/32,24.206.79.25/32,24.206.80.86/31,24.206.98.66/31,24.206.99.62/31,24.239.129.58/32,24.239.129.57/32,24.239.137.74/31,24.239.144.57/32,24.239.144.58/32,24.239.145.56/31,24.239.160.59/32,24.239.160.60/32,24.239.163.58/31,24.239.165.148/31,24.239.166.59/32,24.239.166.60/32,24.206.106.62/31,24.206.111.54/31,24.206.120.20/31,24.206.84.100/32,24.206.84.99/32,24.239.139.56/31,24.239.162.60/31,24.206.100.64/31,24.206.108.64/31,24.206.109.79/32,24.206.109.80/32,24.206.103.63/32,24.206.103.64/32,24.206.104.66/31,24.206.105.56/31,24.206.65.56/31,24.206.66.80/31,24.206.68.80/31,24.206.70.152/31,24.206.72.78/31,24.206.69.18/31,24.206.71.80/31,24.206.74.56/31,24.206.75.56/31,24.206.78.84/31,24.206.82.91/32,24.206.82.92/32,24.206.88.20/31,24.206.89.20/31,24.239.128.84/31,24.206.76.128/31,24.206.97.78/31,24.239.130.68/31,24.239.131.60/31,24.239.132.66/31,24.239.133.74/31,24.239.136.58/31,24.239.138.74/31,24.239.141.69/32,24.239.141.70/32,24.239.161.56/31,24.239.164.54/31,24.239.134.60/31,24.239.135.54/31,24.239.140.63/32,24.239.140.64/32,24.239.167.56/31"

def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('ns', type=str, default="test", help='namespace required')
    parser.add_argument("-d", '--debug', help='does not update; only prints out commands', action="store_true")
    parser.add_argument("-n", '--namespace', help='update specified namespace', action="store_true")
    parser.add_argument("-f", '--file', help='update from a text file containing a list of namespaces', action="store_true")

    args = parser.parse_args()
    ns = args.ns
    if args.namespace:
        namespace_list = [ns]
    if args.file:
        namespace_list = utils.convert_txt_file_to_list(ns)
    
    print(f'Netskope IP count: {len(netskope_ips.split(","))}')

    if args.debug:
        print("------- DEBUG RUN -------")
        print(f"Updating {len(namespace_list)} Job/s listed below:")
        for namespace in namespace_list:
            ingress = kube.get_ingress(namespace)
            for i in ingress:
                kube.patch_ingress_whitelist(i, namespace, netskope_ips, debug=True)
    else:
        print("------- REAL RUN -------")
        print(f"Updating {len(namespace_list)} Job/s listed below:")
        for namespace in namespace_list:
            ingress = kube.get_ingress(namespace)
            for i in ingress:
                kube.patch_ingress_whitelist(i, namespace, netskope_ips, debug=False)
        
    utils.exec_cmd('say -v Samantha "Image update successfully completed."')
    print("------- ALL UPDATES DONE -------")


if __name__ == "__main__":
    main()
