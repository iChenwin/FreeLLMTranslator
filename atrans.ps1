$currDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
python "$currDir\translator.py" $args
