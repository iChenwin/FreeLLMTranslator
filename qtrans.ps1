# Wrapper to run the python translator script
$scriptPath = Join-Path $PSScriptRoot "translator.py"
python $scriptPath $args
