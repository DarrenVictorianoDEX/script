import click
from common import utils, kube

rt = ["rt"]
hr = ["hr"]
clinic = ["clinic"]


@click.Group
def vnv():
    pass


@vnv.command()
@click.option('-i', '--image', 'image_to_use', help='Image to use.')
@click.option('-n', '--name', 'from_name', help='The person to greet.')
@click.option('-f', '--file', 'from_file', help='read from file.')
def hello(image_to_use, from_name=None, from_file=None):
    """Simple program that greets NAME for a total of COUNT times."""
    if from_name is None and from_file is None:
        click.echo("need either namespace or file")
    else:
        click.echo(f"Hello {image_to_use}!")
        click.echo(f"name: {from_name} | file: {from_file}")


@vnv.command()
@click.argument('image', type=str)
@click.option('--name', '-n', help='Specify name directly.')
@click.option('--name-from-file', '-f', type=click.Path(exists=True), help='Read name from a file.')
@click.option('--name-from-list', '-l', type=click.Choice(kube.get_all_ns_keys()), help='Choose name from a list.')
def process_image(image, name, name_from_file, name_from_list):
    name_args = [name, name_from_file, name_from_list]
    num_provided = sum(1 for arg in name_args if arg is not None)

    if num_provided != 1:
        raise click.UsageError("Exactly one of --name, --name-from-file, or --name-from-list must be provided.")

    click.echo(f"Image: {image}")
    if name:
        click.echo(f"Name: {name}")
    elif name_from_file:
        click.echo(f"Name from file: {name_from_file}")
    elif name_from_list:
        if name_from_list == 'rt':
            name_choice = rt
        elif name_from_list == 'hr':
            name_choice = hr
        elif name_from_list == 'clinic':
            name_choice = clinic
        click.echo(f"Name from list: {name_choice}")


if __name__ == '__main__':
    vnv()
