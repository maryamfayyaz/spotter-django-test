import csv
import asyncio
import aiohttp
import aiofiles
from aiolimiter import AsyncLimiter
from io import StringIO
from decouple import config

FUEL_PATH = config('FUEL_PATH')
ORS_API_KEY = config('ORS_API_KEY')

OUTPUT_CSV = FUEL_PATH
INPUT_CSV = "fuel-prices-for-be-assessment.csv"
ORS_URL = "https://api.openrouteservice.org/geocode/search"

limiter = AsyncLimiter(max_rate=40, time_period=60)

async def geocode_address(session, address):
    params = {"api_key": ORS_API_KEY, "text": address, "size": 1}
    headers = {"Accept": "application/json"}

    async with limiter:
        try:
            async with session.get(ORS_URL, params=params, headers=headers, timeout=15, ssl=False) as response:
                if response.status != 200:
                    return None, None, f"HTTP {response.status}"
                data = await response.json()
                features = data.get("features", [])
                if features:
                    coords = features[0]["geometry"]["coordinates"]
                    return coords[1], coords[0], None
                return None, None, "No results"
        except Exception as e:
            return None, None, str(e)


async def main():
    with open(INPUT_CSV, mode="r") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames + ["lat", "lon"]

    async with aiofiles.open(OUTPUT_CSV, mode="w") as outfile:
        writer_stream = StringIO()
        writer = csv.DictWriter(writer_stream, fieldnames=fieldnames)
        writer.writeheader()
        await outfile.write(writer_stream.getvalue())

    async with aiohttp.ClientSession() as session:
        for row in rows:
            address = f"{row['Address']}, {row['City']}, {row['State']}, USA"
            lat, lon, error = await geocode_address(session, address)
            row["lat"] = lat if lat else ""
            row["lon"] = lon if lon else ""

            if error:
                print(f"Failed: {row['Truckstop Name']} — {error}")
            else:
                print(f"Geocoded: {row['Truckstop Name']}")

            async with aiofiles.open(OUTPUT_CSV, mode="a") as outfile:
                writer_stream = StringIO()
                writer = csv.DictWriter(writer_stream, fieldnames=fieldnames)
                writer.writerow(row)
                await outfile.write(writer_stream.getvalue())


if __name__ == "__main__":
    asyncio.run(main())
