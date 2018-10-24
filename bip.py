#!/usr/bin/env python3

import click
import os
import re


textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))


@click.group()
def bip():
    pass


@bip.command(help='Inject binary into a picture')
@click.option('-i', '--input', required=True, help="Host file, picture", type=click.Path(exists=True))
@click.option('-n', '--injection', required=True, help="Injection file, binary", type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help="Choose the output filename", type=click.Path(exists=False))
@click.option('--override-binary', help="Overrides binary check on -b and -p", default=False, is_flag=True, type=bool)
def inject(injection, input, output, override_binary):

    # Check if user supplied an output file extension and add it.
    if os.path.splitext(output)[1] == "":
        output = output + os.path.splitext(input)[1]

    # Open input and injection files and save contents to a variable
    with open(injection, 'rb') as injection_file:
        injection_bytes = injection_file.read()
    with  open(input, 'rb') as input_file:
        input_bytes = input_file.read()

    # Check if input and injection variables are binary, and exit if not
    if not is_binary_string(injection_bytes) and not override_binary:
        click.echo("The injection file is not binary. Use the --override-binary flag to ignore this.")
        exit()
    if not is_binary_string(input_bytes) and not override_binary:
        click.echo("The input file is not binary. Use the --override-binary flag to ignore this.")
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
    header = "<bip>begin injection<filetype>{}</filetype></bip>".format(os.path.splitext(injection)[1])
    output_bytes = input_bytes + str.encode(header) + injection_bytes

    # Save bytes to file
    with open(output, 'wb') as output_file:
        output_file.seek(0)
        output_file.write(output_bytes)
        output_file.truncate()
        click.echo("Injection successful, saved to {}".format(output))


@bip.command(help='Save injected binary from a picture')
@click.option("-i", "--input", required=True, help="File with injected binary", type=click.Path(exists=True))
@click.option("-o", "--output", required=True, help="Output name", type=click.Path(exists=False))
def eject(input, output):
    # Check if user supplied an output file extension and remove it.
    if os.path.splitext(output)[1] != "":
        output = os.path.splitext(output)[0]

    # Open input file
    with open(input, "rb") as input_file:
        input_file = input_file.read()
        # Search for BIP header
        bip_re = re.search(b"<bip>(.*)</bip>", input_file)
        if bip_re:
            # Get injected filetype from header
            filetype_re = re.search(b"<filetype>(\..*)</filetype>", bip_re.group(1))
            if filetype_re:
                filetype = filetype_re.group(1).decode()
        else:
            click.echo("No BIP injection found, exiting...")
            exit()
        # Get injected bytes after the BIP header
        injection_bytes = re.search(b"<bip>.*</bip>([\s\S]*)", input_file).group(1)
        # Save injected bytes to file
        with open(output + filetype, "wb") as output_file:
            output_file.seek(0)
            output_file.write(injection_bytes)
            output_file.truncate()
            click.echo("Ejection successful, saved to {}".format(output + filetype))


@bip.command(help="Remove any binary from file")
@click.option("-i", "--input", required=True, help="File with injected binary", type=click.Path(exists=True))
@click.option("-o", "--output", required=False, help="Output name, if omitted, defaults to input", type=click.Path(exists=False))
def cleanse(input, output):

    # If output omitted, use input file
    if not output:
        output = input
        click.echo("Output option omitted, defaulting to input")

    # Check if output file exists and ask about overwrite
    if os.path.isfile(output):
        if not click.confirm('Output file exists, would you like to overwrite it?'):
            exit()
        else:
            # Check if output file is writable
            if not os.access(output, os.W_OK):
                click.echo("Write permission denied on {}, exiting.".format(output))
                exit()

    # Check if user supplied an output file extension and remove it.
    if os.path.splitext(output)[1] != "":
        output = os.path.splitext(output)[0]

    # Open input file
    with open(input, "rb") as input_file:
        input_file = input_file.read()
        # Search for BIP header
        bip_re = re.search(b"<bip>(.*)</bip>", input_file)
        if not bip_re:
            click.echo("No BIP injection found, exiting...")
            exit()
        # Get injected bytes after the BIP header
        injection_bytes = re.search(b"([\s\S]*)<bip>.*</bip>", input_file).group(1)
        # Save injected bytes to file
        with open(output + os.path.splitext(input)[1], "wb") as output_file:
            output_file.seek(0)
            output_file.write(injection_bytes)
            output_file.truncate()
            click.echo("Cleansing successful, saved to {}".format(output + os.path.splitext(input)[1]))


if __name__ == "__main__":
    bip()