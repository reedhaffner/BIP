#!/usr/bin/env python3

import click
import os


textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))


@click.group()
def bip():
    pass


@bip.command(help='Inject binary into a picture')
@click.option('-b', '--binary', required=True, help="Binary to be injected", type=click.Path(exists=True))
@click.option('-p', '--picture', required=True, help="Picture host file", type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help="Choose the output filename", type=click.Path(exists=False))
@click.option('--override-binary', help="Overrides binary check on -b and -p", default=False, is_flag=True, type=bool)
def inject(binary, picture, output, override_binary):

    # Open binary and picture files and save contents to a variable
    with open(binary, 'rb') as binary_file:
        binary_bytes = binary_file.read()
    with  open(picture, 'rb') as picture_file:
        picture_bytes = picture_file.read()

    # Check if binary and picture variables are binary, and exit if not
    if not is_binary_string(binary_bytes) and not override_binary:
        click.echo("The binary file is not binary. Use the --override-binary flag to ignore this.")
        exit()
    if not is_binary_string(picture_bytes) and not override_binary:
        click.echo("The picture file is not binary. Use the --override-binary flag to ignore this.")
        exit()


    # Check if output file exists and ask about overwrite
    if os.path.isfile(output):
        if not click.confirm('Output file exists, would you like to overwrite it?'):
            exit()
        else:
            # Check if output file is writable
            if not os.access(output, os.W_OK):
                click.echo("Write permission denied on {}, exiting.".format(output))
                exit()

    # Create BIP header and create the output bytes
    header = "<bip>begin injection<filetype>{}</filetype></bip>".format(os.path.splitext(binary)[1])
    output_bytes = picture_bytes + str.encode(header) + binary_bytes

    # Save bytes to file
    with open(output, 'wb') as output_file:
        output_file.seek(0)
        output_file.write(output_bytes)
        output_file.truncate()



@bip.command(help='Save injected binary from a picture')
def eject():
    click.echo("eject")


@bip.command(help="Remove any binary from picture")
def cleanse():
    click.echo("cleanse")


if __name__ == "__main__":
    bip()