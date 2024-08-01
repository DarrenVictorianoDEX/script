from dpython.niles.niles_upload import NILESUpload
from common import utils, kube

import click
from click import confirm


@click.Group
def cli():
    pass


@cli.command()
@click.argument('image', type=str)
@click.option('--namespace', '-n', help='single namespace to update.')
@click.option('--name-from-file', '-f', type=click.Path(exists=True), help='list of namespace from a file.')
@click.option('--name-from-list', '-l', type=click.Choice(kube.get_all_ns_keys()), help='builtin list of patest namespaces.')
@click.option('--debug', '-d', is_flag=True, help='Turn on debug mode')
@click.option('--boot', '-b', is_flag=True, help='Wait for pods to boot')
def update_image(image, namespace, name_from_file, name_from_list, debug, boot):
    """
    Update UDP1 job's Image. \n
    built-in list for patest namespaces used for '-l' option: \t\t
    ['test', 'rt', 'hr', 'clinic', 'discovery', 'spc', 'spc2']
    """
    click.echo(f"Your Current GCP Project is: \n{kube.get_current_context()} \n")
    if not confirm("Are you in the correct GCP project?"):
        click.echo("Update cancelled.")
        return
    
    name_args = [namespace, name_from_file, name_from_list]
    num_provided = sum(1 for arg in name_args if arg is not None)

    if num_provided != 1:
        raise click.UsageError(f"Exactly one of the option below must be provided. \
                               \n -n (namespace), \
                               \n -f (list of namespace from a txt file), \
                               \n -l (built-in list of patest namespace: {kube.get_all_ns_keys()})")
    
    if namespace:
        namespace_list = [namespace]
    elif name_from_file:
        namespace_list = utils.convert_txt_file_to_list(name_from_file)
    elif name_from_list:
        namespace_list = kube.get_ns_list(name_from_list)

    if debug:
        click.echo("------- DEBUG RUN -------")
        click.echo(f"Updating {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            click.echo(f'\t- {i}')
        click.echo(f"Image to update to: {image} \n")
        kube.update_image_for_namespace_list(image=image, NS_list=namespace_list, debug=True, boot=boot)
    else:
        click.echo("------- REAL RUN -------")
        click.echo(f"Updating {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            click.echo(f'- {i}')
        click.echo(f"Image to update to: {image} \n")
        kube.update_image_for_namespace_list(image=image, NS_list=namespace_list, debug=False, boot=boot)

    # utils.exec_cmd('say -v Samantha "Image update successfully completed."')
    click.echo("------- ALL UPDATES DONE -------")


@cli.command()
@click.argument('branch', type=str)
def generate_bin(branch):
    """
    Generate Receiver Payload. (BIN file)
    """
    NILESUpload.DEBUG = True
    obj = NILESUpload(
        # optional url="your niles api url",
        client_id="180dba1c-34e7-d124-6ae1-8f77437f5132",
        client_secret="fe3a3375-8606-7be5-4cc4-2468dcfe0376"
    )

    """
    In order to instantiate the niles class,
    1. a client id to niles api
    2. a client secret to niles api
    3. [Optional] url to change the endpoint base url

    If you want to cache your client_id and client_secret to make an empty parameter 'NILESUploader()' instantiation
    uncomment and call the static setup_env method once
    """
    # NILESUploader.setup_env()
    """
    If you already have your own bin file to upload, you dont need to run the
    request_to_receiver_api method
    """

    response = NILESUpload.request_to_receiver_api(
        url="http://10.9.107.16:443/api/v1",
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


@cli.command()
@click.option('--namespace', '-n', help='single namespace to update.')
@click.option('--name-from-file', '-f', type=click.Path(exists=True), help='list of namespace from a file.')
@click.option('--name-from-list', '-l', type=click.Choice(kube.get_all_ns_keys()), help='builtin list of patest namespaces.')
@click.option('--debug', '-d', is_flag=True, help='Turn on debug mode')
def reboot_jobs(namespace, name_from_file, name_from_list, debug):
    """
    Reboot UDP1 jobs. \n
    built-in list for patest namespaces used for '-l' option: \t\t
    ['test', 'rt', 'hr', 'clinic', 'discovery', 'spc', 'spc2']
    """
    click.echo(f"Your Current GCP Project is: \n{kube.get_current_context()} \n")
    if not confirm("Are you in the correct GCP project?"):
        click.echo("Reboot cancelled.")
        return
    
    name_args = [namespace, name_from_file, name_from_list]
    num_provided = sum(1 for arg in name_args if arg is not None)

    if num_provided != 1:
        raise click.UsageError(f"Exactly one of the option below must be provided. \
                               \n -n (namespace), \
                               \n -f (list of namespace from a txt file), \
                               \n -l (built-in list of patest namespace: {kube.get_all_ns_keys()})")
    
    if namespace:
        namespace_list = [namespace]
    elif name_from_file:
        namespace_list = utils.convert_txt_file_to_list(name_from_file)
    elif name_from_list:
        namespace_list = kube.get_ns_list(name_from_list)

    if debug:
        click.echo("------- DEBUG RUN -------")
        click.echo(f"Rebooting {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            click.echo(f'\t- {i}')
        kube.reboot_namespace_list(NS_list=namespace_list, debug=True)
    else:
        click.echo("------- REAL RUN -------")
        click.echo(f"Rebooting {len(namespace_list)} Job/s listed below:")
        for i in namespace_list:
            click.echo(f'- {i}')
        kube.reboot_namespace_list(NS_list=namespace_list, debug=False)
    
    click.echo("------- ALL REBOOT DONE -------")


@cli.command()
@click.option('--namespace', '-n', help='single namespace to update.')
@click.option('--name-from-file', '-f', type=click.Path(exists=True), help='list of namespace from a file.')
@click.option('--name-from-list', '-l', type=click.Choice(kube.get_all_ns_keys()), help='builtin list of patest namespaces.')
@click.option('--debug', '-d', is_flag=True, help='Turn on debug mode')
def patch_netskope(namespace, name_from_file, name_from_list, debug):
    """
    Whitelist netskope IPs for the given namespace/s. \n
    built-in list for patest namespaces used for '-l' option: \t\t
    ['test', 'rt', 'hr', 'clinic', 'discovery', 'spc', 'spc2']
    """

    netskope_ips="66.85.67.20/32,104.154.31.59/30,34.123.228.176/32,34.72.71.80/32,24.206.101.62/31,24.206.102.57/32,24.206.102.58/32,24.206.107.62/31,24.206.110.66/31,24.206.112.87/32,24.206.112.88/32,24.206.114.60/31,24.206.115.66/31,24.206.67.20/31,24.206.73.90/31,24.206.77.78/31,24.206.79.26/32,24.206.79.25/32,24.206.80.86/31,24.206.98.66/31,24.206.99.62/31,24.239.129.58/32,24.239.129.57/32,24.239.137.74/31,24.239.144.57/32,24.239.144.58/32,24.239.145.56/31,24.239.160.59/32,24.239.160.60/32,24.239.163.58/31,24.239.165.148/31,24.239.166.59/32,24.239.166.60/32,24.206.106.62/31,24.206.111.54/31,24.206.120.20/31,24.206.84.100/32,24.206.84.99/32,24.239.139.56/31,24.239.162.60/31,24.206.100.64/31,24.206.108.64/31,24.206.109.79/32,24.206.109.80/32,24.206.103.63/32,24.206.103.64/32,24.206.104.66/31,24.206.105.56/31,24.206.65.56/31,24.206.66.80/31,24.206.68.80/31,24.206.70.152/31,24.206.72.78/31,24.206.69.18/31,24.206.71.80/31,24.206.74.56/31,24.206.75.56/31,24.206.78.84/31,24.206.82.91/32,24.206.82.92/32,24.206.88.20/31,24.206.89.20/31,24.239.128.84/31,24.206.76.128/31,24.206.97.78/31,24.239.130.68/31,24.239.131.60/31,24.239.132.66/31,24.239.133.74/31,24.239.136.58/31,24.239.138.74/31,24.239.141.69/32,24.239.141.70/32,24.239.161.56/31,24.239.164.54/31,24.239.134.60/31,24.239.135.54/31,24.239.140.63/32,24.239.140.64/32,24.239.167.56/31"

    click.echo(f"Your Current GCP Project is: \n{kube.get_current_context()} \n")
    if not confirm("Are you in the correct GCP project?"):
        click.echo("Update cancelled.")
        return
    
    name_args = [namespace, name_from_file, name_from_list]
    num_provided = sum(1 for arg in name_args if arg is not None)

    if num_provided != 1:
        raise click.UsageError(f"Exactly one of the option below must be provided. \
                               \n -n (namespace), \
                               \n -f (list of namespace from a txt file), \
                               \n -l (built-in list of patest namespace: {kube.get_all_ns_keys()})")
    
    if namespace:
        namespace_list = [namespace]
    elif name_from_file:
        namespace_list = utils.convert_txt_file_to_list(name_from_file)
    elif name_from_list:
        namespace_list = kube.get_ns_list(name_from_list)

    if debug:
        click.echo("------- DEBUG RUN -------")
        click.echo(f"Updating {len(namespace_list)} Job/s listed below:")
        for namespace in namespace_list:
            ingress = kube.get_ingress(namespace)
            for i in ingress:
                kube.patch_ingress_whitelist(i, namespace, netskope_ips, debug=True)
    else:
        click.echo("------- REAL RUN -------")
        click.echo(f"Updating {len(namespace_list)} Job/s listed below:")
        for namespace in namespace_list:
            ingress = kube.get_ingress(namespace)
            for i in ingress:
                kube.patch_ingress_whitelist(i, namespace, netskope_ips, debug=False)
        
    click.echo("------- ALL UPDATES DONE -------")


if __name__ == '__main__':
    cli()
