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


if __name__ == '__main__':
    cli()
