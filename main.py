from common import utils, kube
import click


@click.Group
def cli():
    pass

@cli.command()
@click.argument('image', type=str)
@click.option('--name', '-n', help='single namespace to update.')
@click.option('--name-from-file', '-f', type=click.Path(exists=True), help='list of namespace from a file.')
@click.option('--name-from-list', '-l', type=click.Choice(kube.get_all_ns_keys()), help='builtin list of patest namespaces.')
@click.option('--debug', '-d', is_flag=True, help='Turn on debug mode')
@click.option('--boot', '-b', is_flag=True, help='Wait for pods to boot')
def update_image(image, name, name_from_file, name_from_list, debug, boot):
    name_args = [name, name_from_file, name_from_list]
    num_provided = sum(1 for arg in name_args if arg is not None)

    if num_provided != 1:
        raise click.UsageError(f"Exactly one of the option below must be provided. \
                               \n -n (namespace), \
                               \n -f (list of namespace from a txt file), \
                               \n -l (built-in list of patest namespace: {kube.get_all_ns_keys()})")
    
    if name:
        namespace_list = [name]
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


if __name__ == '__main__':
    cli()
