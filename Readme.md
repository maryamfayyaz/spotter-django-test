# Spotter Django Test

## Install Dependencies
pip install -r requirements.txt
## To Run
python manage.py runserver


## API
curl --location 'http://localhost:8000/api/route-fuel/' \
--header 'Content-Type: application/json' \
--header 'Cookie: refreshToken=_AoZf3RPW4ppdNUYdosMugjNLEyobVb3Q0L33q0pxHfGA' \
--data '{
    "start": [
        41.878113,
        -87.629799
    ],
    "end": [
        39.739236,
        -104.990251
    ]
}'