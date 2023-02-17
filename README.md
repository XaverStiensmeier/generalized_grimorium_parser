# generalized_grimorium_parser
Parses Grimorium spell entries. Currently only working for "Zaubersprüche".

## CLI

- `-f` `--pdf_file` contains the pdf
- `-p` `--pages` takes a list of pages
- `-s` `--specific-parser` takes a string that specifies the specific parser. Currently only `darkaid` is implemented.
- Example `./spell_parser.py -f 'grimorium.pdf' -p 62 63 64`

### Dark Aid
If you use `--specific-parser darkaid` the output will be in json and Dark Aid compatible. The output consists of two parts. The first part is the reference only (that needs to be added to grimorium if the spell already exists in another rulebook) and the actual spell. That spell needs to be added to grimorium if the spell doesn't exist in another rulebook or overwrite the existing spell in another rulebook with it. Make sure to keep the old page number though (remember it and then change after overwriting).

The reversalis is currently not perfectly captured. Remove any fluff text that is included. Also, check for dashes that were used for linebreaks. I have an option to remove them, but then they might be even removed when they should stay so I don't make use of it currently. Likely wrong placed dashes can be found quickly as there will be a space after them.