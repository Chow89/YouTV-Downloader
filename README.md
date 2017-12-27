# YouTV-Downloader

## Install
<pre>
pip install -r requirements.txt
</pre>

Insert mail, password and file path in config.json.

## Usage
<pre>
python3 downloader.py --config=/path/to/config.json
</pre>

## Configuration
<pre>
{
  "username": string,
  "password": string,
  "premium": false,
  "storage_path": string,
  "broadcasts": [
    {
      "title": "string,
      "filter": {
        "min_productionyear": integer
      }
    }
  ]
}
</pre>
