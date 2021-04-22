import argparse
import sys
from pathlib import Path
from archive_links import archive_text

def parse_args():
    parser = argparse.ArgumentParser(description="Convert all URLs in a text document to archive.org links")
    parser.add_argument('input', type=str, help="Input file location, any utf-encoded file!", default=None)
    parser.add_argument('--output', type=str, help="Output file. If absent, goes to stdout",required=False)
    parser.add_argument('--timeout', type=float, help="How long to wait to test for responsive pages in s (default 1)", required=False, default=1)
    parser.add_argument('--force_archive', action="store_true", help="Force a rearchive, even if one already exists on archive.org")
    parser.add_argument('--verbose', action="store_true",
                        help="Print everything!")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    input_file = Path(args.input).absolute()
    if not input_file.exists():
        print(f'{input_file} does not exist!')
        sys.exit(1)

    with open(input_file, 'r') as ifile:
        text = ifile.read()

    out_text = archive_text(text, force_archive=args.force_archive,verbose=args.verbose, timeout=args.timeout)

    if args.output is not None:
        output_file = Path(args.output)
        print(f'Writing text to {output_file}')
        with open(Path(output_file), 'w') as ofile:
            ofile.write(text)
    else:
        sys.stdout.write(out_text)